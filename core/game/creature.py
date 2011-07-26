from game.engine import getSpectators
from packet import TibiaPacket
from game.map import placeCreature, removeCreature, getTile
import thread
import game.enum as enum
import config
import time
import copy

# Unique ids, thread safe too
def __uid():
    idsTaken = 1000
    while True:
        idsTaken += 1
        yield idsTaken
        
__uniqueId = __uid().next
__uniqueLock = thread.allocate_lock()
def uniqueId():
    __uniqueLock.acquire()
    id = __uniqueId()
    __uniqueLock.release()
    return id

allCreatures = {}

class Creature:
    
    def __init__(self, data, position, cid=None):
        self.data = data
        self.creatureType = 0
        self.direction = 0
        self.position = position
        self.speed = 100
        self.scripts = { "onNextStep":[]}
        self.cid = cid if cid else self.generateClientID()
        self.outfit = [self.data["looktype"], self.data["lookhead"], self.data["lookbody"], self.data["looklegs"], self.data["lookfeet"]]
        self.mount = 0
        self.mounted = 0
        self.addon = 0
        self.action = None
        self.actionLock = thread.allocate_lock()
        self.lastStep = 0
        self.target = None # target for follow/attacks based on modes
        
        # We are trackable
        allCreatures[self.cid] = self
        
    def name(self):
        return self.data["name"]

    def clientId(self):
        return self.cid

    def generateClientID(self):
        raise NotImplementedError("This function must be overrided by a secondary level class!")
        
    def stepDuration(self, ground):
        if time.time() - self.lastStep < 1: 
            return (ground.speed / self.speed) # TODO
        return 1

    def move(self, direction, spectators=None):
        import data.map.info
        
        self.direction = direction
        
        # Make packet
        stream = TibiaPacket(0x6D)
        stream.position(self.position)
        
        oldStackpos = getTile(self.position).findCreatureStackpos(self)
        stream.uint8(oldStackpos)
        
        
        # Recalculate position
        position = self.position[:] # Important not to remove the : here, we don't want a reference!
        if direction is 0:
            position[1] = self.position[1] - 1
        elif direction is 1:
            position[0] = self.position[0] + 1
        elif direction is 2:
            position[1] = self.position[1] + 1
        elif direction is 3:
            position[0] = self.position[0] - 1
        elif direction is 4:
            position[1] = self.position[1] + 1
            position[0] = self.position[0] - 1
        elif direction is 5:
            position[1] = self.position[1] + 1
            position[0] = self.position[0] + 1
        elif direction is 6:
            position[1] = self.position[1] - 1
            position[0] = self.position[0] - 1
        elif direction is 7:
            position[1] = self.position[1] - 1
            position[0] = self.position[0] + 1
            
        # We don't walk out of the map!
        if position[0] < 1 or position[1] < 1 or position[0] > data.map.info.width or position[1] > data.map.info.height:
           return False
                    
        stream.position(position)
        newTile = getTile(position)
        
        if self.lastStep+self.stepDuration(newTile.getThing(0)) > time.time():
            return False
            
        else:
            self.lastStep = time.time()
        if newTile.creatures(): # Dont walk to creatures
            return False
            
        removeCreature(self, self.position)
        placeCreature(self, position)
        
        oldPosition = self.position[:]
        self.position = position
              
        # Send to everyone   
        if not spectators:
            spectators = getSpectators(position)
        
        for spectator in spectators:
            streamX = stream
            if spectator.player == self:
                streamX = copy.copy(stream)
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
            
            canSeeNew = spectator.player.canSee(position)
            canSeeOld = spectator.player.canSee(oldPosition)
            if not canSeeOld and canSeeNew:
                stream2 = TibiaPacket()
                stream2.addTileCreature(position, 1, self, spectator.player) # This automaticly deals with known list so
                stream2.send(spectator)
                
            elif canSeeOld and not canSeeNew:
                stream2 = TibiaPacket()
                #if self.cid in spectator.player.knownCreatures:
                #    spectator.player.knownCreatures.remove(self.cid) # Remove him from the known list
                    
                stream2.removeTileItem(oldPosition, oldStackpos)
                stream2.send(spectator)
                
            elif not canSeeOld and not canSeeNew: # Happend on the last 4 squares in the +1 rim, cause a debug with etc rx=-1 (also a ry, but tibia fail to meansion it)
                pass
            else:
                streamX.send(spectator) 

        if len(self.scripts["onNextStep"]):
            for script in self.scripts["onNextStep"]:
                script(self)
                self.scripts["onNextStep"].remove(script)
                
        return True # Required for auto walkings

    def teleport(self, position):
        # 4 steps, remove item (creature), send new map and cords, and effects 
        
        stream = TibiaPacket()
        stream.removeTileItem(self.position, getTile(self.position).findCreatureStackpos(self))
        stream.magicEffect(self.position, 0x02)
        stream.sendto(getSpectators(self.position, ignore=[self]))
        
        removeCreature(self, self.position)
        placeCreature(self, position)
        if self.creatureType == 0:
            stream = TibiaPacket(0x6C)
            stream.position(self.position)
            stream.uint8(1)
            stream.uint8(0x64)
            stream.position(position)
            stream.map_description((position[0] - 8, position[1] - 6, position[2]), 18, 14, self)
            stream.magicEffect(position, 0x02)
            stream.send(self.client)
            
        self.position = position  
        
        for spectator in getSpectators(position, ignore=[self]):
            stream = TibiaPacket()
            stream.addTileCreature(position, 1, self, spectator.player)
            stream.magicEffect(position, 0x02)
            stream.send(spectator)
                
        

    def turn(self, direction):
        if self.direction is direction:
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