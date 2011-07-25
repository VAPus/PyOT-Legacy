from game.item import BaseThing
import game.item
import time

def getTile(pos):
    try:
        return knownMap[ pos[0] ][ pos[1] ][ pos[2] ]
    except:
        loadTiles(pos[0], pos[1])
        try:
            return knownMap[ pos[0] ][ pos[1] ][ pos[2] ]
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

class Tile(BaseThing):
    def __init__(self, items):
        self.things = items
        self.topItemCount = len(items)
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
                
    
knownMap = {}
sectors = {}
callbacks = {}

import data.map.info
dummyTiles = {} # solid items like mountains will stay here
dummyItems = {} # Ground items etc

def loadTiles(x,y, walk=False):
    if x > data.map.info.height or y > data.map.info.width:
        return None
        
    sectorX = int(x / data.map.info.sectorSize[0])
    sectorY = int(y / data.map.info.sectorSize[1])
    
    # An idea by soul4soul. To be better implanted into walk sections really
    """if walk:
        commands = [(load, [sectorX+1, sectorY], {})]
        commands.append((load, [sectorX-1, sectorY], {}))
        commands.append((load, [sectorX, sectorY+1], {}))
        commands.append((load, [sectorX, sectorY-1], {}))
        commands.append((load, [sectorX-1, sectorY-1], {}))
        commands.append((load, [sectorX+1, sectorY+1], {}))
        commands.append((load, [sectorX-1, sectorY+1], {}))
        commands.append((load, [sectorX+1, sectorY-1], {}))"""
    # This locks walking until it's done if it isn't already loaded, which is should be!
    load(sectorX, sectorY)
    # Perform the loading in threadpool, this hold one thread
    """if walk:
        threads.callMultipleInThread(commands)"""
    
def load(sectorX, sectorY):

    if sectorX < 0 or sectorY < 0 or (sectorX in sectors and sectorY in sectors[sectorX]):
        return None

    if sectorX*data.map.info.sectorSize[0] > data.map.info.height-1 or sectorY*data.map.info.sectorSize[1] > data.map.info.width-1:
        return None
        
    if not sectorX in sectors:
        sectors[sectorX] = {}
        
    sectors[sectorX][sectorY] = True
    
    begin = time.time() 
    
    # Ops codes
    def M(name,x,y,z=7):
        game.monster.getMonster(name).spawn([x,y,z])
    
    def I(itemId):
        global dummyItems
        if not itemId in dummyItems:
            dummyItems[itemId] = game.item.Item(itemId)
        return dummyItems[itemId]

    dd = {}
    N = None # Shortform
    execfile("data/map/map_%d_%d.sec" % (sectorX, sectorY), locals(), dd)
    _map_ = dd["m"]
    
    xPos = (sectorX*32)
    yPos = (sectorY*32)
    
    for x in _map_:
        if not xPos in knownMap:
            knownMap[xPos] = {}
        for y in x:
            if not yPos in knownMap[xPos]:
                knownMap[xPos][yPos] = {}

            for z in y:
                knownMap[xPos][yPos][z] = Tile(y[z][:])
            yPos += 1    
        yPos = sectorY*32
        xPos += 1

    print "Loading took: %f to load sector %d_%d" % (time.time() - begin, sectorX, sectorY)
    # Do callbacks
    m = str(sectorX).zfill(3)+str(sectorY).zfill(3)
    if m in callbacks:
        for func in callbacks[m]:
            func()

def unload(sectorX, sectorY):
    for x in xrange(sectorX * 64, (sectorX * 64) + 64):
        for x in xrange(sectorY * 64, (sectorY * 64) + 64):
            del knownMap[x][y]
    
def regPostLoadSector(x,y,callback):
    m = str(x).zfill(3)+str(y).zfill(3)
    if not m in callbacks:
        callbacks[m] = []
    callbacks[m].append(callback)
    