from core.game.item import BaseThing
from twisted.internet import threads
import cjson, zlib, threading

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
    def __init__(self, items, bottomItems = []):
        self.things = items
        self.topItemCount = len(items)
        self.creatureCount = 0
        self.bottomItemCount = len(bottomItems)
        self.things.extend(bottomItems)

    def placeCreature(self, creature):
        self.things.insert(self.topItemCount+self.creatureCount, creature)
        self.creatureCount += 1
    
    def removeCreature(self,creature):
        self.creatureCount -= 1
        return self.things.remove(creature) # return stackpos
        
    def placeItem(self, item):
        self.bottomItemCount += 1
        self.things.append(item)
        return len(self.things)-1
        
    def bottomItems(self):
        return self.things[self.topItemCount+self.creatureCount:]
        
    def topItems(self):
        return self.things[:self.topItemCount]
        
    def creatures(self):
        return self.things[self.topItemCount:self.topItemCount+self.creatureCount]
    def removeItem(self, item):
        self.bottomItemCount -= 1
        return self.things.remove(item) # return stackpos
        
    def removeClientItem(self, cid, stackpos=None):
        import core.game.item
        sid = core.game.item.reverseItems[cid]
        if stackpos and self.things[stackpos] is sid:
            self.bottomItemCount -= 1
            return self.things.pop(stackpos)
            
        else:
            self.bottomItemCount -= 1
            return self.items.remove(sid)
            
    def placeClientItem(self, cid):
        import core.game.item
        sid = core.game.item.reverseItems[cid]
        return self.placeItem(sid)

    
knownMap = {}
sectors = {}

import data.map.info

def loadTiles(x,y, walk=True):
    if x > data.map.info.height or y > data.map.info.width:
        return None
        
    sectorX = int(x / data.map.info.sectorSize[0])
    sectorY = int(y / data.map.info.sectorSize[1])
    
    # An idea by soul4soul. To be better implanted into walk sections really
    if walk:
        commands = [(load, [sectorX+1, sectorY], {})]
        commands.append((load, [sectorX-1, sectorY], {}))
        commands.append((load, [sectorX, sectorY+1], {}))
        commands.append((load, [sectorX, sectorY-1], {}))
        commands.append((load, [sectorX-1, sectorY-1], {}))
        commands.append((load, [sectorX+1, sectorY+1], {}))
        commands.append((load, [sectorX-1, sectorY+1], {}))
        commands.append((load, [sectorX+1, sectorY-1], {}))
    # This locks walking until it's done if it isn't already loaded, which is should be!
    load(sectorX, sectorY)
    # Perform the loading in threadpool, this hold one thread
    if walk:
        threads.callMultipleInThread(commands)
    
def load(sectorX, sectorY):
    if sectorX < 0 or sectorY < 0 or (sectorX in sectors and sectorY in sectors[sectorX]):
        return None

    if sectorX*data.map.info.sectorSize[0] > data.map.info.height or sectorY*data.map.info.sectorSize[1] > data.map.info.width:
        return None
        
    if not sectorX in sectors:
        sectors[sectorX] = {}
        
    sectors[sectorX][sectorY] = True
    
    mapy = cjson.decode(zlib.decompress(open("data/map/map_%d_%d.sec" % (sectorX, sectorY), "rb").read()))
    
    for xx in mapy:
        x = int(xx)
        if not x in knownMap:
            knownMap[x] = {}
        for yy in mapy[xx]:
            y = int(yy)
            if not y in knownMap[x]:
                knownMap[x][y] = {}
            for zz in mapy[xx][yy]:
                z = int(zz)
                knownMap[x][y][z] = Tile(mapy[xx][yy][zz][0])

def unload(sectorX, sectorY):
    for x in range(sectorX * 64, (sectorX * 64) + 64):
        for x in range(sectorY * 64, (sectorY * 64) + 64):
            del knownMap[x][y]
    
