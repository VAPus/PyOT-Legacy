from game.item import Item
import game.item
from twisted.internet import threads, reactor
from twisted.python import log
import bindconstant
import marshal
import scriptsystem
from collections import deque
import config
    
def getTile(pos):
    iX = int(pos[0] / 32)
    iY = int(pos[1] / 32)
    pX = pos[0] -iX * 32
    pY = pos[1] -iY * 32
    sectorSum = (iX * 32768) + iY
    try:
        return knownMap[sectorSum][pos[2]][pX][pY]
    except:
        loadTiles(pos[0], pos[1])
        try:
            return knownMap[sectorSum][pos[2]][pX][pY]
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

knownMap = {}
for i in xrange(data.map.info.levels[1], data.map.info.levels[0]):
    knownMap[i] = {}
sectors = []



# Ops codes
class S(object):
    __slots__ = ('base', 'radius')
    
    def __init__(self, x, y, z=None, radius=5): # z isn't used.
        self.base = (x,y) # Constant
        self.radius = radius
        
    def M(self, name,x,y,z=7, spawnTime=None):
        try:
            game.monster.getMonster(name).spawn([self.base[0]+x,self.base[1]+y,z], radius=self.radius, spawnTime=spawnTime, radiusTo=self.base)

        except:
            log.msg("Spawning of monster '%s' failed, it's likely that it doesn't exist, or you try to spawn it on solid tiles" % name)
                
        return self
        
        
    def N(self, name,x,y,z=7, spawnTime=None):
        try:
            game.npc.getNPC(name).spawn([self.base[0]+x,self.base[1]+y,z], radius=self.radius, spawnTime=spawnTime, radiusTo=self.base)

        except:
            log.msg("Spawning of NPC '%s' failed, it's likely that it doesn't exist, or you try to spawn it on solid tiles" % name)
            
        return self
        
bindconstant.bind_all(S)

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

R = I # TODO

def T(*args):
    return Tile(args, itemLen=len(args))

T = bindconstant._make_constants(T)

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
        T(*args)
        
global V
V = None

if config.stackTiles:
    dummyTiles = {}
    
def loadTiles(x,y, walk=True):
    if x < 0 or y < 0:
        return None
    elif x > data.map.info.height or y > data.map.info.width:
        return None
        
    sectorX = int(x / data.map.info.sectorSize[0])
    sectorY = int(y / data.map.info.sectorSize[1])
    
    load(sectorX, sectorY)

def __loadOp(code): exec(code)

def load(sectorX, sectorY):
    sectorSum = (sectorX * 32768) + sectorY
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
    m = None
    try:
        exec(marshal.loads(open("data/map/%d.%d.sec.cache" % (sectorX, sectorY), "rb").read()))
    except:
        # Build cache data
        # Note: Cache is not rev independant, nor python independant. Don't send them instead of the .sec files
        compiled = compile(open("data/map/%d.%d.sec" % (sectorX, sectorY), 'rb').read(), "%d.%d" % (sectorX, sectorY), 'exec')
        # Write it
        marshal.dump(compiled, open("data/map/%d.%d.sec.cache" % (sectorX, sectorY), 'wb'), 2)
        exec(compiled)
    
    if m:
        knownMap[sectorSum] = m          
            
    if l:    
        threads.deferToThread(__loadOp, l)
    
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
        if pos[0] < xMax and pos[0] > xMin and pos[1] < yMax and pos[1] > yMin:
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
    sectors.remove(sectorSum)