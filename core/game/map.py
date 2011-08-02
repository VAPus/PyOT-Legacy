from game.item import Item
import game.item
from twisted.internet import threads
from twisted.python import log
import bindconstant
import marshal
import scriptsystem

def getTile(pos):
    try:
        return knownMap[ pos[2] ][ pos[0] - (7-pos[2]) ][ pos[1] ]
    except:
        loadTiles(pos[0] - (7-pos[2]), pos[1])
        try:
            return knownMap[ pos[2] ][ pos[0] - (7-pos[2]) ][ pos[1] ]
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
    def __init__(self, items, topItemCount=0):
        if not topItemCount:
            workItems = items[:]
            self.things = [workItems.pop(0)]
            self.topItemCount = 1
            
            if workItems:
                bottomItems = []
                for item in workItems:
                    if item.ontop:
                        self.things.append(item)
                        self.topItemCount += 1
                    else:
                        bottomItems.append(item)
                        
                if bottomItems:
                    self.things.extend(bottomItems)
             
            if "solid" in game.item.items[self.things[0].itemId]:
                self.things = tuple(self.things)
            else:
                self.creatureCount = 0
        else:
             self.things = items
             self.topItemCount= topItemCount
             self.creatureCount = 0
             
    def placeCreature(self, creature):
        self.things.insert(self.topItemCount, creature)
        self.creatureCount += 1
        return self.topItemCount
        
    def removeCreature(self,creature):
        self.creatureCount -= 1
        return self.things.remove(creature)
        
    def placeItem(self, item):
        self.things.insert(self.topItemCount+self.creatureCount, item)
        return self.topItemCount+self.creatureCount
    
    def placeItemEnd(self, item):
        self.things.append(item)
        return len(self.things)-1
        
    def bottomItems(self):
        return self.things[self.topItemCount+self.creatureCount:]
        
    def topItems(self):
        return self.things[:self.topItemCount]

    def getItems(self):
        items = self.topItems()[:]
        items.extend(self.bottomItems())
        return items
    def creatures(self):
        return self.things[self.topItemCount:self.topItemCount+self.creatureCount]
        
    def removeItem(self, item):
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
            self.creatureCount -= 1
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

    def findClientItem(self, cid, stackpos=None):
        for x in self.bottomItems():
            if x.cid == cid:
                if stackpos:
                    return (self.things.index(x), x)
                return x
                
    def findCreatureStackpos(self, creature):
        return self.things.index(creature)
                
    def toSafe(self, position):
        for item in self.things:
            if not item.solid:
                return self # I am already safe
                
        tile = getTile(position)
        tile = Tile(self.things, self.topItemCount)
        return tile

bindconstant.bind_all(Tile) # Apply constanting to Tile

    
knownMap = {}
sectors = {}
callbacks = {}

import data.map.info
dummyItems = {} # Ground items etc

# Ops codes
def M(name,x,y,z=7):
    try:
        game.monster.getMonster(name).spawn([x,y,z])
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

def I(itemId, **kwargs):
    # Do not stack
    if not kwargs:
        try:
            return dummyItems[itemId]
        except:
            item = Item(itemId, **kwargs)
            
            itemX = game.scriptsystem.get('addMapItem').runSync(item, None, None, item, options={})

            if not itemX:
                dummyItems[item.itemId] = item
            else:
                return itemX
            return item
    else:
        item = Item(itemId, **kwargs)
        itemX = game.scriptsystem.get('addMapItem').runSync(item, None, None, item, options=kwargs)
        if itemX:
            return itemX
        return item
    
def T(*args):
    return Tile(list(args))

T = bindconstant._make_constants(T)

global V
V = None
        
def loadTiles(x,y, walk=True):
    if x > data.map.info.height or y > data.map.info.width:
        return None
        
    sectorX = int(x / data.map.info.sectorSize[0])
    sectorY = int(y / data.map.info.sectorSize[1])
    
    load(sectorX, sectorY)
    
def load(sectorX, sectorY):
    global V # Should really be avioided
    
    if sectorX in sectors and sectorY in sectors[sectorX] or (sectorX*data.map.info.sectorSize[0] > data.map.info.height-1 or sectorY*data.map.info.sectorSize[1] > data.map.info.width-1):
        return False
        
    if not sectorX in sectors:
        sectors[sectorX] = {}
        
    sectors[sectorX][sectorY] = True

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
    
    currZ = None
    currX = None
    localItems = game.item.items # Prevent a bit of a lookup
    for z in m:
        xPos = (sectorX*32)
        try:
            currZ = knownMap[z]
        except:
            knownMap[z] = {}
            currZ = knownMap[z]
            
        for x in m[z]:
            yPos = sectorY*32
            try:
                currX = currZ[xPos]
            except:
                currZ[xPos] = {}
                currX = currZ[xPos]
                
            for tile in x:
                if tile:
                    if "solid" in localItems[tile.things[0].itemId]:
                        currX[yPos] = tile
                    else:
                        currX[yPos] = Tile(tile.things[:], tile.topItemCount)
                    
                yPos += 1    
            
            xPos += 1
    
    if l:    
        threads.deferToThread(l)
        
    # Do callbacks
    m = "%s%s" % (str(sectorX).zfill(3),str(sectorY).zfill(3))
    if m in callbacks:
        for func in callbacks[m]:
            func()

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
    