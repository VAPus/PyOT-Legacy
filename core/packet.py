import struct
import otcrypto
from twisted.python import log
from twisted.internet import reactor
from zlib import adler32

def inThread(f):
    def func(*argc, **argw):
        reactor.callInThread(f, *argc, **argw)
    return func
class TibiaPacketReader(object):
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
        
class TibiaPacket(object):
    def __init__(self, header=None):
        self.bytes = []
        if header:
            self.uint8(header)

    def clear(self):
        self.bytes = []

    # 8bit - 1byte, C type: char
    def uint8(self, data):
        self.bytes.append(struct.pack("<B", data))
    def int8(self, data):
        self.bytes.append(struct.pack("<b", data))

    # 16bit - 2bytes, C type: short
    def uint16(self, data):
        self.bytes.append(struct.pack("<H", data))
    def int16(self, data):
        self.bytes.append(struct.pack("<h", data))

    # 32bit - 4bytes, C type: int
    def uint32(self, data):
        self.bytes.append(struct.pack("<I", data))
    def int32(self, data):
        self.bytes.append(struct.pack("<i", data))

    # 64bit - 8bytes, C type: long long
    def uint64(self, data):
        self.bytes.append(struct.pack("<Q", data))
    def int64(self, data):
        self.bytes.append(struct.pack("<q", data))

    # 32bit - 4bytes, C type: float
    def float(self, data):
        self.bytes.append(struct.pack("<f", data))

    # 64bit - 8bytes, C type: double
    def double(self, data):
        self.bytes.append(struct.pack("<d", data))

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

            if item.stackable:
                self.uint8(item.count or 1)
            elif item.type == 11 or item.type == 12:
                if item.type == 11:
                    print "Notice on %d" % item.itemId
                self.uint8(item.fluidSource or 0)
            if item.animation:
                self.uint8(0xFE)
            
        else:
            self.uint16(item)
            if count:
                self.uint8(count)

    # Map Description (the entier visible map)
    # Isn't "Description" a bad word for it?
    def mapDescription(self, position, width, height, player=None):
        skip = -1
        start = 7
        end = 0
        step = -1

        # Lower then ground level
        if position[2] > 7:
            start = position[2] - 2
            end = min(15, position[2] + 2) # Choose the smallest of 15 and z + 2
            step = 1

        # Run the steps by appending the floor
        for z in xrange(start, (end+step), step):
            skip = self.floorDescription((position[0], position[1], z), width, height, position[2] - z, skip, player)

        if skip >= 0:
            self.uint8(skip)
            self.uint8(0xFF)
        
    # Floor Description (the entier floor)
    def floorDescription(self, position, width, height, offset, skip, player=None):
        from game.map import getTile
        for x in xrange(0, width):
            for y in xrange(0, height):
                tile = getTile((position[0] + x + offset, position[1] + y + offset, position[2]))
                if tile and tile.things:
                    if skip >= 0:
                        self.uint8(skip)
                        self.uint8(0xFF)
                    skip = 0
                    self.tileDescription(tile, player)
                else:
                    skip += 1
                    if skip == 0xFF:
                        self.uint8(0xFF)
                        self.uint8(0xFF)
                        skip = -1
        return skip

    def tileDescription(self, tile, player=None):
        self.uint16(0x00)
        
        for item in tile.topItems():
            self.item(item)

        for creature in tile.creatures():
            known = False
            if player and creature is not player:
                known = creature.cid in player.knownCreatures
                
                if not known:
                    player.knownCreatures.append(creature.cid)
  
            self.creature(creature, known)
            

        for item in tile.bottomItems():
            self.item(item)

    def outfit(self, look, addon=0, mount=0x00):
        
        self.uint16(look[0])
        if look[0] != 0:
            self.uint8(look[1])
            self.uint8(look[2])
            self.uint8(look[3])
            self.uint8(look[4])
            self.uint8(addon)
        else:
            self.uint16(look[1])
            
        self.uint16(mount) # Mount
        
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
        self.outfit(creature.outfit, creature.addon, creature.mount if creature.mounted else 0x00)
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

    def addContainerItem(self, openId, item):
        self.uint8(0x70)
        self.uint8(openId)
        self.item(item)
        
    def updateContainerItem(self, openId, slot, item):
        self.uint8(0x71)
        self.uint8(openId)
        self.uint8(slot)
        self.item(item)
       
    def removeContainerItem(self, openId, slot):
        self.uint8(0x72)
        self.uint8(openId)
        self.uint8(slot)
        
    def addTileItem(self, pos, stackpos, item):
        self.uint8(0x6A)
        self.position(pos)
        self.uint8(stackpos)
        self.item(item)

    def addTileCreature(self, pos, stackpos, creature, player=None):
        self.uint8(0x6A)
        self.position(pos)
        self.uint8(stackpos)
        known = False
        if player and creature is not player:
            known = creature.cid in player.knownCreatures
                
            if not known:
                player.knownCreatures.append(creature.cid)
 
        self.creature(creature, known)

    def moveUpPlayer(self, player, oldPos):
        self.uint8(0xBE)
        
        # Underground to surface
        if oldPos[2]-1 == 7:
            skip = self.floorDescription((oldPos[0] - 8, oldPos[1] - 6, 5), 18, 14, 3, -1, player)
            skip = self.floorDescription((oldPos[0] - 8, oldPos[1] - 6, 4), 18, 14, 4, skip, player)
            skip = self.floorDescription((oldPos[0] - 8, oldPos[1] - 6, 3), 18, 14, 5, skip, player)
            skip = self.floorDescription((oldPos[0] - 8, oldPos[1] - 6, 2), 18, 14, 6, skip, player)
            skip = self.floorDescription((oldPos[0] - 8, oldPos[1] - 6, 1), 18, 14, 7, skip, player)
            skip = self.floorDescription((oldPos[0] - 8, oldPos[1] - 6, 0), 18, 14, 8, skip, player)

            if skip >= 0:
                self.uint8(skip)
                self.uint8(0xFF)
                
        elif oldPos[2]-1 > 7: # Still underground
            skip = self.floorDescription((oldPos[0] - 8, oldPos[1] - 6, oldPos[2]-3), 18, 14, oldPos[2]+3, -1, player)
            
            if skip >= 0:
                self.uint8(skip)
                self.uint8(0xFF)
                
        self.uint8(0x68) # West
        self.mapDescription((oldPos[0] - 8, oldPos[1] + 1 - 6, oldPos[2]-1), 1, 14, player)
        
        self.uint8(0x65) # North
        self.mapDescription((oldPos[0] - 8, oldPos[1] - 6, oldPos[2]-1), 18, 1, player)
        
        
    def moveDownPlayer(self, player, oldPos):
        self.uint8(0xBF)
        if oldPos[2]+1 == 8:
            skip = self.floorDescription((oldPos[0] - 8, oldPos[1] - 6, oldPos[2]+1), 18, 14, -1, -1, player)
            skip = self.floorDescription((oldPos[0] - 8, oldPos[1] - 6, oldPos[2]+2), 18, 14, -2, skip, player)
            skip = self.floorDescription((oldPos[0] - 8, oldPos[1] - 6, oldPos[2]+3), 18, 14, -3, skip, player)

            if skip >= 0:
                self.uint8(skip)
                self.uint8(0xFF)
                
        elif oldPos[2]+1 > 8:
            skip = self.floorDescription((oldPos[0] - 8, oldPos[1] - 6, oldPos[2]+3), 18, 14, oldPos[2]-3, -1, player)
            
            if skip >= 0:
                self.uint8(skip)
                self.uint8(0xFF)            
        
        self.uint8(0x66) # East
        self.mapDescription((oldPos[0] + 9, oldPos[1] - 6, oldPos[2]+1), 1, 14, player)
        self.uint8(0x67) # South
        self.mapDescription((oldPos[0] - 8, oldPos[1] + 7, oldPos[2]+1), 18, 1, player)
        
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
        self.bytes.append(struct.pack("%ds" % len(string), str(string)))

    def put(self, string):
        self.bytes.append(struct.pack("%ds" % len(string), str(string)))

    @inThread
    def send(self, stream):
        self.bytes = (''.join(self.bytes),)

        if stream.xtea:
            data = otcrypto.encryptXTEA(struct.pack("<H", len(self.bytes[0]))+self.bytes[0], stream.xtea)
        else:
            data = struct.pack("<H", len(self.bytes[0]))+self.bytes[0]
        reactor.callFromThread(stream.transport.write, struct.pack("<HI", len(data)+4, adler32(data) & 0xffffffff)+data)
    
    @inThread
    def sendto(self, list):
        if not list:
            return # Noone to send to
        
        self.bytes = (''.join(self.bytes),)
        dataL = struct.pack("<H", len(self.bytes[0]))+self.bytes[0]
        lenCache = 0
        for client in list:
             data = otcrypto.encryptXTEA(dataL, client.xtea)
             if not lenCache:
                 lenCache = len(data)+4
             
             
             reactor.callFromThread(client.transport.write, bytes(struct.pack("<HI", lenCache, adler32(data) & 0xffffffff))+data)
