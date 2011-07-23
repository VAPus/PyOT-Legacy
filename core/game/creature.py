from game.engine import getSpectators
from packet import TibiaPacket
from game.map import placeCreature, removeCreature, getTile
import thread
import game.enum as enum

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
        self.speed = 0x0032
        self.scripts = {"onWalk":None, "onNextStep":[]}
        self.cid = cid if cid else self.generateClientID()
        self.outfit = [self.data["looktype"], self.data["lookhead"], self.data["lookbody"], self.data["looklegs"], self.data["lookfeet"]]
        self.mount = 0
        self.mounted = 0
        self.addon = 0
        self.action = None
        self.actionLock = thread.allocate_lock()
        
        # We are trackable
        allCreatures[self.cid] = self
        
    def name(self):
        return self.data["name"]

    def clientId(self):
        return self.cid

    def generateClientID(self):
        raise NotImplementedError("This function must be overrided by a secondary level class!")
        
    def stepDuration(self, tile):
        return (tile.speed / self.speed) # TODO

    def move(self, direction, spectators=None):
        import data.map.info
        
        self.direction = direction
        
        # Make packet
        stream = TibiaPacket(0x6D)
        stream.position(self.position)
        
        oldStackpos = getTile(self.position).findCreatureStackpos(self)
        stream.uint8(getTile(self.position).findCreatureStackpos(self))
        
        
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
        
        if newTile.creatures(): # Dont walk to creatures
            return False
            
        removeCreature(self, self.position)
        placeCreature(self, position)
        
        oldPosition = self.position[:]
        self.position = position
        
        if self.scripts["onWalk"]:
            self.scripts["onWalk"]()
            del self.scripts["onWalk"]
        # Send to everyone   
        if not spectators:
            spectators = getSpectators(position)
            
        for spectator in spectators:
            canSeeNew = spectator.player.canSee(position)
            canSeeOld = spectator.player.canSee(oldPosition)
            if not canSeeOld and canSeeNew:
                stream2 = TibiaPacket()
                stream2.addTileCreature(position, 1, self, spectator.player) # This automaticly deals with known list so
                stream2.send(spectator)
                spectators.remove(spectator)
                
            elif canSeeOld and not canSeeNew:
                stream2 = TibiaPacket()
                if self.cid in spectator.player.knownCreatures:
                    spectator.player.knownCreatures.remove(self.cid) # Remove him from the known list
                    
                stream2.removeTileItem(oldPosition, oldStackpos)
                stream2.send(spectator)
                spectators.remove(spectator)
                
            elif not canSeeOld and not canSeeNew: # Happend on the last 4 squares in the +1 rim, cause a debug with etc rx=-1 (also a ry, but tibia fail to meansion it)
                if self.cid in spectator.player.knownCreatures:
                    spectator.player.knownCreatures.remove(self.cid) # Also remove him from the known list. This check is probably not needed, but who knowns, teleports? :P
                spectators.remove(spectator)
                
        stream.sendto(spectators) 
        
        return True # Required for auto walkings

    def say(self, message):
        stream = TibiaPacket(0xAA)
        stream.uint32(00)
        stream.string(self.data["name"])
        stream.uint16(self.data["level"] if "level" in self.data else 0)
        stream.uint8(enum.MSG_SPEAK_SAY)
        stream.position(self.position)
        stream.string(message)
        stream.sendto(getSpectators(self.position))

    def yell(self, message):
        stream = TibiaPacket(0xAA)
        stream.uint32(00)
        stream.string(self.data["name"])
        stream.uint16(self.data["level"] if "level" in self.data else 0)
        stream.uint8(enum.MSG_SPEAK_YELL)
        stream.position(self.position)
        stream.string(message)
        stream.sendto(getSpectators(self.position))
        
    def stopAction(self):
        try:
            self.action.cancel()
        except:
            pass
        del self.action
        
    def canSee(self, position):
        if abs(position[0]-self.position[0]) < 9 and abs(position[1]-self.position[1]) < 7:
            return True
        