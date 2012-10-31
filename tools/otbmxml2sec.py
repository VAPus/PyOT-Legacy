#!/usr/bin/env python
# -*- coding: latin-1 -*-

from struct import unpack, unpack_from, Struct
import sys
import gc
import io

# Python 3
try:
    xrange()
except:
    xrange = range
    
# The reader class:
class Reader(object):
    __slots__ = ('pos', 'data')
    def __init__(self, data):
        self.pos = 0
        self.data = data

    # 8bit - 1byte, C type: char
    def uint8(self):
        self.pos += 1
        return ord(self.data[self.pos-1])
        
    def peekUint8(self):
        try:
            return ord(self.data[self.pos])
        except:
            return None
    def int8(self, format=Struct("<b")):
        self.pos += 1
        return format.unpack(self.data[self.pos-1:self.pos])[0]

    # 16bit - 2bytes, C type: short
    def uint16(self, format=Struct("<H")):
        self.pos += 2
        return format.unpack(self.data[self.pos-2:self.pos])[0]
    def int16(self, format=Struct("<h")):
        self.pos += 2
        return format.unpack(self.data[self.pos-2:self.pos])[0]

    # 32bit - 4bytes, C type: int
    def uint32(self, format=Struct("<I")):
        self.pos += 4
        return format.unpack(self.data[self.pos-4:self.pos])[0]
    def int32(self, format=Struct("<i")):
        self.pos += 4
        return format.unpack(self.data[self.pos-4:self.pos])[0]

    # 64bit - 8bytes, C type: long long
    def uint64(self):
        self.pos += 8
        return unpack("<Q", self.data[self.pos-8:self.pos])[0]
    def int64(self):
        self.pos += 8
        return unpack("<q", self.data[self.pos-8:self.pos])[0]

    # 32bit - 4bytes, C type: float
    def float(self):
        self.pos += 4
        return unpack("<f", self.data[self.pos-4:self.pos])[0]

    # 64bit - 8bytes, C type: double
    def double(self):
        self.pos += 8
        return unpack("<d", self.data[self.pos-8:self.pos])[0]

    def string(self):
        length = self.uint16()
        self.pos += length
        return ''.join(map(str, unpack("%ds" % length, self.data[self.pos-length:self.pos])))

    def getX(self, size):
        self.pos += size
        return ''.join(map(str, unpack_from("B"*size, self.data, self.pos - size)))

    def getXString(self, size):
        self.pos += size
        return ''.join(map(str, unpack("%ds" % size, self.data[self.pos-size:self.pos])))
        
    def getData(self):
        return self.data[self.pos:]

    def getChild(self):
        if self.peekUint8() == 0xFE:
            self.pos += 1
            return self
        else:
            return None

    def next(self):
        assert self.uint8() == 0xFF
        return self.getChild()

dummyItems = {}
dummyTiles = {}
def genItem(itemid):
    if not itemid in dummyItems:
        dummyItems[itemid] = Item(itemid)
    return dummyItems[itemid]

try:
    with io.open("map.otbm", 'rb') as otbmFile:
        data = otbmFile.read()
except:
    import glob
    with io.open(glob.glob("*.otbm")[0], 'rb') as otbmFile:
        data = otbmFile.read()

nData = []
nextEscape = False
for byte in data:
    if ord(byte) == 0xFD:
        if not nextEscape:
            nextEscape = True
            continue
    nData.append(byte)
    nextEscape = False

data = ''.join(nData)
del nData

otbm = Reader(data)
otbm.pos += 6

version = otbm.uint32()

assert version == 2

width = otbm.uint16()
height = otbm.uint16()
majorVersionItems = otbm.uint32()
minorVersionItems = otbm.uint32()

# Tiles
tiles = (width * height) / 4 # This also count null tiles which we doesn't pass, bad

print("OTBM v%d, %dx%d" % (version, width, height)) 

from generator import Map, Item, Tile, Spawn
print ("--Generating the map layout with no filling")
m = Map(width,height,None,15)
at = m.addTo
a = m.add

print ("--Done generating the map layout")

# Prepopulate map with a ground level of voids
nodes = otbm.getChild()
nodes.pos += 1
description = ""
spawns = ""
houses = ""

m.author("OTBMXML2sec generator")
print ("--Begin parsing description, spawns, and houses")

while nodes.peekUint8() < 0xFE:
    attr = nodes.uint8()

    if attr == 2: continue # ???
    if attr == 1:
        description += otbm.string()+"\n"
        
    elif attr == 11:
        spawns = nodes.string()
        print("--Using spawns: %s" % spawns)
    elif attr == 13:
        houses = nodes.string()
        print("--Using houses: %s" % houses)
    else:
        print otbm.pos
        print("Unknown nodes data %s" % hex(attr))
        sys.exit()

m.description(description)
print (description)
onTile = 0
lastPrint = 0
print("--Begin OTBM nodes")
MAX_X = 0
MAX_Y = 0
MAX_Z = 0
dontNextTile = False # A hack for weird maps.
node = nodes.getChild()
while node:
    type = node.uint8()
    if type == 4: # Tile area
        baseX = node.uint16()
        baseY = node.uint16()
        baseZ = node.uint8()
        
        tile = node.getChild()     
        while tile:
            tileType = tile.uint8()
            if tileType == 5 or tileType == 14: # Tile
                tileX = tile.uint8() + baseX
                tileY = tile.uint8() + baseY
                assert tileX <= width
                assert tileY <= height
                houseId = 0
                if tileType == 14:
                    houseId = tile.uint32()
                _render_ = False
                _itemG_ = None
                flags = 0
                
                # Attributes
                while tile.peekUint8() < 0xFE:
                    attr = tile.uint8()
                    if attr == 3: # OTBM_ATTR_TILE_FLAGS
                        flags = tile.uint32()
                        
                    elif attr == 9: # ITEM, ground item
                        _itemG_ = genItem(tile.uint16())
                        _render_ = True
                    else:
                        print("Unknown tile attribute %s" % hex(attr))
                        sys.exit()

                item = tile.getChild()                                   
                if not item and _itemG_:
                    try:
                        _tile_ = dummyTiles[_itemG_]
                    except:
                        dummyTiles[_itemG_] = [_itemG_]
                        _tile_ = dummyTiles[_itemG_]
                else:
                    _tile_ = []
                    if _itemG_:
                        _tile_.append(_itemG_)
                
                while item:
                    innerAttr = otbm.uint8()
                    if innerAttr == 6: # more items
                        itemId = otbm.uint16()
                        peak = otbm.peekUint8()
                                                
                        if peak >= 0xFE:
                            currItem = genItem(itemId)
                        else:
                            currItem=Item(itemId)
                        
                        # Unserialie attributes
                        while otbm.peekUint8() < 0xFE:                            
                            attr = otbm.uint8()
                                                       
                            if attr == 10: # depotId
                                currItem.attribute("depotId",otbm.uint16())
                                safe = False
                            elif attr == 14: # houseDoorId
                                safe = False
                                currItem.attribute("doorId",otbm.uint8())
                                
                                currItem.action('houseDoor')
                            elif attr == 20: # Sleeperguid
                                otbm.uint32() # TODO: care?
                            elif attr == 21: # sleepstart
                                otbm.uint32()
                            elif attr == 8: # Teleport destination
                                safe = False
                                currItem.attribute("teledest",[otbm.uint16(),otbm.uint16(),otbm.uint8()])
                            elif attr == 15: # Item count
                                safe = False
                                currItem.attribute("count",otbm.uint8())
                            elif attr == 4: # action id
                                safe = False
                                currItem.action(str(otbm.uint16()))
                            elif attr == 5:
                                safe = False
                                currItem.action(str(otbm.uint16() + 0xFFFF))
                            elif attr == 6:
                                safe = False
                                currItem.attribute("text",otbm.string())
                            elif attr == 18:
                                safe = False
                                currItem.attribute("written",otbm.uint32())
                            elif attr == 19:
                                safe = False
                                currItem.attribute("writtenBy",otbm.string())
                            elif attr == 7:
                                safe = False
                                currItem.attribute("description",otbm.string())
                            elif attr == 12:
                                currItem.attribute("count", otbm.uint8())
                            elif attr == 22:
                                safe = False
                                currItem.attribute("charges",otbm.uint8())
                            elif attr == 16:
                                duration = otbm.uint32()
                                print("duration = %d" % duration)
                            elif attr == 17:
                                decayState = otbm.uint8()
                                print("TODO: decaystate = %d on %d" % (decayState, itemId))

                            elif attr == 30:
                                currItem.attribute("name", otbm.string())

                            elif attr == 31:
                                otbm.string() # This is auto from name.

                            elif attr == 33:
                                currItem.attribute("attack", otbm.uint32())


                            elif attr == 23:
                                print "Warning, it's broken :("
                                sys.exit()
                                otbm.uint32()
                                break # All after this is container items

                            elif attr == 41:
                                otbm.string() # Auto.
                            
                            else:
                                print otbm.pos
                                print("Unknown item attribute %d, %d, %d" % (attr, otbm.uint8(), otbm.uint16()))
                                sys.exit()
                        _render_ = True
                        
                        _tile_.append(currItem)
                        
                    else:
                        print otbm.pos
                        print("Unknown item header %s" % (hex(innerAttr)))
                        sys.exit()
                    try:
                        item = tile.next()
                    except:
                        otbm.pos -= 1
                        if not otbm.uint8() == 0xFE:
                            raise
                        # HACK 
                        #otbm.pos -= 5
                        otbm.pos += 4
                        #dontNextTile = True
                        break
            else:
                print otbm.pos
                print("Unknown tile node %s" % hex(tileType))

            if _render_:
                at(tileX,tileY,_tile_, baseZ)
                
                if houseId:
                    m.houses[(tileX, tileY, baseZ)]=houseId
                if flags:
                    m.flags[(tileX, tileY, baseZ)]=flags
            onTile += 1
            if onTile - lastPrint == 2000:
                lastPrint += 2000
                print("---%d/~%d done" % (lastPrint, tiles))
            if not dontNextTile:
                tile = node.next()
            else:
                dontNextTile = False
    elif type == 12: # Towns
        
        while otbm.uint8() == 0xFE:
            townType = otbm.uint8()
            if townType == 13:
                townId = otbm.uint32()
                townName = otbm.string()
                temple = [otbm.uint16(),otbm.uint16(),otbm.uint8()]
                m.town(townId, townName, temple)
            else:
                print("Unknown town node")
                
            
            
            
    elif type == 15 and version >= 2: # Waypoints
        
        while otbm.uint8() == 0xFE:
            waypointType = otbm.uint8()
            if waypointType == 16:
                name = otbm.string()
                cords = [otbm.uint16(),otbm.uint16(),otbm.uint8()]
                m.waypoint(name, cords)
            else:
                print("Unknown waypoint type")
    else:
        print otbm.pos
        print ("Unknown node type %s" % hex(type))
        sys.exit()    
    #print "assert", otbm.pos, otbm.peekUint8()
    #assert otbm.uint8() == 0xFF    
    node = nodes.next()
print("---Done with all OTBM nodes")

del otbm

### Begin XML reading
import xml.dom.minidom
dom = xml.dom.minidom.parse(spawns)

print("---Begin spawns")
for xSpawn in dom.getElementsByTagName("spawn"):
    baseX = int(xSpawn.getAttribute("centerx"))
    baseY = int(xSpawn.getAttribute("centery"))
    baseZ = int(xSpawn.getAttribute("centerz"))
    radius = int(xSpawn.getAttribute("radius"))
    spawn = "s = Spawn(%d, (%d, %d))" % (radius, baseX, baseY)
    spawnSectors = []
    spawnData = {}
    

    for xMonster in xSpawn.getElementsByTagName("monster"):
        monsterX = int(xMonster.getAttribute("x"))
        monsterY = int(xMonster.getAttribute("y"))
        monsterZ  = int(xMonster.getAttribute("z"))
        if monsterZ != baseZ:
            print("UNSUPPORTED spawns!")
            continue

        monsterName = ' '.join([s[0].upper() + s[1:] for s in xMonster.getAttribute("name").split(' ')]).replace(" Of ", " of ")

        sector = (int((baseX+monsterX)/32), int((baseY+monsterY)/32))
        if not sector in spawnSectors:
            spawnSectors.append(sector)
            spawnData[sector] = []
        
        spawnData[sector].append("s.monster(\"%s\", %d, %d, %d, %s)" % (monsterName, monsterX, monsterY, monsterZ, xMonster.getAttribute("spawntime")))    

    for xMonster in xSpawn.getElementsByTagName("npc"):
        npcX = int(xMonster.getAttribute("x"))
        npcY = int(xMonster.getAttribute("y"))
        npcZ  = int(xMonster.getAttribute("z"))
        if npcZ != baseZ:
            print("UNSUPPORTED spawns!")
        
        npcName = ' '.join([s[0].upper() + s[1:] for s in xMonster.getAttribute("name").split(' ')]).replace(" Of ", " of ")

        sector = (int((baseX+npcX)/32), int((baseY+npcY)/32))
        if not sector in spawnSectors:
            spawnSectors.append(sector)
            spawnData[sector] = []
        spawnData[sector].append("s.npc(\"%s\", %d, %d, %d, %s)" % (npcName, npcX, npcY, npcZ, xMonster.getAttribute("spawntime")))  
        
    for entry in spawnSectors:
        x = (entry[0]*32)+16
        y = (entry[1]*32)+16
        # Too lazy to refactor this, probably adds a second to the convertion time, but should otherwise have no ill effects.
        exec("""%s
%s
at(%d, %d, s, %d)""" % (spawn,'\n'.join(spawnData[entry]),x,y,baseZ))
        
print("---Done with spawns")

print("---Begin houses")
dom = xml.dom.minidom.parse(houses)
housesql = """INSERT INTO `houses` (`id`,`name`,`town`,`size`,`rent`) VALUES"""
houses = []
for xHouse in dom.getElementsByTagName("house"):
    houses.append("('%s', '%s', '%s', '%s', '%s')" % (xHouse.getAttribute("houseid"),xHouse.getAttribute("name"),xHouse.getAttribute("townid"),xHouse.getAttribute("size"),xHouse.getAttribute("rent")))
if houses:
    print ("---Writing houses.sql")    
    open("houses.sql", "wb").write(housesql + ','.join(houses) + ";")

    print("---Done houses")

gc.collect()
m.compile()
print("-- Done!")
