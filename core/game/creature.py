from twisted.internet import defer
from game.engine import getSpectators, getPlayers
from game.map import placeCreature, removeCreature, getTile
from twisted.python import log
import threading
import game.enum as enum
import config
import time
import copy
import game.scriptsystem
import inspect
import game.errors
import math

# Unique ids, thread safe too
def __uid():
    idsTaken = 1000
    while True:
        idsTaken += 1
        yield idsTaken
        
__uniqueId = __uid().next
__uniqueLock = threading.Lock()
def uniqueId():
    __uniqueLock.acquire()
    id = __uniqueId()
    __uniqueLock.release()
    return id

allCreatures = {}
allCreaturesObject = allCreatures.viewvalues()

class CreatureBase(object):
    def __init__(self):
        self.scripts = {"onFollow":[], "onTargetLost":[]}
        
    def regOnFollow(self, function):
        self.scripts["onFollow"].append(function)
        
    def unregOnFollow(self, function):
        self.scripts["onFollow"].remove(function)
        
    def onFollow(self, target):
        for func in self.scripts["onFollow"]:
            game.scriptsystem.scriptPool.callInThread(func, self, target)

    def regOnTargetLost(self, function):
        self.scripts["onTargetLost"].append(function)

    def unregOnTargetLost(self, function):
        self.scripts["onTargetLost"].remove(function)
        
    def onTargetLost(self, target):
        for func in self.scripts["onTargetLost"]:
            game.scriptsystem.scriptPool.callInThread(func, self, target)
            
class Creature(object):
    
    def __init__(self, data, position, cid=None):
        self.data = data
        self.creatureType = 0
        self.direction = 0
        self.position = position
        self.speed = 100.0
        self.scripts = { "onNextStep":[]}
        self.cid = cid if cid else self.generateClientID()
        self.outfit = [self.data["looktype"], self.data["lookhead"], self.data["lookbody"], self.data["looklegs"], self.data["lookfeet"]]
        self.mount = 0
        self.mounted = 0
        self.addon = self.data["lookaddons"]
        self.action = None
        self.lastAction = 0
        self.lastStep = 0
        self.target = None # target for follow/attacks
        self.targetMode = 0 # 0 = no particular reason, 1 = attack, 2 = follow
        self.vars = {}
        self.cooldowns = {} # This is a int32, icon are the first 8, then group is the next 7
        self.regenerate = None
        self.alive = True
        self.lastDamager = None
        self.solid = not config.creatureWalkthrough
        
        # We are trackable
        allCreatures[self.cid] = self

    def actionLock(self, *args):
        if self.lastAction >= time.time():
            game.engine.safeCallLater(0.1, *args)
            return False
        else:
            self.lastAction = time.time()
            return True

    def isPlayer(self):
        return False

    def isNPC(self):
        return False
        
    def isMonster(self):
        return False
        
    def name(self):
        return self.data["name"]

    def description(self):
        return "You see a creature."
        
    def clientId(self):
        return self.cid

    def thingId(self):
        return self.creatureType # Used to indentify my "thing"
    
    def actionIds(self):
        return ('99',) # Static actionID
        
    def generateClientID(self):
        raise NotImplementedError("This function must be overrided by a secondary level class!")
        
    def stepDuration(self, ground, delay=1.5):
        #if time.time() - self.lastStep < delay:
        if True: # Ignore delay system
            if not ground.speed:
                ground.speed = 100
                
            postValue = (config.drawingSpeed - 50) / 1000.0
            return (ground.speed / self.speed) + postValue
        #return delay

    def notPossible(self):
        # Needs to be overrided in player
        # Here we can inform a script if a illigal event
        # Right now, don't care
        return

    def refreshStatus(self, streamX=None): pass
    def refreshSkills(self, streamX=None): pass
    
    def move(self, direction, spectators=None, level=0):
        d = defer.Deferred()
        game.engine.safeCallLater(0, self.__move, d, direction, spectators, level)
        return d
        
    @defer.deferredGenerator
    def __move(self, d, direction, spectators=None, level=0):
        if not level and not self.actionLock(self.__move, d, direction, spectators, level):
            return
        import data.map.info
        
        
        oldPosition = self.position[:]
        
        # Recalculate position
        position = oldPosition[:] # Important not to remove the : here, we don't want a reference!
        if direction == 0:
            position[1] = oldPosition[1] - 1
        elif direction == 1:
            position[0] = oldPosition[0] + 1
        elif direction == 2:
            position[1] = oldPosition[1] + 1
        elif direction == 3:
            position[0] = oldPosition[0] - 1
        elif direction == 4:
            position[1] = oldPosition[1] + 1
            position[0] = oldPosition[0] - 1
        elif direction == 5:
            position[1] = oldPosition[1] + 1
            position[0] = oldPosition[0] + 1
        elif direction == 6:
            position[1] = oldPosition[1] - 1
            position[0] = oldPosition[0] - 1
        elif direction == 7:
            position[1] = oldPosition[1] - 1
            position[0] = oldPosition[0] + 1

        position[2] = oldPosition[2] + level

        # We don't walk out of the map!
        if position[0] < 1 or position[1] < 1 or position[0] > data.map.info.width or position[1] > data.map.info.height:
            self.cancelWalk()
            return
                    
        # New Tile
        newTile = getTile(position)
        oldTile = getTile(oldPosition)

        try:
            oldStackpos = oldTile.findCreatureStackpos(self)
        except:
            """self.teleport(position)
            self.lastStep = time.time()
            if callback:
                callback(self, oldPosition, position)
            
            self.lastAction += self.stepDuration(newTile.getThing(0)) * (3 if direction > 3 else 1)"""
            self.cancelWalk()
            return
        
        for thing in newTile.things:
            if thing.solid:
                self.turn(direction) # Fix me?
                self.notPossible()
                d.errback(game.errors.ImpossibleMove)  # Prevent walking on solid tiles
                return
            
            
        """t = time.time()
        if not level and self.lastStep+self.stepDuration(newTile.getThing(0)) > t:
            game.engine.safeCallLater(t-self.lastStep+self.stepDuration(newTile.getThing(0)), self.move, direction)
            return False
            
        else:
            self.lastStep = time.time()"""

        self.lastStep = time.time()
        self.lastAction += self.stepDuration(newTile.getThing(0)) * (config.diagonalWalkCost if direction > config.diagonalWalkCost else 1)
                
        
            
        # Deal with walkOff
        for item in oldTile.getItems():
            yield defer.waitForDeferred(game.scriptsystem.get('walkOff').runDefer(item, self, None, position=oldPosition))

        # Deal with preWalkOn
        for item in newTile.getItems():
            yield defer.waitForDeferred(game.scriptsystem.get('preWalkOn').runDefer(item, self, None, oldTile=oldTile, newTile=newTile, position=position))
            
            
        newStackPos = newTile.placeCreature(self)

        if not newStackPos or newStackPos > 9:
            self.cancelWalk()
            d.errback(game.errors.ImpossibleMove)
            return
            
        oldTile.removeCreature(self)
        
            
        
        self.position = position
        self.direction = direction
        
        # Send to everyone   
        if not spectators:
            spectators = getPlayers(position)
            
        for spectator in spectators:
            # Make packet
            if not spectator.client:
                continue

            canSeeNew = spectator.canSee(position)
            canSeeOld = spectator.canSee(oldPosition)

            if spectator == self:
                if oldPosition[2] != 7 or position[2] < 8: # Only as long as it's not 7->8 or 8->7
                    stream = spectator.packet(0x6D)
                    stream.position(oldPosition)
                    stream.uint8(oldStackpos)
                    stream.position(position)   
                else:
                    stream = spectator.packet()
                    stream.removeTileItem(oldPosition, oldStackpos)
                # Levels
                if oldPosition[2] > position[2]:
                    stream.moveUpPlayer(self, oldPosition)
                        
                elif oldPosition[2] < position[2]:
                    stream.moveDownPlayer(self, oldPosition)
                
                # Y movements
                if oldPosition[1] > position[1]:
                    stream.uint8(0x65)
                    stream.mapDescription((oldPosition[0] - 8, self.position[1] - 6, self.position[2]), 18, 1, self)
                elif oldPosition[1] < position[1]:
                    stream.uint8(0x67)
                    stream.mapDescription((oldPosition[0] - 8, self.position[1] + 7, self.position[2]), 18, 1, self)
                
                # X movements
                if oldPosition[0] < position[0]:
                    stream.uint8(0x66)
                    stream.mapDescription((self.position[0] + 9, self.position[1] - 6, self.position[2]), 1, 14, self)
                elif oldPosition[0] > position[0]:
                    stream.uint8(0x68)
                    stream.mapDescription((self.position[0] - 8, self.position[1] - 6, self.position[2]), 1, 14, self)

                    
                    
            elif not canSeeOld and canSeeNew:
                stream = spectator.packet()
                stream.addTileCreature(position, newStackPos, self, spectator) # This automaticly deals with known list so
                    
            elif canSeeOld and not canSeeNew:
                stream = spectator.packet()
                stream.removeTileItem(oldPosition, oldStackpos)
                
            elif not canSeeOld and not canSeeNew:
                continue
            else:
                if oldPosition[2] != 7 or position[2] < 8: # Only as long as it's not 7->8 or 8->7
                    stream = spectator.packet(0x6D)
                    stream.position(oldPosition)
                    stream.uint8(oldStackpos)
                    stream.position(position)   
                else:
                    stream = spectator.packet()
                    stream.removeTileItem(oldPosition, oldStackpos)
                    
            stream.send(spectator.client) 

        if self.scripts["onNextStep"]:
            for script in self.scripts["onNextStep"][:]:
                script(self)
                self.scripts["onNextStep"].remove(script)
                     
        # Deal with walkOn
        for item in newTile.getItems(): # Scripts
            game.scriptsystem.get('walkOn').run(item, self, None, position=position)
            if item.teledest:
                try:
                    self.teleport(item.teledest)
                except:
                    log.msg("%d (%s) got a invalid teledist (%s), remove it!" % (item.itemId, str(item), str(item.teledest)))
                    del item.teledest

        if d.callback:
            d.callback((self, oldPosition, position))

    def magicEffect(self, pos, type):
        for spectator in getSpectators(pos):
            stream = spectator.packet()
            stream.magicEffect(pos, type)
            stream.send(spectator)
        
    def shoot(self, fromPos, toPos, type):
        for spectator in getSpectators(pos):
            stream = spectator.packet()
            stream.shoot(fromPos, toPos, type)
            stream.send(spectator)

    def refreshOutfit(self):
        for spectator in game.engine.getSpectators(self.position):
            stream = spectator.packet(0x8E)
            stream.uint32(self.clientId())
            stream.outfit(self.outfit, self.addon, self.mount if self.mounted else 0x00)
            stream.send(spectator)

    def changeMountStatus(self, mounted):
        mount = game.resource.getMount(self.mount)
        if mount:
            self.mounted = mounted
        
            if mount.speed:
                self.setSpeed((self.speed + mount.speed) if mounted else (self.speed - mount.speed))
            self.refreshOutfit()
    
    def setOutfit(self, looktype, lookhead=0, lookbody=0, looklegs=0, lookfeet=0, addon=0):
        self.outfit = [looktype, lookhead, lookbody, looklegs, lookfeet]
        self.addon = addon
        self.refreshOutfit()

    def setSpeed(self, speed):
        if speed != self.speed:
            if speed > 1500:
                speed = 1500.0
            self.speed = float(speed)
            for spectator in getSpectators(self.position):
                stream = spectator.packet(0x8F)
                stream.uint32(self.clientId())
                stream.uint16(self.speed)
                stream.send(spectator)
            
    def onDeath(self):
        #del allCreatures[self.clientId()]
        pass # To be overrided in monster and player

    def hitEffects(self):
        if self.isPlayer() or self.base.blood == game.enum.FLUID_BLOOD:
            return game.enum.COLOR_RED, game.enum.EFFECT_DRAWBLOOD
        elif self.base.blood == game.enum.FLUID_SLIME:
            return game.enum.COLOR_LIGHTGREEN, game.enum.EFFECT_POISON
        elif self.base.blood == game.enum.FLUID_ENERGY:
            return game.enum.COLOR_PURPLE, game.enum.EFFECT_PURPLEENERGY
        elif self.base.blood == game.enum.FLUID_UNDEAD:
            return game.enum.COLOR_GREY, game.enum.EFFECT_HITAREA
        elif self.base.blood == game.enum.FLUID_FIRE:
            return game.enum.COLOR_ORANGE, game.enum.EFFECT_DRAWBLOOD
        
    def damageToBlock(self, dmg, type):
        return dmg
        
    def onHit(self, by, dmg, type):
        self.lastDamager = by

        if by.isPlayer():
            if by.modes[1] == game.enum.BALANCED:
                dmg = dmg / 0.75
            elif by.modes[1] == game.enum.DEFENSIVE:
                dmg = dmg / 0.5
                
        dmg = min(self.damageToBlock(dmg, type), 0) # Armor calculations

        dmg = max(self.data["health"] * -1, dmg)



        if type == game.enum.MELEE:
            textColor, magicEffect = self.hitEffects()
        
        elif type == game.enum.ICE:
            textColor = game.enum.COLOR_TEAL
            magicEffect = game.enum.EFFECT_ICEATTACK
            
        elif type == game.enum.FIRE:
            textColor = game.enum.COLOR_ORANGE
            magicEffect = game.enum.EFFECT_HITBYFIRE

        elif type == game.enum.EARTH:
            textColor = game.enum.COLOR_LIGHTGREEN
            magicEffect = game.enum.EFFECT_HITBYPOSION
           
        elif type == game.enum.ENERGY:
            textColor = game.enum.COLOR_PURPLE
            magicEffect = game.enum.EFFECT_ENERGY_DAMAGE
            
        elif type == game.enum.HOLY:
            textColor = game.enum.COLOR_YELLOW
            magicEffect = game.enum.EFFECT_HOLYDAMAGE
            
        elif type == game.enum.DEATH:
            textColor = game.enum.COLOR_DARKRED
            magicEffect = game.enum.EFFECT_SMALLCLOUDS
            
        elif type == game.enum.DROWN:
            textColor = game.enum.COLOR_LIGHTBLUE
            magicEffect = game.enum.EFFECT_ICEATTACK
            
        self.magicEffect(self.position, magicEffect) 
        
        tile = game.map.getTile(self.position)
        addSplash = True
        for item in tile.getItems():
            if item.itemId == game.enum.SMALLSPLASH:
                item.decay(self.position) # Reset decay
                addSplash = False
                        
        if addSplash:
            splash = game.item.Item(game.enum.SMALLSPLASH)
            
            if self.isPlayer():
                splash.fluidSource = game.enum.FLUID_BLOOD
            else:
                splash.fluidSource = self.base.blood
            if splash.fluidSource in (game.enum.FLUID_BLOOD, game.enum.FLUID_SLIME):
                game.engine.placeItem(splash, self.position)
            
            
        if by and by.isPlayer():
            by.message("%s loses %d hitpoint%s due to your attack." % (self.name().capitalize(), -1 * dmg, 's' if dmg < -1 else ''), game.enum.MSG_DAMAGE_DEALT, value = -1 * dmg, color = textColor, pos=self.position)

        if self.isPlayer():
            if by:
                self.message("You lose %d hitpoint%s due to an attack by %s." % (-1 * dmg, 's' if dmg < -1 else '', by.name().capitalize()), game.enum.MSG_DAMAGE_RECEIVED)
            else:
                self.message("You lose %d hitpoint%s." % (-1 * dmg, 's' if dmg < -1 else ''), game.enum.MSG_DAMAGE_RECEIVED)

        elif not self.target and self.data["health"] < 1:
            self.follow(by) # If I'm a creature, set my target
        
        # Modify health
        self.modifyHealth(dmg)
        
        
    def onSpawn(self):
        pass # To be overrided
        
    def setHealth(self, health):
        if self.data["health"] == 0 and health:
            self.alive = True
            
        self.data["health"] = max(0, health)
        
        for spectator in getSpectators(self.position):
            stream = spectator.packet(0x8C)
            stream.uint32(self.clientId())
            stream.uint8(self.data["health"] * 100 / self.data["healthmax"])
            stream.send(spectator)
         
        self.refreshStatus()
        
        if self.data["health"] == 0:
            self.alive = False
            self.onDeath()
           

    def modifyHealth(self, health, spawn=False):
        self.setHealth(min(self.data["health"] + health, self.data["healthmax"]))
    
    def setMana(self, mana):
        self.data["mana"] = mana
        self.refreshStatus()

    def modifyMana(self, mana):
        self.setMana(min(self.data["mana"] + mana, self.data["manamax"]))
        
    def setSoul(self, soul):
        self.data["soul"] = soul
        self.refreshStatus()
    
    def modifySoul(self, soul):
        self.setSoul(self.data["soul"] + soul)
        
    def teleport(self, position):
        """if not self.actionLock(self.teleport, position):
            return False"""
            
        # 4 steps, remove item (creature), send new map and cords, and effects
        oldPosition = self.position[:]
        
        newTile = getTile(position)
        
        if not newTile or newTile.things[0].solid:
            raise game.errors.SolidTile()

        oldStackpos = getTile(oldPosition).findCreatureStackpos(self)
        for spectator in getSpectators(oldPosition, ignore=(self,)):
            stream = spectator.packet()
            stream.removeTileItem(oldPosition, oldStackpos)
            stream.magicEffect(oldPosition, 0x02)
            stream.send(spectator)
        
        
        stackpos = placeCreature(self, position)
        if not stackpos:
            raise game.errors.ImpossibleMove()
        
        removeCreature(self, oldPosition)
        self.position = position 
        if self.creatureType == 0:
            stream = self.packet()
            stream.removeTileItem(oldPosition, oldStackpos)
            stream.uint8(0x64)
            stream.position(position)
            stream.mapDescription((position[0] - 8, position[1] - 6, position[2]), 18, 14, self)
            #stream.magicEffect(position, 0x02)
            stream.send(self.client)
            
         
        
        for spectator in getSpectators(position, ignore=(self,)):
            stream = spectator.packet()
            stream.addTileCreature(position, stackpos, self, spectator.player)
            stream.magicEffect(position, 0x02)
            stream.send(spectator)
                

    def turn(self, direction):
        if self.direction == direction:
            return
            
        self.direction = direction
        
        # Make package
        for spectator in getSpectators(self.position):
            stream = spectator.packet(0x6B)
            stream.position(self.position)
            stream.uint8(getTile(self.position).findCreatureStackpos(self))
            stream.uint16(0x63)
            stream.uint32(self.clientId())
            stream.uint8(direction)
            stream.send(spectator)
        
    def turnAgainst(self, position):
        # First north/south
        if position[1] > self.position[1]:
            return self.turn(0)
        elif position[1] < self.position[1]:
            return self.turn(2)
        elif position[0] > self.position[0]:
            return self.turn(1)
        elif position[0] < self.position[0]:
            return self.turn(3)
            
    def say(self, message, messageType=enum.MSG_SPEAK_SAY):
        for spectator in getSpectators(self.position, config.sayRange):
            stream = spectator.packet(0xAA)
            stream.uint32(0)
            stream.string(self.data["name"])
            stream.uint16(self.data["level"] if "level" in self.data else 0)
            stream.uint8(messageType)
            stream.position(self.position)
            stream.string(message)
            stream.send(spectator)

    def yell(self, message, messageType=enum.MSG_SPEAK_YELL):
        for spectator in getSpectators(self.position, config.sayRange):
            stream = spectator.packet(0xAA)
            stream.uint32(0)
            stream.string(self.data["name"])
            stream.uint16(self.data["level"] if "level" in self.data else 0)
            stream.uint8(messageType)
            stream.position(self.position)
            stream.string(message)
            stream.send(spectator)

    def whisper(self, message, messageType=enum.MSG_SPEAK_WHISPER):
        for spectator in getSpectators(self.position, config.sayRange):
            stream = spectator.packet(0xAA)
            stream.uint32(0)
            stream.string(self.data["name"])
            stream.uint16(self.data["level"] if "level" in self.data else 0)
            stream.uint8(messageType)
            stream.position(self.position)
            stream.string(message)
            stream.send(spectator)

    def sayPrivate(self, message, to, messageType=enum.MSG_PRIVATE_FROM):
        if not to.isPlayer(): return
        
        stream = to.packet(0xAA)
        stream.uint32(0)
        stream.string(self.data["name"])
        stream.uint16(self.data["level"] if "level" in self.data else 0)
        stream.uint8(messageType)
        stream.position(self.position)
        stream.string(message)
        stream.send(to.client)    
        
    def stopAction(self):
        ret = False
        try:
            self.action.cancel()
            ret = True
        except:
            pass
        self.action = None
        return ret
        
    def cancelWalk(self, d=None):
        return # Is only executed on players
        
    def canSee(self, position, radius=(8,6)):
        if self.position[2] <= 7 and position[2] > 7: # We are on ground level and we can't see underground
            return False
                
        elif self.position[2] >= 8 and abs(self.position[2]-position[2]) > 2: # We are undergorund and we may only see 2 floors
            return False
        
        offsetz = self.position[2]-position[2]
        if (position[0] >= self.position[0] - radius[0] + offsetz) and (position[0] <= self.position[0] + radius[0]+1 + offsetz) and (position[1] >= self.position[1] - radius[1] + offsetz) and (position[1] <= self.position[1] + radius[1]+1 + offsetz):
            return True
        return False
    
    def distanceStepsTo(self, position):
        return abs(self.position[0]-position[0])+abs(self.position[1]-position[1])
        
    def inRange(self, position, x, y, z=0):
        return ( abs(self.position[0]-position[0]) <= x and abs(self.position[1]-position[1]) <= y and abs(self.position[2]-position[2]) <= y )   
    
    def positionInDirection(self, direction):
        position = self.position[:] # Important not to remove the : here, we don't want a reference!
        if direction == 0:
            position[1] = self.position[1] - 1
        elif direction == 1:
            position[0] = self.position[0] + 1
        elif direction == 2:
            position[1] = self.position[1] + 1
        elif direction == 3:
            position[0] = self.position[0] - 1
        elif direction == 4:
            position[1] = self.position[1] + 1
            position[0] = self.position[0] - 1
        elif direction == 5:
            position[1] = self.position[1] + 1
            position[0] = self.position[0] + 1
        elif direction == 6:
            position[1] = self.position[1] - 1
            position[0] = self.position[0] - 1
        elif direction == 7:
            position[1] = self.position[1] - 1
            position[0] = self.position[0] + 1
        return position

    # Personal vars
    def setVar(self, name, value=None):
        try:
            if value == None:
                del self.vars[inspect.stack()[0][1] + name]
            else:
                self.vars[inspect.stack()[0][1] + name] = value
        except:
            return None
            
    def getVar(self, name):
        try:
            return self.vars[inspect.stack()[0][1] + name]
        except:
            return None

    # Global storage
    def setGlobal(self, field, value):
        try:
            game.engine.globalStorage['storage'][field] = value
        except:
            return False
    
    def getGlobal(self, field, default=None):
        try:
            return game.engine.globalStorage['storage'][field]
        except:
            return default
            
    def removeGlobal(self, field):
        try:
            del game.engine.globalStorage['storage'][field]
        except:
            pass

    # Global object storage
    def setGlobalObject(self, field, value):
        try:
            game.engine.globalStorage['objectStorage'][field] = value
        except:
            return False
    
    def getGlobalObject(self, field, default=None):
        try:
            return game.engine.globalStorage['objectStorage'][field]
        except:
            return default
            
    def removeGlobalObject(self, field):
        try:
            del game.engine.globalStorage['objectStorage'][field]
        except:
            pass
        
    def __followCallback(self, who):
        if self.target == who:
            game.engine.autoWalkCreatureTo(self, self.target.position, -1, True)
            self.target.scripts["onNextStep"].append(self.__followCallback)
            
    def follow(self, target):
        """if self.targetMode == 2 and self.target == target:
            self.targetMode = 0
            self.target = None
            return"""

        self.target = target
        self.targetMode = 2
        game.engine.autoWalkCreatureTo(self, self.target.position, -1, True)
        self.target.scripts["onNextStep"].append(self.__followCallback)

    def playerSay(self, player, say, type, channel):
        pass # Override me
