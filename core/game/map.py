from game.item import Item
import game.item
from twisted.internet import threads, reactor
from twisted.python import log
import bindconstant
import cPickle
import scriptsystem
from collections import deque
import config
import game.enum
import time
import io
    
def getTile(pos):
    iX = int(pos[0] / 32)
    iY = int(pos[1] / 32)
    pX = pos[0] -iX * 32
    pY = pos[1] -iY * 32
    sectorSum = (iX * 32768) + iY
    try:
        return knownMap[sectorSum][pos[2]][pX][pY]
    except:
        if loadTiles(pos[0], pos[1]):
            try:
                return knownMap[sectorSum][pos[2]][pX][pY]
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

PACK_ITEMS = 0 # top items
PACK_CREATURES = 8
PACK_FLAGS = 16

class Tile(object):
    __slots__ = ('things', 'countNflags')
    def __init__(self, items, topItemCount=0, itemLen=0, flags=0):
        if not topItemCount:
            self.countNflags = 1
            
            # Special case.
            if itemLen == 1:
                #self.things = (items[0],) if game.item.items[items[0].itemId]["a"] & 1 else [items[0]]
                self.things = [items[0]]
                
            else:
                workItems = deque(items)
                self.things = [workItems.popleft()]
                if workItems:
                    bottomItems = []
                    for item in workItems:
                        if item.ontop:
                            self.things.append(item)
                            self.countNflags += 1
                        else:
                            bottomItems.append(item)
                    if bottomItems:
                        self.things.extend(bottomItems) 
  
        else:
            self.things = list(items)
            self.countNflags = topItemCount

        if flags:
            self._modpack(PACK_FLAGS, flags)
            
    def _depack(self, level):
        return (self.countNflags >> level) & 255
        
    def _modpack(self, level, mod):
        self.countNflags += mod << level

    def getCreatureCount(self):
        return self._depack(PACK_CREATURES)
    
    def getItemCount(self):
        return len(self.things) - self._depack(PACK_CREATURES)
        
    def getFlags(self):
        return self._depack(PACK_FLAGS)
        
    def setFlag(self, flag):
        if not self.getFlags() & flag:
            self._modpack(PACK_FLAGS, flag)

    def unsetFlag(self, flag):
        if self.getFlags() & flag:
            self._modpack(PACK_FLAGS, -flag)
            
    def placeCreature(self, creature):
        pos = self._depack(PACK_ITEMS) + self._depack(PACK_CREATURES)
        if pos > 9:
            return

        self.things.insert(pos, creature)
        self._modpack(PACK_CREATURES, 1)

        return pos
        
    def removeCreature(self,creature):
        self._modpack(PACK_CREATURES, -1)
        return self.things.remove(creature)
        
    def placeItem(self, item):
        if item.ontop:
            pos = self._depack(PACK_ITEMS)
            self._modpack(PACK_ITEMS, 1)
        else:
            pos = self._depack(PACK_ITEMS) + self._depack(PACK_CREATURES)
        self.things.insert(pos, item)
        return pos
    
    def placeItemEnd(self, item):
        self.things.append(item)
        return len(self.things)-1

    def ground(self):
        return self.things[0]
        
    def bottomItems(self):
        return self.things[self._depack(PACK_ITEMS) + self._depack(PACK_CREATURES):]
        
    def topItems(self):
        return self.things[:self._depack(PACK_ITEMS)]

    def getItems(self):
        items = self.topItems()[:]
        try:
            items.extend(self.bottomItems())
        except:
            pass
        
        return items
        
    def creatures(self):
        cc = self._depack(PACK_ITEMS)
        return self.things[cc:cc + self._depack(PACK_CREATURES)]
        
    def removeItem(self, item):
        if item.ontop:
            self._modpack(PACK_ITEMS, -1)
        return self.things.remove(item)

    def removeItemWithId(self, itemId):
        for i in self.getItems():
            if i.itemId == itemId:
                self.removeItem(i)
                
    # Fase those calls out
    def removeClientItem(self, cid, stackpos=None):
        if stackpos and self.things[stackpos].cid == cid:
            return self.things.pop(stackpos)
        else:
            for x in self.bottomItems():
                if x.cid == cid:
                    self.things.remove(x)
                    break
    """
    def removeClientCreature(self, stackpos=None):
        if stackpos and self.things[stackpos]:
            self.creatureCount -= 1 << 4
            return self.things.pop(stackpos)  
            
    def placeClientItem(self, cid):
        import game.item
        item = game.item.Item(game.item.sid(cid))
        return self.placeItem(item)"""
        
    def getThing(self, stackpos):
        try:
            return self.things[stackpos]
        except:
            return None
    
    def setThing(self, stackpos, item):
        self.things[stackpos] = item
        
    def findItem(self, sid):
        for x in self.bottomItems():
            if x.itemId == sid:
                return x

    def findStackpos(self, thing):
        return self.things.index(thing)
        
    def findClientItem(self, cid, stackpos=None):
        for x in self.bottomItems():
            if x.cid == cid:
                if stackpos:
                    return (self.things.index(x), x)
                return x
                
    def findCreatureStackpos(self, creature):
        return self.things.index(creature)

    def __getstate__(self):
        return (self.things, self.countNflags)
    
    def __setstate__(self, saved):
        self.things = saved[0]
        self.countNflags = saved[1]
        
#bindconstant.bind_all(Tile) # Apply constanting to Tile  

class HouseTile(Tile):
    __slots__ = ('houseId', 'position')
    def __getstate__(self):
        
        # Remove all non-loaded things for the sake of the cache. 
        items = []
        cf = self.getFlags()
        for i in self.things:
            if i.fromMap:
                items.append(i)
                if i.ontop:
                    cf += 1
        
        return (items, cf, self.houseId, self.position)
    
    def __setstate__(self, saved):
        self.things = saved[0]      
        self.countNflags = saved[1]  
        self.houseId = saved[2]
        self.position = saved[3]
        
        if self.houseId in houseTiles:
            houseTiles[self.houseId].append(self)
        else:
            houseTiles[self.houseId] = [self]
        
        check = True    
        for i in self.things:
            if "houseDoor" in i.actions:
                if check and self.houseId in houseDoors:
                    houseDoors[self.houseId].append(self.position)
                    check = False
                else:
                    houseDoors[self.houseId] = [self.position]

        try:
            for item in game.house.houseData[self.houseId].data["items"][self.position]:
                self.placeItem(item)
        except KeyError:
            pass
    
#bindconstant.bind_all(HouseTile) # Apply constanting to HouseTile 

import data.map.info as mapInfo
dummyItems = {} 

knownMap = {}

houseTiles = {}

houseDoors = {}

# Ops codes
class S(object):
    __slots__ = ('base', 'radius')
    
    def __init__(self, x, y, z=None, radius=5): # z isn't used.
        self.base = (x,y) # Constant
        self.radius = radius
        
    def M(self, name,x,y,z=7, spawnTime=None):
        try:
            game.monster.getMonster(name).spawn([self.base[0]+x, self.base[1]+y, z], radius=self.radius, spawnTime=spawnTime, radiusTo=self.base)

        except:
            log.msg("Spawning of monster '%s' failed, it's likely that it doesn't exist, or you try to spawn it on solid tiles" % name)
                
        return self
        
        
    def N(self, name,x,y,z=7, spawnTime=None):
        try:
            game.npc.getNPC(name).spawn([self.base[0]+x, self.base[1]+y, z], radius=self.radius, spawnTime=spawnTime, radiusTo=self.base)

        except:
            log.msg("Spawning of NPC '%s' failed, it's likely that it doesn't exist, or you try to spawn it on solid tiles" % name)
            
        return self
        
bindconstant.bind_all(S)

def I(itemId, **kwargs):
    # Do not stack
    if not kwargs and config.stackItems:
        try:
            return dummyItems[itemId]
        except:
            item = Item(itemId)
            item.tileStacked = True
            item.fromMap = True
            dummyItems[itemId] = item

            return item
    else:
        item = Item(itemId, **kwargs)
        item.fromMap = True
        
        return item

R = I # TODO

def T(*args):
    return Tile(args, itemLen=len(args))

T = bindconstant._make_constants(T)

def Tf(flags, *args):
    return Tile(args, itemLen=len(args), flags=flags)

Tf = bindconstant._make_constants(Tf)

def H(houseId, position, *args):   
    tile = HouseTile(args, itemLen=len(args))
    tile.houseId = houseId
    tile.position = position # Never rely on this data.
    
    # Set protected zone
    tile.setFlag(game.enum.TILEFLAGS_PROTECTIONZONE)
        
    # Find and cache doors
    check = True
    for i in tile.getItems():
        if "houseDoor" in i.actions:
            if check and houseId in houseDoors:
                houseDoors[houseId].append(position)
                check = True
            else:
                houseDoors[houseId] = [position]
            
    
    if houseId in houseTiles:
        houseTiles[houseId].append(tile)
    else:
        houseTiles[houseId] = [tile]
        
    try:
        for item in game.house.houseData[houseId].data["items"][position]:
            tile.placeItem(item)
    except KeyError:
        pass

    return tile
    
def C(*args):
    if config.stackTiles:
        code = 0
        por = 0
        for item in tile.things:
            code += item.itemId << por
            por += 14
        if not code in dummyTiles:
            dummyTiles[code] = T(*args)
        return dummyTiles[code]
    else:
        return T(*args)
        
global V
V = None

if config.stackTiles:
    dummyTiles = {}
    
def loadTiles(x,y, walk=True):
    if x < 0 or y < 0:
        return None
    elif x > mapInfo.height or y > mapInfo.width:
        return None
    
    return load(int(x / mapInfo.sectorSize[0]), int(y / mapInfo.sectorSize[1]))

def load(sectorX, sectorY):
    sectorSum = (sectorX * 32768) + sectorY
    
    ybase = sectorY*mapInfo.sectorSize[1]
    xbase = sectorX*mapInfo.sectorSize[0]
    if sectorSum in knownMap or ybase > mapInfo.height-1 or xbase > mapInfo.width-1:
        return False

    global V # Should really be avioided 
    if not V:
        V = Tile((I(100),), 1)
          
    print "Loading %d,%d,sec" % (sectorX, sectorY)
    t = time.time()
    
    # Attempt to load a cached file
    # Comment out. Please find a way to also store the houseTiles data aswell.
    try:
        with io.open("data/map/%d.%d.sec.cache" % (sectorX, sectorY), "rb") as f:
            knownMap[sectorSum] = cPickle.loads(f.read())
    except:
        # Build cache data
        # Note: Cache is not rev independant, nor python independant. Don't send them instead of the .sec files
        with io.open("data/map/%d.%d.sec" % (sectorX, sectorY), 'rb') as f:
            knownMap[sectorSum] = eval(f.read(), {}, {"V":V, "C":C, "H":H, "Tf":Tf, "T":T, "I":I, "R":R})
        # Write it
        with io.open("data/map/%d.%d.sec.cache" % (sectorX, sectorY), 'wb') as f:
            f.write(game.engine.fastPickler(knownMap[sectorSum]))
            
    print "Loading took: %f" % (time.time() - t)
    
    if 'l' in knownMap[sectorSum]:    
        exec(knownMap[sectorSum]['l'], {}, {"S":S})
        
    if config.performSectorUnload:
        reactor.callLater(config.performSectorUnloadEvery, reactor.callInThread, _unloadMap, sectorX, sectorY)
    
    scriptsystem.get('postLoadSector').runSync("%d.%d" % (sectorX, sectorY), None, None, sector=knownMap[sectorSum])
    
    return True

# Map cleaner
def _unloadCheck(sectorX, sectorY):
    # Calculate the x->x and y->y ranges
    # We're using a little higher values here to avoid reloading again 
    
    xMin = (sectorX * mapInfo.sectorSize[0]) + 14
    xMax = (xMin + mapInfo.sectorSize[0]) + 14
    yMin = (sectorY * mapInfo.sectorSize[1]) + 11
    yMax = (yMin + mapInfo.sectorSize[1]) + 11
    
    for player in game.player.allPlayersObject:
        pos = player.position # Pre get this one for sake of speed, saves us a total of 4 operations per player
        
        # Two cases have to match, the player got to be within the field, or be able to see either end (x or y)
        if (pos[0] < xMax or pos[0] > xMin) and (pos[1] < yMax or pos[1] > yMin):
            return False # He can see us, cancel the unloading
            
    return True
    
def _unloadMap(sectorX, sectorY):
    print "Checking %d.%d.sec" % (sectorX, sectorY)
    t = time.time()
    if _unloadCheck(sectorX, sectorY):
        print "Unloading...."
        unload(sectorX, sectorY)
        print "Unloading took: %f" % (time.time() - t)   
        
def unload(sectorX, sectorY):
    sectorSum = (sectorX * 32768) + sectorY
    try:
        del knownMap[sectorSum]
    except:
        pass