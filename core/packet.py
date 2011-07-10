import struct
import otcrypto
from zlib import adler32
import copy
from twisted.python import log

class TibiaPacketReader:
    def __init__(self, data):
        self.length = len(data)
        self.pos = 0
        self.data = data

    # 8bit - 1byte, C type: char
    def uint8(self):
        self.pos += 1
        return struct.unpack("<B", self.data[self.pos-1:self.pos])[0]
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
        
    # Positions
    # Returns list(x,y,z)
    #def position(self):
    #    position = components.position.Position(self.uint16(),self.uint16(),self.uint8())
    #    return position

    def string(self):
        length = self.uint16()
        self.pos += length
        return ''.join(map(str, struct.unpack("%ds" % length, self.data[self.pos-length:self.pos])))

    def getX(self, size):
        self.pos += size
        return ''.join(map(str, struct.unpack_from("B"*size, self.data, self.pos - size)))

    def getData(self):
        return self.data[self.pos:]

    def position(self):
        return [self.uint16(), self.uint16(), self.uint8()]
        
class TibiaPacket:
    def __init__(self, header=None):
        self.pos = 0
        self.data = b""
        if header:
            self.uint8(header)

    def clear(self):
        self.pos = 0
        self.data = b""

    # 8bit - 1byte, C type: char
    def uint8(self, data):
        self.pos += 1
        self.data += struct.pack("<B", data)
    def int8(self, data):
        self.pos += 1
        self.data += struct.pack("<b", data)

    # 16bit - 2bytes, C type: short
    def uint16(self, data):
        self.pos += 2
        self.data += struct.pack("<H", data)
    def int16(self, data):
        self.pos += 2
        self.data += struct.pack("<h", data)

    # 32bit - 4bytes, C type: int
    def uint32(self, data):
        self.pos += 4
        self.data += struct.pack("<I", data)
    def int32(self, data):
        self.pos += 4
        self.data += struct.pack("<i", data)

    # 64bit - 8bytes, C type: long long
    def uint64(self, data):
        self.pos += 8
        self.data += struct.pack("<Q", data)
    def int64(self, data):
        self.pos += 8
        self.data += struct.pack("<q", data)

    # 32bit - 4bytes, C type: float
    def float(self, data):
        self.pos += 4
        self.data += struct.pack("<f", data)

    # 64bit - 8bytes, C type: double
    def double(self, data):
        self.pos += 8
        self.data += struct.pack("<d", data)

    # Position
    # Parameters is list(x,y,z)
    def position(self, position):
        self.uint16(position[0])
        self.uint16(position[1])
        self.uint8(position[2])

    # Magic Effect
    def magicEffect(self, pos, type):
        self.uint8(0x83)
        self.position(pos)
        self.uint8(type)
   
    # Shoot
    def shoot(self, fromPos, toPos, type):
        self.uint8(0x85)
        self.position(fromPos)
        self.position(toPos)
        self.uint8(type)

    # Item
    # Parameters is of class Item or ItemID
    def item(self, item, count=None):
        import game.item
        if isinstance(item, game.item.Item):
            self.uint16(item.cid)
            if item.count is not None:
                self.uint8(item.count)
        else:
            self.uint16(item)
            if count:
                self.uint8(count)

    # Map Description (the entier visible map)
    # Isn't "Description" a bad word for it?
    def map_description(self, position, width, height):
        skip = -1
        start = 7
        end = 0
        step = -1

        # Higher then ground level
        if position[2] > 7:
            start = position[2] - 2
            end = min(15, position[2] + 2) # Choose the smallest of 15 (MAX - 1) and z + 2
            step = 1

        # Run the steps by appending the floor
        for z in range(start, (end+step), step):
            skip = self.floorDescription((position[0], position[1], z), width, height, position[2] - z, skip)

        if skip >= 0:
            self.uint8(skip)
            self.uint8(0xFF)
        
    # Floor Description (the entier floor)
    def floorDescription(self, position, width, height, offset, skip):
        from game.map import getTile
        for x in range(0, width):
            for y in range(0, height):
                tile = getTile((position[0] + x + offset , position[1] + y + offset, position[2]))
                if tile:
                    if skip >= 0:
                        self.uint8(skip)
                        self.uint8(0xFF)
                    skip = 0
                    self.tileDescription(tile)
                else:
                    skip += 1
                    if skip is 0xFF:
                        self.uint8(0xFF)
                        self.uint8(0xFF)
                        skip = -1
        return skip

    def tileDescription(self, tile):
        self.uint16(0x00)
        for item in tile.topItems():
            self.item(item)

        
        for creature in tile.creatures():
            self.creature(creature, False)
            

        for item in tile.bottomItems():
            self.item(item)

    # TODO: Outfit class?
    def add_outfit(self, looktype, head=0, body=None, legs=0, feet=0, addons=0,lookitem=0):
        self.uint16(looktype)
        if looktype is not 0:
            self.uint8(head)
            self.uint8(body)
            self.uint8(legs)
            self.uint8(feet)
            self.uint8(addons)
        else:
            self.uint16(lookitem)
            
        self.uint16(0x00) # Mount
        
    def creature(self, creature, known):
        if known:
            self.uint16(0x62)
            self.uint32(creature.clientId())
        else:
            self.uint16(0x61)
            self.uint32(0) # Remove known
            self.uint32(creature.clientId())
            self.uint8(creature.creatureType)
            self.string(creature.name())
        self.uint8(100) # Health %
        self.uint8(creature.direction) # Direction
        self.add_outfit(creature.data["looktype"], creature.data["lookhead"],creature.data["lookbody"],creature.data["looklegs"],creature.data["lookfeet"],0) # TODO: FIx outfits!
        self.uint8(0xFF) # Light
        self.uint8(215) # Light
        self.uint16(creature.speed) # Speed
        self.uint8(0) # Skull
        self.uint8(0) # Party/Shield
        if not known:
            self.uint8(0) # Emblem
        self.uint8(1) # Can't walkthrough
    def worldlight(self, level, color):
        self.uint8(0x82)
        self.uint8(level)
        self.uint8(color)

    def creaturelight(self, cid, level, color):
        self.uint8(0x8D)
        self.uint32(cid)
        self.uint8(level)
        self.uint8(color)

    def removeInventoryItem(self, pos):
        self.uint8(0x79)
        self.uint8(pos)
        
    def addInventoryItem(self, pos, item):
        self.uint8(0x78)
        self.uint8(pos)
        self.item(item)

    def addTileItem(self, pos, stackpos, item):
        self.uint8(0x6A)
        self.position(pos)
        self.uint8(stackpos)
        self.item(item)

    def addTileCreature(self, pos, stackpos, creature):
        self.uint8(0x6A)
        self.position(pos)
        self.uint8(stackpos)
        self.creature(creature, False)
        
    def updateTileItem(self, pos, stackpos, item):
        self.uint8(0x6B)
        self.position(pos)
        self.uint8(stackpos)
        self.item(item)
        
    def removeTileItem(self, pos, stackpos):
        self.uint8(0x6C)
        self.position(pos)
        self.uint8(stackpos)
        
    def string(self, string):
        self.uint16(len(string))
        self.pos += len(string)
        self.data += struct.pack("%ds" % len(string), str(string))

    def put(self, string):
        self.pos += len(string)
        self.data += struct.pack("%ds" % len(string), str(string))

    def send(self, stream):
        buffer = b""
        ol = len(self.data)

        self.data = struct.pack("<H", ol)+self.data
        ol += 2

        if stream.xtea:
            self.data = otcrypto.encryptXTEA(self.data, stream.xtea)

        adler = adler32(self.data)
        # Fix a bug in Python2?
        if adler < 0:
             adler = adler & 0xffffffff
        buffer = struct.pack("<HI", len(self.data)+4, adler)
        buffer += self.data

        stream.transport.write(buffer)
        
    def sendto(self, list):
        self.data = struct.pack("<H", len(self.data))+self.data
        lenCache = 0
        for client in list:
             data = otcrypto.encryptXTEA(self.data, client.xtea)
             adler = adler32(data)
             if adler < 0:
                 adler = adler & 0xffffffff
             
             if not lenCache:
                 lenCache = len(data)+4
             
             client.transport.write(bytes(struct.pack("<HI", lenCache, adler))+data)
