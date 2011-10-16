#!/usr/bin/env python
# -*- coding: latin-1 -*-

import struct, sys

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
        return struct.unpack("<B", self.data[self.pos-1:self.pos])[0]
        
    def peekUint8(self):
        try:
            a = self.uint8()
            self.pos -= 1
            return a
        except:
            return None
    def int8(self):
        self.pos += 1
        return struct.unpack("<b", self.data[self.pos-1:self.pos])[0]

    # 16bit - 2bytes, C type: short
    def uint16(self):
        self.pos += 2
        return struct.unpack("<H", self.data[self.pos-2:self.pos])[0]
    def int16(self):
        self.pos += 2
        return struct.unpack("<h", self.data[self.pos-2:self.pos])[0]

    # 32bit - 4bytes, C type: int
    def uint32(self):
        self.pos += 4
        return struct.unpack("<I", self.data[self.pos-4:self.pos])[0]
    def int32(self):
        self.pos += 4
        return struct.unpack("<i", self.data[self.pos-4:self.pos])[0]

    # 64bit - 8bytes, C type: long long
    def uint64(self):
        self.pos += 8
        return struct.unpack("<Q", self.data[self.pos-8:self.pos])[0]
    def int64(self):
        self.pos += 8
        return struct.unpack("<q", self.data[self.pos-8:self.pos])[0]

    # 32bit - 4bytes, C type: float
    def float(self):
        self.pos += 4
        return struct.unpack("<f", self.data[self.pos-4:self.pos])[0]

    # 64bit - 8bytes, C type: double
    def double(self):
        self.pos += 8
        return struct.unpack("<d", self.data[self.pos-8:self.pos])[0]

    def string(self):
        length = self.uint16()
        self.pos += length
        return ''.join(map(str, struct.unpack("%ds" % length, self.data[self.pos-length:self.pos])))

    def getX(self, size):
        self.pos += size
        return ''.join(map(str, struct.unpack_from("B"*size, self.data, self.pos - size)))

    def getXString(self, size):
        self.pos += size
        return ''.join(map(str, struct.unpack("%ds" % size, self.data[self.pos-size:self.pos])))
        
    def getData(self):
        return self.data[self.pos:]
    

class L(object):
    __slots__ = ('value')
    def __init__(self, val):
        self.value = val
        
class Node(object):
    __slots_ = ('data', 'nodes', 'begin', 'size')
    def __init__(self, begin, size=None):
        self.data = b""
        self.nodes = []
        self.begin = begin
        self.size = size
            

    def parse(self):
        otbm.pos = self.begin
        byte = otbm.uint8()
        nextIsEscaped = False
        while otbm.pos < (self.begin + self.size):
            if byte == 0xFE and not nextIsEscaped:
                blockSize = self.sizer()
                node = self.handleBlock(otbm.pos, blockSize)
                otbm.pos += blockSize
            elif byte == 0xFF and not nextIsEscaped:
                level.value -= 1
                if level.value < 0:
                    print("DEBUG!")
                break
                
            elif byte == 0xFD and not nextIsEscaped:
                nextIsEscaped = True
                
            else:
                nextIsEscaped = False 
                self.data += struct.pack("<B", byte)
                
            byte = otbm.uint8()
        self.data = Reader(self.data)

    def sizer(self):
        oldPos = otbm.pos
        global subLevels
        subLevels = 0
        
        def leveler():
            global subLevels
            subLevels += 1
            byte = otbm.uint8()
            nextIsEscaped = False
            while byte != None:
                if byte == 0xFE and not nextIsEscaped:
                    leveler()

                elif byte == 0xFF and not nextIsEscaped:
                    subLevels -= 1
                    if subLevels < 0:
                        print("DEBUG!")
                    break
                    
                elif byte == 0xFD and not nextIsEscaped:
                    nextIsEscaped = True
                    
                else:
                    nextIsEscaped = False 
                    
                byte = otbm.uint8()            
        leveler()
        size = otbm.pos - oldPos
        otbm.pos = oldPos
        return size
    def handleBlock(self, begin, size):
        level.value += 1
        node = Node(begin, size)
        self.nodes.append(node)
        return node
        
    def next(self):
        if self.nodes:
            try:
                del self.data
            except:
                pass
            node = self.nodes.pop(0)
            node.parse()
            return node
        else:
            del self # It's rather safe to assume we don't be around anymore
            return None


dummyItems = {}
def genItem(itemid, *argc, **kwargs):
    if not itemid in dummyItems:
        dummyItems[itemid] = Item(itemid, *argc, **kwargs)
    return dummyItems[itemid]

otbmFile = open("map.otbm", 'rb')
otbm = Reader(otbmFile.read())

level = L(1)
root = Node(5, len(otbm.data)) # Begin on level 1
root.parse()
root.data.pos += 1

version = root.data.uint32()
width = root.data.uint16()
height = root.data.uint16()
majorVersionItems = root.data.uint32()
minorVersionItems = root.data.uint32()

# Tiles
tiles = (width * height) / 4 # This also count null tiles which we doesn't pass, bad

print("OTBM v%d, %dx%d" % (version, width, height)) 
_output_ = []
_output_.append("""
from generator import Map, Item, Tile, Spawn
print ("--Generating the map layout with no filling (gad this takes alot of memory)")
m = Map($$$MAX_X$$$,$$$MAX_Y$$$,None,$$$MAX_Z$$$)
at = m.addTo
a = m.add
I = Item
T = Tile
print ("--Done generating the map layout")
""")
# Prepopulate map with a ground level of voids

nodes = root.next()
nodes.data.pos += 1
description = ""
spawns = ""
houses = ""

_output_.append("""m.author("OTBMXML2sec generator")
print ("--Beging parsing description, spawns, and houses")
""")
while nodes.data.peekUint8():
    attr = nodes.data.uint8()
    if attr == 1:
        description += nodes.data.string()+"\n"
        
    elif attr == 11:
        spawns = nodes.data.string()
        print("--Using spawns: %s" % spawns)
    elif attr == 13:
        houses = nodes.data.string()
        print("--Using houses: %s" % houses)
    else:
        print("Unknown nodes data")
        
_output_.append('m.description("""%s""")' % (description))
print (description)
node = nodes.next()
onTile = 0
lastPrint = 0
print("--Begin OTBM nodes")
MAX_X = 0
MAX_Y = 0
MAX_Z = 0
while node:
    type = node.data.uint8()
    if type == 4: # Tile area
        baseX = node.data.uint16()
        baseY = node.data.uint16()
        baseZ = node.data.uint8()
        
        tile = node.next()
        while tile:
            tileType = tile.data.uint8()
            if tileType == 5 or tileType == 14: # Tile
                tileX = tile.data.uint8() + baseX
                tileY = tile.data.uint8() + baseY
                
                if tileX > MAX_X:
                    MAX_X = tileX
                if tileY > MAX_Y:
                    MAX_Y = tileY
                if baseZ > MAX_Z:
                    MAX_Z = baseZ
                    
                houseId = 0
                if tileType == 14:
                    houseId = tile.data.uint32()
                _render_ = False
                _itemG_ = None
                flags = 0
                
                # Attributes
                while tile.data.peekUint8():
                    attr = tile.data.uint8()
                    if attr == 3: # OTBM_ATTR_TILE_FLAGS
                        flags = tile.data.uint32()
                        
                    elif attr == 9: # ITEM, ground item
                        _itemG_ = "I(%d)" % (tile.data.uint16())
                        _render_ = True
                        
                    else:
                        print("Unknown tile attrubute")
                
                if _itemG_:
                    _tile_ = ["ti=[%s]" % _itemG_]
                else:
                    _tile_ = ["ti=[]"]
                
                item = tile.next()
                itemNum = 0
                while item:
                    if item.data.uint8() == 6: # more items
                        itemId = item.data.uint16()
                        _tile_.append("i%d=I(%d)" % (itemNum, itemId))
                        
                        # Unserialie attributes
                        while item.data.peekUint8():
                            attr = item.data.uint8()
                            if attr == 10: # depotId
                                _tile_.append("i%d.attribute(\"depotId\",%d)" % (itemNum, item.data.uint16()))
                                safe = False
                            elif attr == 14: # houseDoorId
                                safe = False
                                _tile_.append("i%d.attribute(\"doorId\",%d)" % (itemNum, item.data.uint8()))
                                
                                _tile_.append("i%d.action('houseDoor')" % itemNum)
                            elif attr == 20: # Sleeperguid
                                item.data.uint32() # TODO: care?
                            elif attr == 21: # sleepstart
                                item.data.uint32()
                            elif attr == 8: # Teleport destination
                                safe = False
                                _tile_.append("i%d.attribute(\"teledest\",(%d,%d,%d))" % (itemNum,item.data.uint16(),item.data.uint16(),item.data.uint8()))
                            elif attr == 15: # Item count
                                safe = False
                                _tile_.append("i%d.attribute(\"count\",%d)" % (itemNum, item.data.uint8()))
                            elif attr == 4: # action id
                                safe = False
                                _tile_.append("i%d.action('%d')" % (itemNum, item.data.uint16()))
                            elif attr == 5:
                                safe = False
                                _tile_.append("i%d.action('%d')" % (itemNum, item.data.uint16() + 0xFFFF))
                            elif attr == 6:
                                safe = False
                                _tile_.append('i%d.attribute("text","""%s""")' % (itemNum, item.data.string()))
                            elif attr == 18:
                                safe = False
                                _tile_.append("i%d.attribute(\"written\",%d)" % (itemNum, item.data.uint32()))
                            elif attr == 19:
                                safe = False
                                _tile_.append("i%d.attribute(\"writtenBy\",\"%s\")" % (itemNum, item.data.string()))
                            elif attr == 7:
                                safe = False
                                _tile_.append("i%d.attribute(\"description\",\"%s\")" % (itemNum, item.data.string()))
                            elif attr == 12:
                                runeCharges = item.data.uint8()
                            elif attr == 22:
                                safe = False
                                _tile_.append("i%d.attribute(\"count\",%d)" % (itemNum, item.data.uint8()))
                            elif attr == 16:
                                duration = item.data.uint32()
                                print("duration = %d" % duration)
                            elif attr == 17:
                                decayState = item.data.uint8()
                                print("TODO: decaystate = %d on %d" % (decayState, itemId))
                            elif attr == 23:
                                count = item.data.uint32()
                                break # All after this is container items
                            else:
                                print("Unknown item attribute %d" % attr)
                        _render_ = True
                        
                        _tile_.append("ti.append(i%d)" % itemNum)
                        itemNum += 1
                    else:
                        print("Unknown item header")
                    item = tile.next()
            else:
                print("Unknown tile node")
            if _render_:
                if len(_tile_) == 1:
                    _output_.append("at(%d,%d,%s%s)" % (tileX, tileY, _tile_[0].replace("ti=",""), ',%d'%baseZ if baseZ != 7 else ''))
                else:
                    _tile_.append("at(%d,%d,ti%s)" % (tileX, tileY, ',%d'%baseZ if baseZ != 7 else ''))
                    _output_.append("\n".join(_tile_))
                if houseId:
                    _output_.append("m.houses[(%d,%d,%d)]=%d" % (tileX, tileY, baseZ, houseId))
                if flags:
                    _output_.append("m.flags[(%d,%d,%d)]=%d" % (tileX, tileY, baseZ, flags))
            onTile += 1
            if onTile - lastPrint == 2000:
                lastPrint += 2000
                print("---%d/~%d done" % (lastPrint, tiles))
            tile = node.next()
            
    elif type == 12: # Towns
        town = node.next()
        
        while town:
            townType = town.data.uint8()
            if townType == 13:
                townId = town.data.uint32()
                townName = town.data.string()
                temple = [town.data.uint16(),town.data.uint16(),town.data.uint8()]
                _output_.append("m.town(%d, \"%s\", %s)" % (townId, townName, temple))
            else:
                print("Unknown town node")
                
            town = node.next()
            
            
    elif type == 15 and version >= 2: # Waypoints
        waypoint = node.next()
        
        while waypoint:
            waypointType = waypoint.data.uint8()
            if waypointType == 16:
                name = waypoint.data.string()
                cords = [waypoint.data.uint16(),waypoint.data.uint16(),waypoint.data.uint8()]
                _output.append("m.waypoint(\"%d\", %s)" % (name, cords))
            else:
                print("Unknown waypoint type")
            waypoint = node.next()
    del node
    node = nodes.next()

print("---Done with all OTBM nodes")

del nodes
del root
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

        monsterName = xMonster.getAttribute("name") 

        sector = (int((baseX+monsterX)/32), int((baseY+monsterY)/32))
        if not sector in spawnSectors:
            spawnSectors.append(sector)
            spawnData[sector] = []
        
        spawnData[sector].append("s.monster(\"%s\", %d, %d, %d)" % (monsterName, monsterX, monsterY, monsterZ))    

    for xMonster in xSpawn.getElementsByTagName("npc"):
        npcX = int(xMonster.getAttribute("x"))
        npcY = int(xMonster.getAttribute("y"))
        npcZ  = int(xMonster.getAttribute("z"))
        if npcZ != baseZ:
            print("UNSUPPORTED spawns!")
        
        npcName = xMonster.getAttribute("name") 

        sector = (int((baseX+npcX)/32), int((baseY+npcY)/32))
        if not sector in spawnSectors:
            spawnSectors.append(sector)
            spawnData[sector] = []
        spawnData[sector].append("s.npc(\"%s\", %d, %d, %d)" % (npcName, npcX, npcY, npcZ))  
        
    for entry in spawnSectors:
        x = (entry[0]*32)+16
        y = (entry[1]*32)+16
        _output_.append(spawn)
        _output_.append('\n'.join(spawnData[entry]))
        _output_.append("at(%d, %d, s, %d)\n" % (x, y, baseZ))
        if x > MAX_X:
            MAX_X = x
        if y > MAX_Y:
            MAX_Y = y
        if baseZ > MAX_Z:
            MAX_Z = baseZ
        
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

_output_.append("m.compile()")
_output_[0] = _output_[0].replace("$$$MAX_X$$$", str(MAX_X+1)).replace("$$$MAX_Y$$$", str(MAX_Y+1)).replace("$$$MAX_Z$$$", str(MAX_Z+1))
lef = len(_output_)
le = lef / 100
co = 1
for i in xrange(le, lef, le):
    _output_.insert(i, "print ('%d%% (%d/%d)')" % (co, i, lef))
    co += 1
    
print("-- Writing genmap.py")
with open("genmap.py", "wb") as f:
    f.write("\n".join(_output_))

print("-- Done! (map truncated to %dx%dx%d)" % (MAX_X, MAX_Y, MAX_Z))