from twisted.internet.defer import inlineCallbacks, Deferred
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
        self.extAction = 0
        self.lastStep = 0
        self.target = None # target for follow/attacks
        self.targetMode = 0 # 0 = no particular reason, 1 = attack, 2 = follow
        self.vars = {}
        self.cooldowns = {} # This is a int32, icon are the first 8, then group is the next 7
        self.regenerate = None
        self.alive = True
        self.lastDamager = None
        self.solid = not config.creatureWalkthrough
        self.shield = 0
        self.emblem = 0
        self.skull = 0
        self.knownBy = set()
        self.conditions = {}
        self.walkPattern = None
        
        # We are trackable
        allCreatures[self.cid] = self

    def actionLock(self, *argc, **kwargs):
        if self.lastAction >= time.time():
            if "stopIfLock" in kwargs and kwargs["stopIfLock"]:
                return False
            game.engine.safeCallLater(0.1, *argc, **kwargs)
            return False
        else:
            self.lastAction = time.time()
            return True

    def extActionLock(self, *argc, **kwargs):
        if self.extAction >= time.time():
            game.engine.safeCallLater(0.1, *argc, **kwargs)
            return False
        else:
            return True
            
    @staticmethod
    def actionDecor(f):
        """ Decorator used by external actions """
        def new_f(creature, *argc, **kwargs):
            if not creature.alive or not creature.actionLock(new_f, creature, *argc, **kwargs) or not creature.extActionLock(new_f, creature, *argc, **kwargs) :
                return
            else:
                creature.extAction = time.time() + 0.2
                creature.lastAction = time.time() + 0.2
                f(creature, *argc, **kwargs)

        return new_f

    def isPlayer(self):
        return False

    def isPremium(self):
        return True
        
    def isNPC(self):
        return False
        
    def isMonster(self):
        return False

    def isItem(self):
        return False
        
    def isPushable(self, by):
        return False
    
    def isAttackable(self, by):
        return False

    def isSummon(self):
        return False
            
    def isSummonFor(self, creature):
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
        return ('creature',) # Static actionID

    def generateClientID(self):
        raise NotImplementedError("This function must be overrided by a secondary level class!")
        
    def stepDuration(self, ground, delay=1.5):
        #if time.time() - self.lastStep < delay:
        if True:
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
    def refreshConditions(self, streamX=None): pass
    
    def despawn(self):
        self.alive = False
        tile = game.map.getTile(self.position)
        stackpos = tile.findCreatureStackpos(self)
        tile.removeCreature(self)
        
        for spectator in getSpectators(self.position):
            stream = spectator.packet()
            stream.removeTileItem(self.position, stackpos)
            stream.send(spectator)
        try:
            if self.respawn:
                if self.spawnTime:
                    game.engine.safeCallLater(self.spawnTime, self.base.spawn, self.spawnPosition)
                else:
                    game.engine.safeCallLater(self.base.spawnTime, self.base.spawn, self.spawnPosition)
        except:
            pass
        
    def move(self, direction, spectators=None, level=0, stopIfLock=False):
        d = Deferred()
        game.engine.safeCallLater(0, self._move, d, direction, spectators, level, stopIfLock)
        return d
        
    @inlineCallbacks
    def _move(self, d, direction, spectators=None, level=0, stopIfLock=False):
        if not self.alive or not level and not self.actionLock(self._move, d, direction, spectators, level):
            return
            
        if not self.alive or not self.data["health"]:
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

        val = yield game.scriptsystem.get("move").run(self)
        if val == False:
            return
            
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
                #self.turn(direction) # Fix me?
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
        delay = self.stepDuration(newTile.getThing(0)) * (config.diagonalWalkCost if direction > 3 else 1)
        self.lastAction += delay
        self.extAction = time.time() + (delay/2)
                
        
            
        # Deal with walkOff
        for item in oldTile.getItems():
            yield game.scriptsystem.get('walkOff').runDefer(item, self, None, position=oldPosition)

        # Deal with preWalkOn
        for item in newTile.getItems():
            r = game.scriptsystem.get('preWalkOn').runSync(item, self, None, oldTile=oldTile, newTile=newTile, position=position)
            if r == False:
                return
            
            
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
            spectators = getPlayers(position, (10, 8))
            
        for spectator in spectators:
            # Make packet
            if not spectator.client:
                continue

            canSeeNew = spectator.canSee(position)
            canSeeOld = spectator.canSee(oldPosition)
            isKnown = self in spectator.knownCreatures
            
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
                print "Send move"
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

                    
                    
            elif (not canSeeOld or not isKnown) and canSeeNew:
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
            game.scriptsystem.get('walkOn').run(item, self, None, position=position, fromPosition=oldPosition)
            if item.teledest:
                try:
                    self.teleport(item.teledest)
                except:
                    log.msg("%d (%s) got a invalid teledist (%s), remove it!" % (item.itemId, str(item), str(item.teledest)))
                    del item.teledest

        
        if d.callback:
            d.callback((self, oldPosition, position))
            
        # Deal with appear and disappear. Ahh the power of sets :)
        oldPosCreatures = game.engine.getCreatures(oldPosition)
        newPosCreatures = game.engine.getCreatures(position)
        disappearFrom = oldPosCreatures - newPosCreatures
        appearTo = newPosCreatures - oldPosCreatures
        for creature2 in disappearFrom:
            game.scriptsystem.get('disappear').run(creature2, self)
            game.scriptsystem.get('disappear').run(self, creature2)
            
        for creature2 in appearTo:
            game.scriptsystem.get('appear').run(creature2, self)
            game.scriptsystem.get('appear').run(self, creature2)
            
    def magicEffect(self, type, pos=None):
        if not pos or pos[0] == 0xFFFF:
            pos = self.position
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

    def rename(self, name):
        newSpectators = game.engine.getPlayers(self.position)
        stackpos = game.map.getTile(self.position).findCreatureStackpos(self)
        
        self.data["name"] = name
        for player in self.knownBy:
            stream = player.packet()
            stream.removeTileItem(self.position, stackpos)
            if player in newSpectators:
                stream.addTileCreature(self.position, stackpos, self, player, True)

            stream.send(player.client)

    def privRename(self, player, name):
        if player in self.knownBy:
            stackpos = game.map.getTile(self.position).findCreatureStackpos(self)
            stream = player.packet()
            stream.removeTileItem(self.position, stackpos)
            originalName = self.data["name"]
            
            def doRename():
                self.data["name"] = name
                stream.addTileCreature(self.position, stackpos, self, player, True)
                self.data["name"] = originalName
                stream.send(player.client)     
                
            reactor.callFromThread(doRename) # For thread safety

            
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
        
    def onHit(self, by, dmg, type, effect=None):
        self.lastDamager = by
          
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
        
        if effect:
            magicEffect = effect
            
        dmg = [dmg]
        textColor = [textColor]
        magicEffect = [magicEffect]
        type = [type]
        
        process = game.scriptsystem.get("hit").runSync(self, self.lastDamager, damage=dmg, type=type, textColor=textColor, magicEffect=magicEffect)
        if process == False:
            return
            
        dmg = dmg[0]
        textColor = textColor[0]
        magicEffect = magicEffect[0]
        type = type[0]
        
        self.magicEffect(magicEffect) 
        
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
            by.message("%s loses %d hitpoint%s due to your attack." % (self.name().capitalize(), -1 * dmg, 's' if dmg < -1 else ''), 'MSG_DAMAGE_DEALT', value = -1 * dmg, color = textColor, pos=self.position)

        if self.isPlayer():
            if by:
                self.message("You lose %d hitpoint%s due to an attack by %s." % (-1 * dmg, 's' if dmg < -1 else '', by.name().capitalize()), 'MSG_DAMAGE_RECEIVED')
            else:
                self.message("You lose %d hitpoint%s." % (-1 * dmg, 's' if dmg < -1 else ''), 'MSG_DAMAGE_RECEIVED')

        elif not self.target and self.data["health"] < 1:
            self.follow(by) # If I'm a creature, set my target
        
        # Modify health
        self.modifyHealth(dmg)
        
        if by and not by.data["health"]:
            by.target = None
            by.targetMode = 0
        
        
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
            return False
            
        return True
           

    def modifyHealth(self, health, spawn=False):
        return self.setHealth(min(self.data["health"] + health, self.data["healthmax"]))
    
    def setMana(self, mana):
        if self.data["health"] > 0:
            self.data["mana"] = mana
            self.refreshStatus()
            return True
        return False
        
    def modifyMana(self, mana):
        return self.setMana(min(self.data["mana"] + mana, self.data["manamax"]))
        
        
    def setSoul(self, soul):
        if self.data["health"] > 0:
            self.data["soul"] = soul
            self.refreshStatus()
            return True
        return False
        
    def modifySoul(self, soul):
        return self.setSoul(self.data["soul"] + soul)
        
    def teleport(self, position):
        """if not self.actionLock(self.teleport, position):
            return False"""
            
        # 4 steps, remove item (creature), send new map and cords, and effects
        oldPosition = self.position[:]
        
        newTile = getTile(position)
        oldPosCreatures = set()
        if not newTile or newTile.things[0].solid:
            raise game.errors.SolidTile()

        try:
            oldStackpos = getTile(oldPosition).findCreatureStackpos(self)
            for spectator in getSpectators(oldPosition, ignore=(self,)):
                stream = spectator.packet()
                stream.removeTileItem(oldPosition, oldStackpos)
                stream.magicEffect(oldPosition, 0x02)
                stream.send(spectator)
            oldPosCreatures = game.engine.getCreatures(oldPosition)
        except:
            pass # Just append creature
        
        stackpos = placeCreature(self, position)
        if not stackpos:
            raise game.errors.ImpossibleMove()
        
        removeCreature(self, oldPosition)
        self.position = position 
        if self.creatureType == 0 and self.client:
            stream = self.packet()
            try:
                stream.removeTileItem(oldPosition, oldStackpos)
            except:
                pass # Just append
            stream.uint8(0x64)
            stream.position(position)
            stream.mapDescription((position[0] - 8, position[1] - 6, position[2]), 18, 14, self)
            #stream.magicEffect(position, 0x02)
            stream.send(self.client)
        
        newPosCreatures = game.engine.getCreatures(position)
        disappearFrom = oldPosCreatures - newPosCreatures
        appearTo = newPosCreatures - oldPosCreatures
        for creature2 in disappearFrom:
            game.scriptsystem.get('disappear').run(creature2, self)

        for creature2 in appearTo:
            game.scriptsystem.get('appear').run(creature2, self)    
         
        
        for spectator in getSpectators(position, ignore=(self,)):
            stream = spectator.packet()
            stream.addTileCreature(position, stackpos, self, spectator.player)
            stream.magicEffect(position, 0x02)
            stream.send(spectator)
                
    def turn(self, direction):
        if self.direction == direction:
            return
            
        if not self.alive or not self.actionLock(self.turn, direction):
            return

        self.direction = direction
        self.extAction = time.time() + 0.15
        
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
            
    def say(self, message, messageType='MSG_SPEAK_SAY'):
        for spectator in getSpectators(self.position, config.sayRange):
            stream = spectator.packet(0xAA)
            stream.uint32(0)
            stream.string(self.data["name"])
            stream.uint16(self.data["level"] if "level" in self.data else 0)
            stream.uint8(stream.enum(messageType))
            stream.position(self.position)
            stream.string(message)
            stream.send(spectator)

    def yell(self, message, messageType='MSG_SPEAK_YELL'):
        for spectator in getSpectators(self.position, config.sayRange):
            stream = spectator.packet(0xAA)
            stream.uint32(0)
            stream.string(self.data["name"])
            stream.uint16(self.data["level"] if "level" in self.data else 0)
            stream.uint8(stream.enum(messageType))
            stream.position(self.position)
            stream.string(message)
            stream.send(spectator)

    def whisper(self, message, messageType='MSG_SPEAK_WHISPER'):
        for spectator in getSpectators(self.position, config.sayRange):
            stream = spectator.packet(0xAA)
            stream.uint32(0)
            stream.string(self.data["name"])
            stream.uint16(self.data["level"] if "level" in self.data else 0)
            stream.uint8(stream.enum(messageType))
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

    def canTarget(self, position, radius=(8,6)):
        if self.position[2] != position[2]: # We are on ground level and we can't see underground
            return False
        
        if (position[0] >= self.position[0] - radius[0]) and (position[0] <= self.position[0] + radius[0]+1) and (position[1] >= self.position[1] - radius[1]) and (position[1] <= self.position[1] + radius[1]+1):
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
            game.engine.saveGlobalStorage = True
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
            game.engine.saveGlobalStorage = True
        except:
            pass

    # Global object storage
    def setGlobalObject(self, field, value):
        try:
            game.engine.globalStorage['objectStorage'][field] = value
            game.engine.saveGlobalStorage = True
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
            game.engine.saveGlobalStorage = True
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

    # Change passability
    def setSolid(self, solid):
        if self.solid == solid:
            return
            
        self.solid = solid
        
        for client in getSpectators(self.position):
            stream = client.packet(0x92)
            stream.uint32(self.cid)
            stream.uint8(self.solid)
            stream.send(client)
            
    def setSolidFor(self, player, solid):
        stream = player.packet(0x92)
        stream.uint32(self.cid)
        stream.uint8(solid)
        stream.send(player.client)
        
    # Shields
    def setPartyShield(self, shield):
        if self.shield == shield:
            return
            
        self.shield = shield
    
        for player in getPlayers(self.position):
            stream = player.packet(0x90)
            stream.uint32(self.cid)
            stream.uint8(self.getPartShield(player))
            stream.send(player.client)
            
    def getPartyShield(self, creature):
        return self.shield # TODO
        
    # Emblem
    def setEmblem(self, emblem):
        if self.emblem == emblem:
            return
        
        self.emblem = emblem

        for player in getPlayers(self.position):
            stream = player.packet()
            stream.addTileCreature(self.position, game.map.getTile(self.position).findStackpos(self), self, player)
            stream.send(player.client)
            
    # Skull
    def setSkull(self, skull):
        if self.skull == skull:
            return
        
        self.skull = skull

        for player in getPlayers(self.position):
            stream = player.packet(0x90)
            stream.uint32(self.cid)
            stream.uint8(self.getSkull(player))
            stream.send(player.client)    
            
    def getSkull(self, creature):
        return self.skull # TODO
        
    def square(self, creature, color=27):
        pass
    
    # Conditions
    def condition(self, condition, stackbehavior=enum.CONDITION_LATER):
        try:
            oldCondition = self.conditions[condition.type]
            if not oldCondition.ticks:
                raise
            
            if stackbehavior == enum.CONDITION_IGNORE:
                return False
            elif stackbehavior == enum.CONDITION_LATER:
                return engine.safeCallLater(oldCondition.ticks * oldCondition.per, self.condition, condition, stackbehavior)
            elif stackbehavior == enum.CONDITION_ADD:
                oldCondition.ticks += forticks
            elif stackbehavior == enum.CONDITION_MODIFY:
                condition.ticks += oldCondition.ticks
                self.conditions[condition.type] = condition
            elif stackbehavior == enum.CONDITION_REPLACE:
                oldCondition.stop()
                self.conditions[condition.type] = condition
                condition.start(self)
                print "Condition"
        except:
            self.conditions[condition.type] = condition
            condition.start(self)
   
        self.refreshConditions()

    def multiCondition(self, *argc, **kwargs):
        try:
            stackbehavior = kwargs["stackbehavior"]
        except:
            stackbehavior = enum.CONDITION_LATER
        
        currCon = argc[0]
        for con in argc[1:]:
            currCon.callback = lambda: self.condition(con, stackbehavior)
            currCon = con
            
        self.condition(argc[0], stackbehavior)
        
    def hasCondition(self, conditionType, subtype=""):
        if subtype and isinstance(conditionType, str):
            conditionType = "%s_%s" % (conditionType, subtype)
        try:
            self.conditions[conditionType]
            return True
        except:
            return False

    def loseCondition(self, conditionType, subtype=""):
        if subtype and isinstance(conditionType, str):
            conditionType = "%s_%s" % (conditionType, subtype)
        try:
            self.condions[conditionType].stop()
            return True
        except:
            return False

    # Spells
    def castSpell(self, spell, strength=None, target=None):
        game.spell.spells[spell][0](self, strength, target)
        
        
class Condition(object):
    def __init__(self, type, subtype="", ticks=1, per=1, *argc, **kwargs):
        self.ticks = ticks
        self.per = per
        self.creature = None
        self.tickEvent = None
        if subtype and isinstance(type, str):
            self.type = "%s_%s" % (type, subtype)
        else:
            self.type = type
        self.effectArgs = argc
        self.effectKwargs = kwargs
        
        try:
            self.effect
        except:
            if type == CONDITION_FIRE:
                self.effect = self.effectFire
            elif type == CONDITION_POISON:
                self.effect = self.effectPoison
        
    def start(self, creature):
        self.creature = creature
        self.init()
        self.tick()
        
    def stop(self):
        try:
            self.tickEvent.cancel()
        except:
            pass
        
        self.finish()
        
    def init(self):
        pass

    def callback(self): pass
    
    def finish(self):
        del self.creature.conditions[self.type]
        self.creature.refreshConditions()
        self.callback()

    def effectPoison(self, damage=0, minDamage=0, maxDamage=0):
        self.creature.magicEffect(EFFECT_HITBYPOISON)
        self.creature.modifyHealth((damage or random.randint(minDamage, maxDamage)) * -1)

    def effectFire(self, damage=0, minDamage=0, maxDamage=0):
        self.creature.magicEffect(EFFECT_HITBYFIRE)
        self.creature.modifyHealth((damage or random.randint(minDamage, maxDamage)) * -1)
        
    def tick(self):
        self.effect(*self.effectArgs, **self.effectKwargs)
        self.ticks -= 1
        if self.ticks > 0:
            self.tickEvent = engine.safeCallLater(self.per, self.tick)
        else:
            self.finish()