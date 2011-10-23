from game.item import Item
import game.item
from twisted.internet import threads, reactor
from twisted.python import log
import bindconstant
import marshal
import scriptsystem
from collections import deque
import config

try:
    import io # Python 2.7+
    _open = io.open
except:
    _open = open # Less than 2.7
    
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
        return housePositions[(pos[0], pos[1], pos[2])]
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
            self.things = items
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
        
bindconstant.bind_all(Tile) # Apply constanting to Tile  

class HouseTile(Tile):
    __slots__ = 'houseId'
    
bindconstant.bind_all(HouseTile) # Apply constanting to HouseTile 

import data.map.info
dummyItems = {} 

knownMap = {}

houseTiles = {}

housePositions = {}

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
            item = Item(itemId, **kwargs)
            
            itemX = scriptsystem.get('addMapItem').runSync(item, None, None, options={})

            if not itemX:
                item.tileStacked = True
                item.fromMap = True
                dummyItems[itemId] = item
            else:
                itemX.fromMap = True
                return itemX
            return item
    else:
        item = Item(itemId, **kwargs)
        itemX = scriptsystem.get('addMapItem').runSync(item, None, None, options=kwargs)
        if itemX:
            itemX.fromMap = True
            return itemX
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
    import game.engine as g
        
    tile = HouseTile(args, itemLen=len(args))
    tile.houseId = houseId
    try:
        houseTiles[houseId].append((tile, position))
        housePositions[position] = houseId
    except:
        houseTiles[houseId] = [(tile, position)]
        housePositions[position] = houseId
    try:
        for item in g.savedItems[position]:
            tile.placeItem(item)
    except:
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
    elif x > data.map.info.height or y > data.map.info.width:
        return None
    
    return load(int(x / data.map.info.sectorSize[0]), int(y / data.map.info.sectorSize[1]))

def load(sectorX, sectorY):
    sectorSum = (sectorX * 32768) + sectorY
    
    ybase = sectorY*data.map.info.sectorSize[1]
    xbase = sectorX*data.map.info.sectorSize[0]
    if sectorSum in knownMap or ybase > data.map.info.height-1 or xbase > data.map.info.width-1:
        return False

    global V # Should really be avioided 
    if not V:
        V = Tile((I(100),), 1)
          
    print "Loading %d,%d,sec" % (sectorX, sectorY)
    
    # Attempt to load a cached file
    l = None
    m = None
    try:
        with _open("data/map/%d.%d.sec.cache" % (sectorX, sectorY), "rb") as f:
            exec marshal.loads(f.read())
    except:
        # Build cache data
        # Note: Cache is not rev independant, nor python independant. Don't send them instead of the .sec files
        with _open("data/map/%d.%d.sec" % (sectorX, sectorY), 'rb') as f:
            compiled = compile(f.read(), "%d.%d" % (sectorX, sectorY), 'exec')
        # Write it
        with _open("data/map/%d.%d.sec.cache" % (sectorX, sectorY), 'wb') as f:
            f.write(marshal.dumps(compiled, 2))
        exec compiled
    

    knownMap[sectorSum] = m          
        
    if l:    
        reactor.callInThread(l)
    
    if config.performSectorUnload:
        reactor.callLater(config.performSectorUnloadEvery, reactor.callInThread, _unloadMap, sectorX, sectorY)
        
    return True

# Map cleaner
def _unloadCheck(sectorX, sectorY):
    # Calculate the x->x and y->y ranges
    # We're using a little higher values here to avoid reloading again 
    import game.player
    
    xMin = (sectorX * data.map.info.sectorSize[0]) + 14
    xMax = (xMin + data.map.info.sectorSize[0]) + 14
    yMin = (sectorY * data.map.info.sectorSize[1]) + 11
    yMax = (yMin + data.map.info.sectorSize[1]) + 11
    
    for player in game.player.allPlayersObject:
        pos = player.position # Pre get this one for sake of speed, saves us a total of 4 operations per player
        
        # Two cases have to match, the player got to be within the field, or be able to see either end (x or y)
        if (pos[0] < xMax or pos[0] > xMin) and (pos[1] < yMax or pos[1] > yMin):
            return False # He can see us, cancel the unloading
            
    return True
    
def _unloadMap(sectorX, sectorY):
    import time
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