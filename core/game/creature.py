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
        self.actionLock = threading.Lock()
        self.lastStep = 0
        self.target = None # target for follow/attacks based on modes
        self.vars = {}
        
        # We are trackable
        allCreatures[self.cid] = self
        
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
            return ground.speed / self.speed
        return delay

    def notPossible(self):
        # Needs to be overrided in player
        # Here we can inform a script if a illigal event
        # Right now, don't care
        return
        
    def move(self, direction, spectators=None, level=0):
        self.actionLock.acquire()
        import data.map.info
        self.direction = direction
        
        
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
           return False
                    
        # New Tile
        newTile = getTile(position)
        oldTile = getTile(oldPosition)

        oldStackpos = oldTile.findCreatureStackpos(self)

            
        if newTile.getThing(0).solid:
            self.notPossible()
            raise game.errors.ImpossibleMove  # Prevent walking on solid tiles
            return False
            
        if newTile.creatures(): # Dont walk to creatures, too be supported
            self.notPossible()
            raise game.errors.ImpossibleMove
            return False
        
        if not level and self.lastStep+self.stepDuration(newTile.getThing(0)) > time.time():
            self.actionLock.release()
            raise game.errors.Cheat("Stepping too fast!")
            return False
            
        else:
            self.lastStep = time.time()
        
        self.lastStep = time.time()


        

        
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
            game.scriptsystem.get('walkOff').runSync(item, self, None, item, oldPosition)

        # Deal with preWalkOn
        for item in newTile.getItems():
            game.scriptsystem.get('preWalkOn').runSync(item, self, None, item, oldTile, newTile, position)
            
            
        newStackPos = newTile.placeCreature(self)

        if not newStackPos:
            raise game.errors.ImpossibleMove
            return False
            
        oldTile.removeCreature(self)
        
            
        
        self.position = position
                
        # Send to everyone   
        if not spectators:
            spectators = getSpectators(position)

        for spectator in spectators:
            streamX = stream
            canSeeNew = spectator.player.canSee(position)
            canSeeOld = spectator.player.canSee(oldPosition)

            if spectator.player == self:
                streamX = copy.copy(stream)
                
                if oldPosition[2] > oldPosition[2]:
                    streamX.moveUpPlayer(self, oldPosition)
                        
                elif oldPosition[2] < oldPosition[2]:
                    streamX.moveDownPlayer(self, oldPosition)
                        
                if direction < 4:
                    self.updateMap(direction, streamX)
                else:
                    if direction & 2 == 2:
                        # North
                        self.updateMap(0, streamX)
                    else:
                        # South
                        self.updateMap(2, streamX)
                    if direction & 1 == 1:
                        # East
                        self.updateMap(1, streamX)
                    else:
                        # West
                        self.updateMap(3, streamX)
                    
                canSeeOld = True
                    
            elif not canSeeOld and canSeeNew:
                streamX.addTileCreature(position, 1, self, spectator.player) # This automaticly deals with known list so
                    
            elif canSeeOld and not canSeeNew:
                streamX.removeTileItem(oldPosition, oldStackpos)

            streamX.send(spectator) 

        if len(self.scripts["onNextStep"]):
            for script in self.scripts["onNextStep"]:
                script(self)
                self.scripts["onNextStep"].remove(script)
                
               
        # Deal with walkOn
        for item in newTile.getItems(): # Scripts
            game.scriptsystem.get('walkOn').run(item, self, None, item, position)
            if item.teledest:
                try:
                    self.teleport(item.teledest)
                except:
                    log.msg("%d (%s) got a invalid teledist (%s), remove it!" % (item.itemId, str(item), str(item.teledest)))
                    del item.teledest
        self.actionLock.release()
        return True # Required for auto walkings

    def magicEffect(self, pos, type):
        stream = TibiaPacket()
        stream.magicEffect(pos, type)
        stream.sendto(getSpectators(pos))
        
    def shoot(self, fromPos, toPos, type):
        stream = TibiaPacket()
        stream.shoot(fromPos, toPos, type)
        stream.sendto(getSpectators(pos))

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
        
    def teleport(self, position):
        # 4 steps, remove item (creature), send new map and cords, and effects 
        newTile = getTile(position)
        
        if newTile.things[0].solid:
            raise game.errors.SolidTile()
        
        
        stream = TibiaPacket()
        oldStackpos = getTile(self.position).findCreatureStackpos(self)
        stream.removeTileItem(self.position, oldStackpos)
        stream.magicEffect(self.position, 0x02)
        stream.sendto(getSpectators(self.position, ignore=[self]))
        
        removeCreature(self, self.position)
        stackpos = placeCreature(self, position)
        if self.creatureType == 0:
            stream = TibiaPacket(0x6C)
            stream.position(self.position)
            stream.uint8(oldStackpos)
            stream.uint8(0x64)
            stream.position(position)
            stream.mapDescription((position[0] - 8, position[1] - 6, position[2]), 18, 14, self)
            stream.magicEffect(position, 0x02)
            stream.send(self.client)
            
        self.position = position  
        
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
        
    def say(self, message):
        stream = TibiaPacket(0xAA)
        stream.uint32(00)
        stream.string(self.data["name"])
        stream.uint16(self.data["level"] if "level" in self.data else 0)
        stream.uint8(enum.MSG_SPEAK_SAY)
        stream.position(self.position)
        stream.string(message)
        stream.sendto(getSpectators(self.position, config.sayRange))

    def yell(self, message):
        stream = TibiaPacket(0xAA)
        stream.uint32(00)
        stream.string(self.data["name"])
        stream.uint16(self.data["level"] if "level" in self.data else 0)
        stream.uint8(enum.MSG_SPEAK_YELL)
        stream.position(self.position)
        stream.string(message)
        stream.sendto(getSpectators(self.position, config.yellRange))
        
    def stopAction(self):
        try:
            self.action.cancel()
        except:
            pass
        self.action = None
        
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
                del self.vars[inspect.stack()[0] + name]
            else:
                self.vars[inspect.stack()[0] + name] = value
        except:
            return None
            
    def getVar(self, name):
        try:
            return self.vars[inspect.stack()[0] + name]
        except:
            return None
