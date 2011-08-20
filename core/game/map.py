from game.item import Item
import game.item
from twisted.internet import threads
from twisted.python import log
import bindconstant
import marshal
import scriptsystem
from collections import deque
import config

PACKSIZE = 0

def ZPack(level, x, y):
    return level + (x << 4) + (y << PACKSIZE)
    
def getTile(pos):
    try:
        t = knownMap[ ZPack(pos[2], pos[0], pos[1]) ]
        if t:
            return t
        else:
            raise
    except:
        loadTiles(pos[0], pos[1])
        try:
            return knownMap[ ZPack(pos[2], pos[0], pos[1]) ]
        except:
            return None
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

class Tile(object):
    __slots__ = ('things', 'itemCount')
    def __init__(self, items, topItemCount=0, itemLen=0):
        if not topItemCount:
            self.itemCount = 1
            
            if itemLen == 1:
                self.things = (items[0],) if game.item.items[items[0].itemId]["a"] & 1 else [items[0]]
            else:
                workItems = deque(items)
                self.things = [workItems.popleft()]
                
                
                if workItems:
                    bottomItems = []
                    for item in workItems:
                        if item.ontop:
                            self.things.append(item)
                            self.itemCount += 1
                        else:
                            bottomItems.append(item)
                            
                    if bottomItems:
                        self.things.extend(bottomItems)
  
        else:
            self.things = items
            self.itemCount = topItemCount
             
    def placeCreature(self, creature):
        pos = (self.itemCount >> 4) + self.itemCount & 0x0F
        if pos > 9:
            return
  
        self.things.insert(pos, creature)
        self.itemCount += 1 << 4

        return pos
        
    def removeCreature(self,creature):
        self.itemCount -= 1 << 4
        return self.things.remove(creature)
        
    def placeItem(self, item):
        if item.ontop:
            pos = self.itemCount & 0x4F
            self.itemCount += 1
        else:
            pos = (self.itemCount >> 4) + self.itemCount & 0x0F
        self.things.insert(pos, item)
        return pos
    
    def placeItemEnd(self, item):
        self.things.append(item)
        return len(self.things)-1

    def ground(self):
        return self.things[0]
        
    def bottomItems(self):
        return self.things[(self.itemCount >> 4) + self.itemCount & 0x0F:]
        
    def topItems(self):
        return self.things[:self.itemCount & 0x0F]

    def getItems(self):
        items = self.topItems()[:]
        try:
            items.extend(self.bottomItems())
        except:
            pass
        return items
    def creatures(self):
        return self.things[self.itemCount & 0x0F:(self.itemCount >> 4) + self.itemCount & 0x0F]
        
    def removeItem(self, item):
        if item.ontop:
            self.itemCount -= 1
        return self.things.remove(item)
        
    def removeClientItem(self, cid, stackpos=None):
        if stackpos and self.things[stackpos].cid == cid:
            return self.things.pop(stackpos)
        else:
            for x in self.bottomItems():
                if x.cid == cid:
                    self.things.remove(x)
                    break
    
    def removeClientCreature(self, stackpos=None):
        if stackpos and self.things[stackpos]:
            self.creatureCount -= 1 << 4
            return self.things.pop(stackpos)  
            
    def placeClientItem(self, cid):
        import game.item
        item = game.item.Item(game.item.sid(cid))
        return self.placeItem(item)
        
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

import data.map.info
dummyItems = {} 

while True:
    if data.map.info.height > 2**PACKSIZE:
        PACKSIZE += 1
        
    else:
        break
PACKSIZE += 4        
"""if config.useNumpy:
    from numpy import empty
    knownMap = empty((data.map.info.levels[0],data.map.info.width,data.map.info.height), dtype=Tile)
    
else:"""
knownMap = {}
sectors = []



# Ops codes
def M(name,x,y,z=7, spawnTime=None):
    try:
        game.monster.getMonster(name).spawn([x,y,z], spawnTime=spawnTime)

    except:
        log.msg("Spawning of monster '%s' failed, it's likely that it doesn't exist, or you try to spawn it on solid tiles" % name)
    
M = bindconstant._make_constants(M)

def MM(name, *argc):
    try:
        z = 7
        length = len(argc)
        if length % 2:
            z = argc[-1]
                
        for count in xrange(0,length, 2):
            game.monster.getMonster(name).spawn([argc[count],argc[count+1],z])

    except:
        log.msg("Spawning of monster '%s' failed, it's likely that it doesn't exist, or you try to spawn it on solid tiles" % name)

MM = bindconstant._make_constants(MM)

def N(name,x,y,z=7, spawnTime=None):
    try:
        game.npc.getNPC(name).spawn([x,y,z], spawnTime=spawnTime)

    except:
        log.msg("Spawning of NPC '%s' failed, it's likely that it doesn't exist, or you try to spawn it on solid tiles" % name)
    
N = bindconstant._make_constants(N)

def I(itemId, **kwargs):
    # Do not stack
    if not kwargs:
        try:
            return dummyItems[itemId]
        except:
            item = Item(itemId, **kwargs)
            
            itemX = scriptsystem.get('addMapItem').runSync(item, None, None, options={})

            if not itemX:
                dummyItems[itemId] = item
            else:
                return itemX
            return item
    else:
        item = Item(itemId, **kwargs)
        itemX = scriptsystem.get('addMapItem').runSync(item, None, None, options=kwargs)
        if itemX:
            return itemX
        return item
    
def T(*args):
    return Tile(args, itemLen=len(args))

T = bindconstant._make_constants(T)

global V
V = None

if config.stackTiles:
    dummyTiles = {}
def loadTiles(x,y, walk=True):
    if x < 0 or y < 0:
        print "Hmm"
        return None
    elif x > data.map.info.height or y > data.map.info.width:
        print "Hmm2"
        return None
        
    sectorX = int(x / data.map.info.sectorSize[0])
    sectorY = int(y / data.map.info.sectorSize[1])
    
    load(sectorX, sectorY)
    
def load(sectorX, sectorY):
    sectorSum = (sectorX << 15) + sectorY
    ybase = sectorY*data.map.info.sectorSize[1]
    xbase = sectorX*data.map.info.sectorSize[0]
    if sectorSum in sectors or (ybase > data.map.info.height-1 or xbase > data.map.info.width-1):
        return False
        
       
    sectors.append(sectorSum)
    global V # Should really be avioided 
    if not V:
        V = Tile((I(100),), 1)
          
    
    # Attempt to load a cached file
    l = None
    try:
        exec(marshal.loads(open("data/map/%d.%d.sec.cache" % (sectorX, sectorY), "rb").read()))
    except:
        # Build cache data
        # Note: Cache is not rev independant, nor python independant. Don't send them instead of the .sec files
        compiled = compile(open("data/map/%d.%d.sec" % (sectorX, sectorY), 'rb').read(), "%d.%d" % (sectorX, sectorY), 'exec')
        # Write it
        marshal.dump(compiled, open("data/map/%d.%d.sec.cache" % (sectorX, sectorY), 'wb'), 2)
        exec(compiled)
    
    localItems = game.item.items # Prevent a bit of a lookup
    for mz in m:
        currZ = mz[0]

        for i,x in enumerate(mz[1]):
            var = currZ + ((i+xbase) << 4)
            for y,tile in enumerate(x):
                if tile:
                    zpacked = var + ((y+ybase) << PACKSIZE)
                        
                    if localItems[tile.things[0].itemId]["a"] & 1:
                        if config.stackTiles:
                            code = 0
                            por = 0
                            for item in tile.things:
                                code += item.itemId << por
                                por += 14
                            if not code in dummyTiles:
                                dummyTiles[code] = tile
                            knownMap[zpacked] = dummyTiles[code]
                        else:
                            knownMap[zpacked] = tile
                    else:
                        knownMap[zpacked] = Tile(tile.things[:], tile.itemCount)                  
            

    if l:    
        threads.deferToThread(l)
        
    # Do callbacks
    """m = "%s%s" % (str(sectorX).zfill(3),str(sectorY).zfill(3))
    if m in callbacks:
        for func in callbacks[m]:
            func()"""

    return True
def unload(sectorX, sectorY):
    for x in xrange(sectorX * 64, (sectorX * 64) + 64):
        for x in xrange(sectorY * 64, (sectorY * 64) + 64):
            del knownMap[x][y]
    
def regPostLoadSector(x,y,callback):
    m = str(x).zfill(3)+str(y).zfill(3)
    if not m in callbacks:
        callbacks[m] = []
    callbacks[m].append(callback)
    