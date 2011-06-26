
import struct

# The reader class:
class Reader:
    def __init__(self, data):
        self.length = len(data)
        self.pos = 0
        self.data = data

    # 8bit - 1byte, C type: char
    def uint8(self):
        self.pos += 1
        return struct.unpack("<B", self.data[self.pos-1:self.pos])[0]
        
    def peekUint8(self, pos=1):
        try:
            self.pos += pos-1
            a = self.uint8()
            self.pos -= pos
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
    
class Tile:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.houseid = 0
        self.data = {}
        self.items = [] # 0 is ground id

class Item:
     def __init__(self, id):
        self.id = id
        self.data = {}
        
otbmFile = open("map.otbm")
otbm = Reader(otbmFile.read())

# This file is somewhat designed as a XMl file



# Now, we could naturally just read shit, but some idiot figured we should use some junky escape system in the file, since we don't, we just got to remove the escape system entierly
# This code is probably 50%+ of the entier execution time
nLen = 0
nData = b""
escape = ""
"""for x in range(0, otbm.length):
    char = otbm.uint8()
    if char is not 0xFD or not otbm.peekUint8() in (0xFD, 0xFE, 0xFF):
        nData += struct.pack("<B", char)
        nLen += 1      

otbm.data = nData
otbm.length = nLen"""

# Skip the first 4bytes, they're just NULLs
otbm.pos = 4

# The root node
if otbm.uint8() == 0xFE:
    # The get props code:
    otbm.uint8() #0x00
    version = otbm.uint32()
    width = otbm.uint16()
    height = otbm.uint16()
    itemVersion1 = otbm.uint32()
    itemVersion2 = otbm.uint32()
    print "OTBM version %d (OTB V: %d.%d, size: %dx%d)" % (version, itemVersion1, itemVersion2, width, height)

otbm.uint8() #0xFE
otbm.uint8() # 0x02
while otbm.peekUint8() != 0xFE:
    attr = otbm.uint8()

    if attr is 1:
        description = otbm.string()
    elif attr is 11:
        spawnFile = otbm.string()
    elif attr is 13:
        houseFile = otbm.string()
    else:
        print "Unknown byte in info (%d)!" % attr
print "DEBUG: Begin tiles on %d" % otbm.pos
tiles = []
mapTiles = {}
totTiles = 0
# Read shit
if True:
    while otbm.pos < otbm.length:
        if otbm.uint8() is not 0xFE: # this ain't suppose to happend, but if you fuck the file up, then sure :p
            #print "DEBUG: Not 0xFE opening, next byte is: %s" % otbm.peekUint8()
            continue
        type = otbm.uint8()
        if type is 4:
            baseX = otbm.uint16()
            baseY = otbm.uint16()
            baseZ = otbm.uint8()

            while otbm.peekUint8() is 0xFE:
                otbm.uint8() # 0xFE
                tileType = otbm.uint8()
                tileX = baseX + otbm.uint8()
                tileY = baseY + otbm.uint8()
                if tileType is 5 or tileType is 14:
                    tile = Tile()
                    tile.x = tileX
                    tile.y = tileY
                    tile.z = baseZ
                    if tileType is 14: # Houses
                        tile.houseid = otbm.uint32()
                    
                    while otbm.peekUint8() not in (0xFF, 0XFE):
                        attr = otbm.uint8()
                        if attr is 3:
                            flags = otbm.uint32() # TODO: Fix flags
                        elif attr is 9:
                            # Items
                            itemid = otbm.uint16()
                            tile.items.append(Item(itemid))
                        else:
                            print "Wrong stuff"

                    #otbm.uint8() # 0xFF
                    if otbm.peekUint8() is 0xFE:
                            while otbm.peekUint8() is 0xFE:
                                otbm.uint8() # 0xFE
                                attr = otbm.uint8()
                                if attr is 6:
                                    # Items
                                    itemid = otbm.uint16()
                                    _item = Item(itemid)

                                    while otbm.peekUint8() in (3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,30,31,33,34,35,36,37,38,39,40,41,42,43,128):
                                        unseri = otbm.uint8()
                                        if unseri is 15:
                                            _item.data["count"] = otbm.uint8()
                                        elif unseri is 6:
                                            _item.data["text"] = otbm.string()
                                        elif unseri is 7:
                                            _item.data["desc"] = otbm.string()
                                        elif unseri in (4,5):
                                            n = otbm.uint16() # Action id or unique id, we don't even support convertion of those!
                                            if n is 0xFFFF: # Bugfix
					      otbm.pos -= 2
					      break
                                        elif unseri is 8: # teleport is a tile matter
                                            tile.data["teleportto"] = (otbm.uint16(), otbm.uint16(), otbm.uint8())
                                        else:
                                            print "Unsupported unseri %d" % unseri
                                            quit()
                                    tile.items.append(Item(itemid))
                                else:
                                    print "Wrong stuff 2"
                                otbm.uint8() #0xFF
                    char = otbm.uint8()
                    if char is not 0xFF:
		       print "Terrible error! %d (on %d)" % (char, otbm.pos) # 0xFF
		       quit()
                    tiles.append(tile)
                    if not tile.x in mapTiles:
                        mapTiles[tile.x] = {}
                    if not tile.y in mapTiles[tile.x]:
                        mapTiles[tile.x][tile.y] = {}
                    if not tile.z in mapTiles[tile.x][tile.y]:
                        mapTiles[tile.x][tile.y][tile.y] = []
                    mapTiles[tile.x][tile.y][tile.y].append(tile)
                    totTiles += 1

            print "Leaving on pos %d (next was: %d %d %d)" % (otbm.pos, otbm.peekUint8(), otbm.peekUint8(2), otbm.peekUint8(3))
            
        elif type is 12:
            while otbm.peekUint8() is 0xFE:
                otbm.uint8() # 0xFE
                otbm.uint8() # 13
                otbm.uint32()
                otbm.string()
                otbm.uint16()
                otbm.uint16()
                otbm.uint8()
                otbm.uint8() # 0xFF
            otbm.uint8() # 0xFF
        elif type is 15:
            print "Buggy thing!"
            while otbm.peekUint8() is 0xFE:
                otbm.uint8() # 0xFE
                otbm.uint8() # 16
                otbm.uint32()
                otbm.string()
                otbm.uint16()
                otbm.uint16()
                otbm.uint8()
                otbm.uint8() # 0xFF
            otbm.uint8() # 0xFF         
        else:
            print "Unsupported type %d " % type
                    
print totTiles