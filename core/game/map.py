from game.item import Item
import game.item
from twisted.internet import threads, reactor
from twisted.python import log
import scriptsystem
from collections import deque
import config
import game.enum
import time
import io
import struct
import sys
import itertools
import gc
import data.map.info as mapInfo

##### Position class ####
def __uid():
    idsTaken = 1
    while True:
        idsTaken += 1
        yield idsTaken
instanceId = __uid().next

def packPos(x,y,z):
    return (z << 24) + (x << 10) + y

def unpackPos(sum):
    z = sum >> 24
    xSum = sum - (z << 24)
    x = xSum >> 10
    y = xSum - (x << 10)

    return x,y,z

def unpackPos(sum):
    z = sum >> 24
    x = sum >> 10 & 1024
    y = sum & 1024

    return x,y,z

def getTile(pos):
    x,y,z,instanceId = pos.x, pos.y, pos.z, pos.instanceId
    sectorX, sectorY = mapInfo.sectorSize
    iX = x // sectorX
    iY = y // sectorY
    pX = x % sectorX
    pY = y % sectorY

    sectorSum = (instanceId << 22) + (iX << 11) + iY
    posSum = packPos(pX, pY, z)
    area = None
    try:
        area = knownMap[sectorSum]
    except KeyError:
        if loadTiles(x, y, instanceId):
            try:
                return knownMap[sectorSum][posSum]
            except:
                return None
    else:
        try:
            return area[posSum]
        except:
            return None

def setTile(pos, tile):
    x,y,z,instanceId = pos.x, pos.y, pos.z, pos.instanceId
    sectorX, sectorY = mapInfo.sectorSize
    iX = x // sectorX
    iY = y // sectorY
    pX = x % sectorX
    pY = y % sectorY

    sectorSum = (instanceId << 22) + (iX << 11) + iY
    posSum = packPos(pX, pY, z)
    area = None
    try:
        area = knownMap[sectorSum]
    except KeyError:
        if loadTiles(x, y, instanceId):
            try:
                knownMap[sectorSum][posSum] = tile
                return True
            except:
                return False
    else:
        try:
            area[posSum] = tile
            return True
        except:
            return False

def getTileConst(x,y,z,instanceId):
    sectorX, sectorY = mapInfo.sectorSize
    iX = x // sectorX
    iY = y // sectorY
    pX = x % sectorX
    pY = y % sectorY
        
    sectorSum = (instanceId << 22) + (iX << 11) + iY
    posSum = packPos(pX,pY,z)
    area = None

    try:
        area = knownMap[sectorSum]
    except KeyError:
        if loadTiles(x, y, instanceId):
            try:
                return knownMap[sectorSum][posSum]
            except:
                return None
    else:
        try:
            return area[posSum]
        except:
            return None
        
def getHouseId(pos):
    try:
        return getTile(pos).houseId
    except:
        return False
        
def placeCreature(creature, pos):
    try:
        return getTile(pos).placeCreature(creature)
    except:
        return False
        
def removeCreature(creature, pos):
    try:
        return getTile(pos).removeCreature(creature)
    except:
        return False  

def newInstance(base=None):
    instance = instanceId()
    if base:
        instances[instance] = base + '/'
    else:
        instances[instance] = ''
        
    return instance

class Tile(object):
    __slots__ = ('things', 'ground', 'flags')
    def __init__(self, ground, items=None, flags=0):
        self.ground = ground

        self.things = items or None
        
        self.flags = flags

    def getCreatureCount(self):
        if not self.things: return 0

        count = 0
        for thing in self.things:
            if isinstance(thing, Creature):
                count += 1

        return count
    
    def getItemCount(self):
        if not self.things: return 0

        return len(self.things) - self.getCreatureCount()
        
    def getTopItemCount(self):
        if not self.things: return 0

        count = 0
        for thing in self.things:
            if isinstance(thing, Item) and thing.ontop:
                count += 1
            else:
                break

        return count

    def getBottomItemCount(self):
        if not self.things: return 0

        count = 0
        for thing in self.things[::-1]:
            if isinstance(thing, Item) and not thing.ontop:
                count += 1
            else:
                break

        return count

    def getFlags(self):
        return self.flags or 0
        
    def setFlag(self, flag):
        flags = self.getFlags()
        if not flags & flag:
            self.flags = flags + flag

    def unsetFlag(self, flag):
        if self.getFlags() & flag:
            self.flags -= flag
            
    def placeCreature(self, creature):
        if not self.things:
            self.things = [creature]
            return 1

        pos = len(self.things) - self.getBottomItemCount()
        
        self.things.insert(pos, creature)

        if pos > 9:
            print self.things
            print pos, self.countNflags
            raise Exception("Item position > 9! Likely we need to deal with this ")
        return pos+1
        
    def removeCreature(self,creature):
        self.things.remove(creature)
        
    def placeItem(self, item):
        assert isinstance(item, Item)
        if not self.things:
            self.things = [item]
            return 1

        if item.ontop:
            pos = self.getTopItemCount()
            self.things.insert(pos, item)
        else:
            pos = len(self.things)
            self.things.append(item)
        if pos > 9:
            print self.things
            print pos, self.countNflags
            raise Exception("Item position > 9! Likely we need to deal with this ")
        return pos+1
    
    def placeItemEnd(self, item):
        if not self.things:
            self.things = [item]
            return 1

        self.things.append(item)
        return len(self.things)
        
    def bottomItems(self):
        if not self.things: return ()
        bottomItems = self.getBottomItemCount()
        if not bottomItems:
            return ()

        return self.things[len(self.things) - bottomItems:]
        
    def topItems(self):
        yield self.ground

        if not self.things: return
        for thing in self.things:
            if isinstance(thing, Item) and thing.ontop:
                yield thing
            else:
                break
            
    def getItems(self):
        yield self.ground

        if not self.things:
            return

        for thing in self.things:
            if isinstance(thing, Item):
                yield thing
 
    def creatures(self):
        if not self.things:
            return

        for thing in self.things:
            if isinstance(thing, Creature):
                yield thing
                
    def hasCreatures(self):
        if not self.things:
            return False

        for thing in self.things:
            if isinstance(thing, Creature):
                return True
        
    def topCreature(self):
        if not self.things:
            return None

        for thing in self.things:
            if isinstance(thing, Creature):
                return thing

    def removeItem(self, item):
        item.stopDecay()
        self.things.remove(item)
        
    def removeItemWithId(self, itemId):
        for i in self.getItems():
            if i.itemId == itemId:
                self.removeItem(i)
                
        
    def getThing(self, stackpos):
        if stackpos == 0: return self.ground
        try:
            return self.things[stackpos-1]
        except:
            return None
    
    def setThing(self, stackpos, item):
        self.things[stackpos] = item
        
    def findItem(self, sid):
        for x in self.bottomItems():
            if x.itemId == sid:
                return x

    def findStackpos(self, thing):
        return self.things.index(thing)+1
        
    def findClientItem(self, cid, stackpos=None):
        for x in self.bottomItems():
            if x.cid == cid:
                if stackpos:
                    return (self.things.index(x), x)
                return x
                

    def copy(self):
        items = None
        if self.items:
            items = []
            for item in self.items:
                items.append(item.copy())

        flags = self.flags
        if flags & TILEFLAGS_STACKED:
            flags -= TILEFLAGS_STACKED

        return Tile(self.ground.copy(), items, flags)

class HouseTile(Tile):
    __slots__ = ('houseId', 'position')
    

dummyItems = {} 

knownMap = {} # sectorSum -> {posSum}

instances = {0: ''}

houseTiles = {}

houseDoors = {}

dummyTiles = {}
    
def loadTiles(x,y, instanceId):
    if x > mapInfo.height or y > mapInfo.width or x < 0 or y < 0:
        return None
    
    return load(x // mapInfo.sectorSize[0], y // mapInfo.sectorSize[1], instanceId)

### Start New Map Format ###

attributeIds = ('actions', 'count', 'solid','blockprojectile','blockpath','usable','pickable','movable','stackable','ontop','hangable','rotatable','animation', 'doorId', 'depotId', 'text', 'written', 'writtenBy', 'description', 'teledest')

# Format (Work in Progress)
# Note: Max sector size in PyOt is 1024.
"""
    <uint8>floor_level
    floorLevel < 60
        <loop>

        <uint16>itemId
        <uint8>attributeCount / other
        
        itemId >= 100:
            every attributeCount (
                See attribute format
            )

        itemId == 50:
            <int32> Tile flags
            
        itemId == 51:
            <uint32> houseId
            
        itemId == 0:
            skip attributeCount fields
            
        {
            ; -> go to next tile
            | -> skip the remaining y tiles (if itemId = 0, and attrNr, skip attrNr x tiles)
            ! -> skip the remaining x and y tiles
            , -> more items
        }
        
    floorLevel == 60:
        <uint16>center X
        <uint16>center Y
        <uint8>center Z
        <uint8> Radius from center creature might walk
        <uint8> count (
            <uint8> type (61 for Monster, 62 for NPC)
            <uint8> nameLength
            <string> Name
             
            <int8> X from center
            <int8> Y from center
                
            <uint16> spawntime in seconds
                       
            }
        )
    Attribute format:
    
    {
        <uint8>attributeId
        <char>attributeType
        {
            attributeType == i (
                <int32>value
            )
            attributeType == s (
                <uint16>valueLength
                <string with length valueLength>value
            )
            attributeType == T
            attributeType == F

            attributeType == l (
                <uint8>listItems
                <repeat this block for listItems times> -> value
            )
        }
        
        
    }
"""

l_unpack = struct.Struct("<HB").unpack
long_unpack = struct.Struct("<i").unpack
creature_unpack = struct.Struct("<bbH").unpack
spawn_unpack = struct.Struct("<HHBBB").unpack

def loadSectorMap(code, instanceId, baseX, baseY):
    global dummyItems, dummyTiles

    thisSectorMap = {}
    pos = 0
    codeLength = len(code)
    skip = False
    skip_remaining = False
    houseId = 0
    housePosition = None
    

    # Bind them locally, this is suppose to make a small speedup as well, local things can be more optimized :)
    # Pypy gain nothing, but CPython does.

    l_Item = game.item.Item
    l_Tile = Tile
    l_HouseTile = HouseTile
    
    l_attributes = attributeIds
    
    # Spawn commands
    l_getNPC = game.npc.getNPC
    l_getMonster = game.monster.getMonster
    
    # This is the Z loop (floor), we read the first byte
    while pos < codeLength:
        # First byte where we're at.
        level = ord(code[pos])
        pos += 1
        
        zSum = level << 24 
        if level == 60:
            centerX, centerY, centerZ, centerRadius, creatureCount = spawn_unpack(code[pos:pos+7])
            
            pos += 7
                            
            # Mark a position
            centerPoint = Position(centerX, centerY, centerZ, instanceId)
                            
            # Here we use attrNr as a count for 
            for numCreature in xrange(creatureCount):
                creatureType = ord(code[pos])
                nameLength = ord(code[pos+1])
                name = code[pos+2:pos+nameLength+2]
                pos += 6 + nameLength
                spawnX, spawnY, spawnTime = creature_unpack(code[pos-4:pos])
                
                if creatureType == 61:
                    creature = l_getMonster(name)
                else:
                    creature = l_getNPC(name)
                if creature:
                    creature.spawn(Position(centerX+spawnX, centerY+spawnY, centerZ, instanceId), radius=centerRadius, spawnTime=spawnTime, radiusTo=centerPoint)
                else:
                    print "Spawning of %s '%s' failed, it doesn't exist!" % ("Monster" if creatureType == 61 else "NPC", name)
                                    
            continue
        
        # Loop over the mapInfo.sectorSize[0] x rows
        for xr in xrange(mapInfo.sectorSize[0]):

            xSum = (xr << 10) + zSum
            # Since we need to deal with skips we need to deal with counts and not a static loop (pypy will have a problem unroll this hehe)
            yr = 0
            
            while yr < mapInfo.sectorSize[1]:
                # The items array and the flags for the Tile.
                items = []
                flags = 0
                ground = None

                # We have no limit on the amount of items that a Tile might have. Loop until we hit a end.
                while True:
                    # uint16 itemId / type
                    # uint8 attrNr / count
                    itemId, attrNr = l_unpack(code[pos:pos+3])

                    # Do we have a positive id? If not its a blank tile
                    if itemId:
                        # Tile flags
                        if itemId == 50:
                            pos += 2
                            # int32
                            flags = long_unpack(code[pos:pos+4])[0]
                            pos += 5
                        
                        # HouseId?
                        elif itemId == 51:
                            pos += 2
                            # int32
                            houseId = long_unpack(code[pos:pos+4])[0]
                            housePosition = ((xr + baseX) >> 20) + ((yr + baseY) >> 4) + level
                            pos += 5
                            
                        elif attrNr:
                            pos += 3
                            attr = {}
                            for n in xrange(attrNr):
                                name = l_attributes[ord(code[pos])]
                                    
                                opCode = code[pos+1]
                                pos += 2
                                
                                if opCode == "i":
                                    pos += 4
                                    value = long_unpack(code[pos-4:pos])[0]
                                elif opCode == "s":
                                    valueLength = long_unpack(code[pos:pos+4])[0]
                                    pos += valueLength + 4
                                    value = code[pos-valueLength:pos]
                                elif opCode == "T":
                                    value = True
                                elif opCode == "F":
                                    value = False
                                elif opCode == "l":
                                    value = []
                                    length = ord(code[pos])

                                    pos += 1
                                    for i in xrange(length):
                                        opCode = code[pos]
                                        pos += 1
                                        if opCode == "i":
                                            pos += 4
                                            item = long_unpack(code[pos-4:pos])[0]
                                        elif opCode == "s":
                                            valueLength = long_unpack(code[pos:pos+4])[0]
                                            pos += valueLength + 4
                                            item = code[pos-valueLength:pos]
                                        elif opCode == "T":
                                            item = True
                                        elif opCode == "F":
                                            item = False
                                        value.append(item)
                                        
                                attr[name] = value
                                
                            pos += 1
                            item = l_Item(itemId, **attr)
                            item.fromMap = True
                            if not ground:
                                ground = item
                            else:
                                items.append(item)
                        else:
                            pos += 4
                            try:
                                if not ground:
                                    ground = dummyItems[itemId]
                                else:
                                    items.append(dummyItems[itemId])
                            except KeyError:
                                item = l_Item(itemId)
                                item.tileStacked = True
                                item.fromMap = True
                                dummyItems[itemId] = item
                                if not ground:
                                    ground = item
                                else:
                                    items.append(item)
                                
                                    

                    else:
                        pos += 4
                        if attrNr:
                            yr += attrNr -1
                        
                    
                        
                    v = code[pos-1]
                    if v == ';': break
                    elif v == '|':
                        skip = True
                        if attrNr:
                            xr += attrNr -1
                        break
                    elif v == '!':
                        skip = True
                        skip_remaining = True
                        break
                    # otherwise it should be ",", we don't need to verify this.
                if ground:
                    ySum = xSum + yr

                    # For the PvP configuration option, yet allow scriptability. Add/Remove the flag.
                    if config.globalProtectionZone and not flags & TILEFLAGS_PROTECTIONZONE:
                        flags += TILEFLAGS_PROTECTIONZONE
                    elif not config.protectedZones and flags & TILEFLAGS_PROTECTIONZONE:
                        flags -= TILEFLAGS_PROTECTIONZONE

                    if houseId:
                        # Fix flags if necessary, TODO: Move this to map maker!
                        if config.protectedZones and not flags & TILEFLAGS_PROTECTIONZONE:
                            flags += TILEFLAGS_PROTECTIONZONE
                            
                        tile = l_HouseTile(ground, items, flags)
                        tile.houseId = houseId
                        tile.position = housePosition
                        
                        
                        # Find and cache doors
                        for i in tile.getItems():
                            if i.hasAction("houseDoor"):
                                try:
                                    houseDoors[houseId].append(housePosition)
                                    break
                                except:
                                    houseDoors[houseId] = [housePosition]
                                
                        
                        if houseId in houseTiles:
                            houseTiles[houseId].append(tile)
                        else:
                            houseTiles[houseId] = [tile]
                            
                        try:
                            for item in game.house.houseData[houseId].data["items"][housePosition]:
                                tile.placeItem(item)
                        except KeyError:
                            pass
    
                        houseId = 0
                        housePosition = None
                        thisSectorMap[ySum] = tile

                    elif config.stackTiles:
                        ok = ground.solid
                        if not ok:
                            for i in items:
                                if i.solid:
                                    ok = True
                                    break
                        if ok:
                            # Constantify items on stacked tiles. This needs some workarounds w/transform. But prevents random bug.
                            items = tuple(items) if items else None
                            hash = ground, items
                            try:
                                thisSectorMap[ySum] = dummyTiles[hash]
                            except:
                                tile = l_Tile(ground, items, flags + TILEFLAGS_STACKED)
                                dummyTiles[hash] = tile
                                thisSectorMap[ySum] = tile

                        else:
                            thisSectorMap[ySum] = l_Tile(ground, items, flags)

                    else:
                        thisSectorMap[ySum] = l_Tile(ground, items, flags)
                yr += 1

                if skip:
                    skip = False
                    break

            if skip_remaining:
                skip_remaining = False
                break
                
    return thisSectorMap           
### End New Map Format ###
def load(sectorX, sectorY, instanceId):
    sectorSum = (instanceId << 22) + (sectorX << 11) + sectorY
    
    if sectorSum in knownMap:
        return False
          
    t = time.time()
    
    # Attempt to load a sector file
    try:
        with io.open("data/map/%s%d.%d.sec" % (instances[instanceId], sectorX, sectorY), "rb") as f:
            map = loadSectorMap(f.read(), instanceId, sectorX * mapInfo.sectorSize[0], sectorY * mapInfo.sectorSize[1])
            knownMap[sectorSum] = map
    except IOError:
        # No? Mark it as empty
        knownMap[sectorSum] = None
        return False
        
    print "Loading of %d.%d.sec took: %f" % (sectorX, sectorY, time.time() - t)    
    
    if config.performSectorUnload:
        reactor.callLater(config.performSectorUnloadEvery, _unloadMap, sectorX, sectorY, instanceId)
    
    scriptsystem.get('postLoadSector').runSync("%d.%d" % (sectorX, sectorY), None, None, sector=map, instanceId=instanceId)
    
    return True

# Map cleaner
def _unloadCheck(sectorX, sectorY, instanceId):
    # Calculate the x->x and y->y ranges
    # We're using a little higher values here to avoid reloading again 
    
    xMin = (sectorX * mapInfo.sectorSize[0]) + 14
    xMax = (xMin + mapInfo.sectorSize[0]) + 14
    yMin = (sectorY * mapInfo.sectorSize[1]) + 11
    yMax = (yMin + mapInfo.sectorSize[1]) + 11
    try:
        for player in game.player.allPlayers.viewvalues():
            pos = player.position # Pre get this one for sake of speed, saves us a total of 4 operations per player
            
            # Two cases have to match, the player got to be within the field, or be able to see either end (x or y)
            if instanceId == pos.instanceId and (pos[0] < xMax or pos[0] > xMin) and (pos[1] < yMax or pos[1] > yMin):
                return False # He can see us, cancel the unloading
    except:
        return False # Players was changed.
        
    return True
    
def _unloadMap(sectorX, sectorY, instanceId):
    print "Checking %d.%d.sec (instanceId %s)" % (sectorX, sectorY, instanceId)
    t = time.time()
    if _unloadCheck(sectorX, sectorY, instanceId):
        print "Unloading...."
        unload(sectorX, sectorY, instanceId)
        print "Unloading took: %f" % (time.time() - t)   
    reactor.callLater(config.performSectorUnloadEvery, _unloadMap, sectorX, sectorY, instanceId)
    
def unload(sectorX, sectorY, instanceId):
    sectorSum = (instanceId << 22) + (sectorX << 11) + sectorY
    try:
        del knownMap[sectorSum]
    except:
        pass
