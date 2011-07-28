import game.item
from twisted.internet import reactor
from twisted.python import log
import time
import platform

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
    def __init__(self, items):
        workItems = items[:]
        self.things = [workItems.pop(0)]
        self.topItemCount = 1
        self.creatureCount = 0
        
        if workItems:
            for item in workItems:
                if item.ontop:
                    self.things.append(item)
                    self.topItemCount += 1
                    workItems.remove(item)
        
        if workItems:
            self.things.extend(workItems)

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
                
    def topCopy(self):
        # Could only be called under load or on pure static ground items, this WILL bug all kinds of tiles with creatures and bottomitems
        # This approch is twice as fast as copy.copy is, might use more memory tho since it won't guaranty that self.*Count is a reference on creation
        # TODO, deal with stacking on entierly solid objects, multilayer
        
        # This might bug, disable GM walks (in current code)
        # Notice: If a GM deside to walk on solids, then recreate the entier Tile, take the normal way, teleport, or suffer insane memory usage!
        if self.things[0].solid: # Only check lowest ground, we need to do a loop on this one!
            return self # Reference, or own kind of auto tile stack, very very unsafe
        return Tile(self.things[:])
        
knownMap = {}
sectors = {}
callbacks = {}

import data.map.info
dummyTiles = {} # solid items like mountains will stay here
dummyItems = {} # Ground items etc

def loadTiles(x,y, walk=True):
    if x > data.map.info.height or y > data.map.info.width:
        return None
        
    sectorX = int(x / data.map.info.sectorSize[0])
    sectorY = int(y / data.map.info.sectorSize[1])
    
    load(sectorX, sectorY)
    
def load(sectorX, sectorY):

    if sectorX < 0 or sectorY < 0 or (sectorX in sectors and sectorY in sectors[sectorX]):
        return None

    if sectorX*data.map.info.sectorSize[0] > data.map.info.height-1 or sectorY*data.map.info.sectorSize[1] > data.map.info.width-1:
        return None
        
    if not sectorX in sectors:
        sectors[sectorX] = {}
        
    sectors[sectorX][sectorY] = True
    

    # Ops codes
    def M(name,x,y,z=7):
        try:
            game.monster.getMonster(name).spawn([x,y,z])
        except:
            log.msg("Spawning of monster '%s' failed, it's likely that it doesn't exist, or you try to spawn it on solid tiles" % name)
    
    def MM(name, *argc):
        try:
            z = 7
            if len(argc) % 2:
                z = argc[-1]
                
            for count in xrange(0,len(argc), 2):
                game.monster.getMonster(name).spawn([argc[count],argc[count+1],z])
        except:
            log.msg("Spawning of monster '%s' failed, it's likely that it doesn't exist, or you try to spawn it on solid tiles" % name)
            
    def I(itemId, **kwargs):
        try:
            return dummyItems[itemId]
        except:
            dummyItems[itemId] = game.item.Item(itemId, **kwargs)
            return dummyItems[itemId]

    def T(*args, **kwargs):
        try:
            if args[0].solid:
                return dummyTiles[args[0].itemId]
            return Tile(list(args), **kwargs)
        except:
            dummyTiles[args[0].itemId] = Tile(list(args), **kwargs)
        return dummyTiles[args[0].itemId]
    
    if platform.system() == "Windows":
        begin = time.clock()
        timer = time.clock
    else:
        timer = time.time
        begin = time.time()
    
    try:
        V = dummyTiles[100] 
    except:
        dummyTiles[100] = T(I(100))
        dummyTiles[100].static = True
        V = dummyTiles[100] 
        
    dd = {}
    execfile("data/map/%d.%d.sec" % (sectorX, sectorY), locals(), dd)
    
    currZ = None
    currX = None
    for z in dd["m"]:
        xPos = (sectorX*32)
        yPos = (sectorY*32)  
        try:
            currZ = knownMap[z]
        except:
            knownMap[z] = {}
            currZ = knownMap[z]
            
        for x in dd["m"][z]:
            try:
                currX = currZ[xPos]
            except:
                currZ[xPos] = {}
                currX = currZ[xPos]
                
            for tile in x:
                if tile:
                    currX[yPos] = tile.topCopy()
                else:
                    currX[yPos] = None
                    
                yPos += 1    
            yPos = sectorY*32
            xPos += 1
    
    print "Loading %d.%d took %f" % (sectorX, sectorY, timer() - begin)
    if "l" in dd:    
        reactor.callInThread(dd["l"])
        
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
    