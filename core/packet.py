import struct
import otcrypto
from twisted.internet import reactor
from zlib import adler32

def inThread(f):
    def func(*argc, **argw):
        reactor.callInThread(f, *argc, **argw)
    return func

class TibiaPacketReader(object):
    __slots__ = ('pos', 'data')
    def __init__(self, data):
        self.pos = 0
        self.data = data

    # 8bit - 1byte, C type: char
    def uint8(self):
        self.pos += 1
        return ord(self.data[self.pos-1:self.pos])
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

    def position(self, instance=None):
        return game.map.Position(self.uint16(), self.uint16(), self.uint8(), instance)
        
    def stackPosition(self, instance=None):
        return game.map.StackPosition(self.uint16(), self.uint16(), self.uint8(), self.uint8(), instance)
        
class TibiaPacket(object):
    __slots__ = ('bytes')
    def __init__(self, header=None):
        self.bytes = []
        if header:
            self.uint8(header)

    def clear(self):
        self.bytes = []

    def reserve(self):
        curr = len(self.bytes)
        self.bytes.append(None)
        
    def fillUint8(self, pos, data):
        self.bytes[pos] = struct.pack("<B", data)
        
    # 8bit - 1byte, C type: char
    def uint8(self, data):
        self.bytes.append(chr(data))
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

        
    def string(self, string):
        self.uint16(len(string))
        self.bytes.append(struct.pack("%ds" % len(string), str(string)))

    def put(self, string):
        self.bytes.append(struct.pack("%ds" % len(string), str(string)))
        
    def raw(self, data):
        self.bytes.append(data)

    #@inThread
    def send(self, stream):
        if not stream:
            return
        stream.writeQueue.append(''.join(self.bytes))
        
    #@inThread
    def sendto(self, list):
        if not list:
            return # Noone to send to
        
        self.bytes = [''.join(self.bytes)]
        for client in list:
            if not client:
                continue
             
            client.writeQueue.append(self.bytes[0])
    
