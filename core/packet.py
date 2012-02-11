import struct
import sys
if sys.subversion[0] != 'PyPy':
    try:
        import otcrypto
    except:
        import otcrypto_python as otcrypto
else:
    import otcrypto_python as otcrypto
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
    __slots__ = ('data')
    def __init__(self, header=None):
        self.data = ""
        if header:
            self.uint8(header)

    def clear(self):
        self.data = ""
        
    # 8bit - 1byte, C type: char
    def uint8(self, data):
        self.data += chr(data)
    def int8(self, data):
        self.data += struct.pack("<b", data)

    # 16bit - 2bytes, C type: short
    def uint16(self, data):
        self.data += struct.pack("<H", data)
    def int16(self, data):
        self.data += struct.pack("<h", data)

    # 32bit - 4bytes, C type: int
    def uint32(self, data):
        self.data += struct.pack("<I", data)
    def int32(self, data):
        self.data += struct.pack("<i", data)

    # 64bit - 8bytes, C type: long long
    def uint64(self, data):
        self.data += struct.pack("<Q", data)
    def int64(self, data):
        self.data += struct.pack("<q", data)

    # 32bit - 4bytes, C type: float
    def float(self, data):
        self.data += struct.pack("<f", data)

    # 64bit - 8bytes, C type: double
    def double(self, data):
        self.data += struct.pack("<d", data)

        
    def string(self, string):
        length = len(string)
        self.data += struct.pack("<H", length) + string

    def put(self, string):
        self.data += str(string)
        
    def raw(self, data):
        self.data += data

    #@inThread
    def send(self, stream):
        if not stream or not self.data:
            return

        data = struct.pack("<H", len(self.data))+self.data

        if stream.xtea:
            data = otcrypto.encryptXTEA(data, stream.xtea)

        stream.transport.write(struct.pack("<HI", len(data)+4, adler32(data) & 0xffffffff)+data)    
            
    #@inThread
    def sendto(self, list):
        if not list or not self.data:
            return # Noone to send to
        
        data = struct.pack("<H", len(self.data))+self.data
        for client in list:
            if not client:
                continue
            
            if client.xtea:
                data = otcrypto.encryptXTEA(data, client.xtea)

            client.transport.write(struct.pack("<HI", len(data)+4, adler32(data) & 0xffffffff)+data)    