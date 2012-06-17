from struct import unpack, pack

import sys
if sys.subversion[0] != 'PyPy':
    try:
        import otcrypto
    except:
        import otcrypto_python as otcrypto
else:
    import otcrypto_python as otcrypto

from zlib import adler32

"""
from twisted.internet import reactor
def inThread(f):
    def func(*argc, **argw):
        reactor.callInThread(f, *argc, **argw)
    return func
"""

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
        return unpack("<b", self.data[self.pos-1:self.pos])[0]

    # 16bit - 2bytes, C type: short
    def uint16(self):
        self.pos += 2
        return unpack("<H", self.data[self.pos-2:self.pos])[0]
    def int16(self):
        self.pos += 2
        return unpack("<h", self.data[self.pos-2:self.pos])[0]

    # 32bit - 4bytes, C type: int
    def uint32(self):
        self.pos += 4
        return unpack("<I", self.data[self.pos-4:self.pos])[0]
    def int32(self):
        self.pos += 4
        return unpack("<i", self.data[self.pos-4:self.pos])[0]

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
        #return ''.join(map(str, unpack("%ds" % length, self.data[self.pos-length:self.pos])))
        return self.data[self.pos-length:self.pos]

    def getX(self, size):
        self.pos += size
        #return ''.join(map(str, struct.unpack_from("B"*size, self.data, self.pos - size)))
        return self.data[self.pos-size:self.pos]

    def getData(self):
        return self.data[self.pos:]

    def position(self, instance=None):
        self.pos += 5
        x,y,z = unpack("<HHB", self.data[self.pos - 5:self.pos]) 
        return game.map.Position(x, y, z, instance)
        
    def stackPosition(self, instance=None):
        self.pos += 6
        x,y,z, stackPos = unpack("<HHBB", self.data[self.pos - 6:self.pos]) 
        return game.map.StackPosition(x, y, z, stackPos, instance)
        
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
        self.data += pack("<b", data)

    # 16bit - 2bytes, C type: short
    def uint16(self, data):
        self.data += pack("<H", data)
    def int16(self, data):
        self.data += pack("<h", data)

    # 32bit - 4bytes, C type: int
    def uint32(self, data):
        self.data += pack("<I", data)
    def int32(self, data):
        self.data += pack("<i", data)

    # 64bit - 8bytes, C type: long long
    def uint64(self, data):
        self.data += pack("<Q", data)
    def int64(self, data):
        self.data += pack("<q", data)

    # 32bit - 4bytes, C type: float
    def float(self, data):
        self.data += pack("<f", data)

    # 64bit - 8bytes, C type: double
    def double(self, data):
        self.data += pack("<d", data)

        
    def string(self, string):
        # HACK! Should be fixed before merge i hope. This gets a utf-8 that is NOT a unicode.
        try:
            string = string.decode("utf-8").encode('iso8859-1')
        except UnicodeDecodeError:
            pass # From client or translated source
            
        length = len(string)
        self.data += pack("<H", length) + string

    def put(self, string):
        self.data += str(string)
        
    def raw(self, data):
        self.data += data

    #@inThread
    def send(self, stream):
        assert stream and self.data

        data = pack("<H", len(self.data))+self.data

        if stream.xtea:
            data = otcrypto.encryptXTEA(data, stream.xtea)

        stream.transport.write(pack("<HI", len(data)+4, adler32(data) & 0xffffffff)+data)   
            
    #@inThread
    def sendto(self, list):
        if not list or not self.data:
            return # Noone to send to
        
        data = pack("<H", len(self.data))+self.data
        for client in list:
            if not client:
                continue
            
            if client.xtea:
                data = otcrypto.encryptXTEA(data, client.xtea)

            client.transport.write(pack("<HI", len(data)+4, adler32(data) & 0xffffffff)+data)