from twisted.internet import defer
from game.engine import getSpectators
from packet import TibiaPacket
from game.map import placeCreature, removeCreature, getTile
import threading
import game.enum as enum
import config
import time
import copy
import game.scriptsystem
import inspect
import game.errors


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
        self.addon = 0
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
        self.solid = False
        
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
        
    def name(self):
        return self.data["name"]

    def clientId(self):
        return self.cid

    def thingId(self):
        return self.creatureType # Used to indentify my "thing"
    
    def actionIds(self):
        return ('99',) # Static actionID
        
    def generateClientID(self):
        raise NotImplementedError("This function must be overrided by a secondary level class!")
        
    def stepDuration(self, ground, delay=1.5):
        if time.time() - self.lastStep < delay:
            if not ground.speed:
                ground.speed = 100
            return round(ground.speed / self.speed, 3)
        return delay

    def notPossible(self):
        # Needs to be overrided in player
        # Here we can inform a script if a illigal event
        # Right now, don't care
        return

    def refreshStatus(self, streamX=None): pass
    def refreshSkills(self, streamX=None): pass
    
    def move(self, *argc, **kwargs):
        d = defer.Deferred()
        game.engine.safeCallLater(0, self.__move, d, *argc, **kwargs)
        return d
        
    @defer.deferredGenerator
    def __move(self, d, direction, spectators=None, level=0):
        self.direction = direction # Direction might change regardless
        
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
        
        for thing in newTile.getItems():
            if thing.solid:
                self.cancelWalk()
                self.notPossible()
                d.errback(game.errors.ImpossibleMove)  # Prevent walking on solid tiles
                return
            
        tileCreatures = newTile.creatures()  
            
        for tileCreature in tileCreatures:
            if tileCreature.solid: # Dont walk to creatures that is solid
                self.notPossible()
                d.errback(game.errors.ImpossibleMove)
                return
            
        """t = time.time()
        if not level and self.lastStep+self.stepDuration(newTile.getThing(0)) > t:
            game.engine.safeCallLater(t-self.lastStep+self.stepDuration(newTile.getThing(0)), self.move, direction)
            return False
            
        else:
            self.lastStep = time.time()"""

        self.lastStep = time.time()
        self.lastAction += self.stepDuration(newTile.getThing(0)) * (config.diagonalWalkCost if direction > config.diagonalWalkCost else 1)

        # Make packet
        if oldPosition[2] != 7 or position[2] < 8: # Only as long as it's not 7->8 or 8->7
            stream = TibiaPacket(0x6D)
            stream.position(oldPosition)
            stream.uint8(oldStackpos)
            stream.position(position)   
        else:
            stream = TibiaPacket()
            stream.removeTileItem(oldPosition, oldStackpos)
                
        
            
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
                
        # Send to everyone   
        if not spectators:
            spectators = getSpectators(position)

        for spectator in spectators:
            streamX = stream
            if not spectator:
                spectator = self.client
            canSeeNew = spectator.player.canSee(position)
            canSeeOld = spectator.player.canSee(oldPosition)

            if spectator.player == self:
                streamX = copy.copy(stream)

                # Levels
                if oldPosition[2] > position[2]:
                    streamX.moveUpPlayer(self, oldPosition)
                        
                elif oldPosition[2] < position[2]:
                    streamX.moveDownPlayer(self, oldPosition)
                
                # Y movements
                if oldPosition[1] > position[1]:
                    streamX.uint8(0x65)
                    streamX.mapDescription((oldPosition[0] - 8, self.position[1] - 6, self.position[2]), 18, 1, self)
                elif oldPosition[1] < position[1]:
                    streamX.uint8(0x67)
                    streamX.mapDescription((oldPosition[0] - 8, self.position[1] + 7, self.position[2]), 18, 1, self)
                
                # X movements
                if oldPosition[0] < position[0]:
                    streamX.uint8(0x66)
                    streamX.mapDescription((self.position[0] + 9, self.position[1] - 6, self.position[2]), 1, 14, self)
                elif oldPosition[0] > position[0]:
                    streamX.uint8(0x68)
                    streamX.mapDescription((self.position[0] - 8, self.position[1] - 6, self.position[2]), 1, 14, self)

                    
                    
            elif not canSeeOld and canSeeNew:
                streamX = TibiaPacket()
                streamX.addTileCreature(position, newStackPos, self, spectator.player) # This automaticly deals with known list so
                    
            elif canSeeOld and not canSeeNew:
                streamX = TibiaPacket()
                streamX.removeTileItem(oldPosition, oldStackpos)
                
            elif not canSeeOld and not canSeeNew:
                continue
            streamX.send(spectator) 

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
        stream = TibiaPacket()
        stream.magicEffect(pos, type)
        stream.sendto(getSpectators(pos))
        
    def shoot(self, fromPos, toPos, type):
        stream = TibiaPacket()
        stream.shoot(fromPos, toPos, type)
        stream.sendto(getSpectators(fromPos))

    def refreshOutfit(self):
        stream = TibiaPacket(0x8E)
        stream.uint32(self.clientId())
        stream.outfit(self.outfit, self.addon, self.mount if self.mounted else 0x00)
        stream.sendto(game.engine.getSpectators(self.position))

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
            stream = TibiaPacket(0x8F)
            stream.uint32(self.clientId())
            stream.uint16(self.speed)
            stream.sendto(getSpectators(self.position))
            
    def onDeath(self):
        #del allCreatures[self.clientId()]
        pass # To be overrided in monster and player

    def hitEffect(self):
        if self.isPlayer() or self.base.blood == game.enum.FLUID_BLOOD:
            return game.enum.EFFECT_DRAWBLOOD
        elif self.base.blood == game.enum.FLUID_SLIME:
            return game.enum.EFFECT_POISON
        elif self.base.blood == game.enum.FLUID_ENERGY:
            return game.enum.EFFECT_PURPLEENERGY
        return game.enum.EFFECT_DRAWBLOOD
        
    def damageToBlock(self, dmg, type):
        return dmg
        
    def onHit(self, by, dmg, type):
        dmg = min(self.damageToBlock(dmg, type), 0) # Armor calculations

        self.modifyHealth(dmg)
        self.magicEffect(self.position, self.hitEffect())
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
                
            game.engine.placeItem(splash, self.position)
            
            
        if by and by.isPlayer():
            by.message("%s loses %d hitpoint%s due to your attack." % (self.name().capitalize(), -1 * dmg, 's' if dmg < -1 else ''), game.enum.MSG_DAMAGE_DEALT)

        if self.isPlayer():
            if by:
                self.message("You lose %d hitpoint%s due to an attack by %s." % (-1 * dmg, 's' if dmg < -1 else '', by.name().capitalize()), game.enum.MSG_DAMAGE_RECEIVED)
            else:
                self.message("You lose %d hitpoint%s." % (-1 * dmg, 's' if dmg < -1 else ''), game.enum.MSG_DAMAGE_RECEIVED)

        elif not self.target and self.data["health"] < 1:
            self.follow(by) # If I'm a creature, set my target
            
    def onSpawn(self):
        pass # To be overrided
        
    def setHealth(self, health):
        if self.data["health"] == 0 and health:
            self.alive = True
            
        self.data["health"] = max(0, health)
        
        stream = TibiaPacket(0x8C)
        stream.uint32(self.clientId())
        stream.uint8(self.data["health"] * 100 / self.data["healthmax"])
        stream.sendto(getSpectators(self.position))
         
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
        self.position = position 
        newTile = getTile(position)
        
        if newTile.things[0].solid:
            raise game.errors.SolidTile()
        
        oldStackpos = getTile(oldPosition).findCreatureStackpos(self)
        
        stream = TibiaPacket()
        stream.removeTileItem(oldPosition, oldStackpos)
        stream.magicEffect(oldPosition, 0x02)
        stream.sendto(getSpectators(oldPosition, ignore=[self]))
        
        
        stackpos = placeCreature(self, position)
        removeCreature(self, oldPosition)
        if self.creatureType == 0:
            stream = TibiaPacket()
            stream.removeTileItem(oldPosition, oldStackpos)
            stream.uint8(0x64)
            stream.position(position)
            stream.mapDescription((position[0] - 8, position[1] - 6, position[2]), 18, 14, self)
            #stream.magicEffect(position, 0x02)
            stream.send(self.client)
            
         
        
        for spectator in getSpectators(position, ignore=[self]):
            stream = TibiaPacket()
            stream.addTileCreature(position, stackpos, self, spectator.player)
            stream.magicEffect(position, 0x02)
            stream.send(spectator)
                

    def turn(self, direction):
        if self.direction == direction:
            return
            
        self.direction = direction
        
        # Make package
        stream = TibiaPacket(0x6B)
        stream.position(self.position)
        stream.uint8(getTile(self.position).findCreatureStackpos(self))
        stream.uint16(0x63)
        stream.uint32(self.clientId())
        stream.uint8(direction)
                
        # Send to everyone
        stream.sendto(getSpectators(self.position))
        
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
        stream = TibiaPacket(0xAA)
        stream.uint32(00)
        stream.string(self.data["name"])
        stream.uint16(self.data["level"] if "level" in self.data else 0)
        stream.uint8(messageType)
        stream.position(self.position)
        stream.string(message)
        stream.sendto(getSpectators(self.position, config.sayRange))

    def yell(self, message, messageType=enum.MSG_SPEAK_YELL):
        stream = TibiaPacket(0xAA)
        stream.uint32(00)
        stream.string(self.data["name"])
        stream.uint16(self.data["level"] if "level" in self.data else 0)
        stream.uint8(messageType)
        stream.position(self.position)
        stream.string(message)
        stream.sendto(getSpectators(self.position, config.yellRange))
        
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
        
    def canSee(self, position):
        if self.position[2] <= 7: # We are on ground level
            if position[2] > 7:
                return False # We can't see underground
                
        elif self.position[2] >= 8: # We are undergorund
            if abs(self.position[2]-position[2]) > 2: # We may only see 2 floors
                return False
        
        offsetz = self.position[2]-position[2]
        if (position[0] >= self.position[0] - 8 + offsetz) and (position[0] <= self.position[0] + 9 + offsetz) and (position[1] >= self.position[1] - 6 + offsetz) and (position[1] <= self.position[1] + 7 + offsetz):
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
