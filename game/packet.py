from struct import unpack, pack
from otcrypto import encryptXTEA
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
        return self.data[self.pos-1]
    def int8(self):
        self.pos += 1
        return unpack("<b", self.data[self.pos-1])[0]

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
        return self.data[self.pos-length:self.pos].decode("utf8")

    def getX(self, size):
        self.pos += size
        #return ''.join(map(str, struct.unpack_from("B"*size, self.data, self.pos - size)))
        return self.data[self.pos-size:self.pos]

    def getData(self):
        return self.data[self.pos:]

    def position(self, instance=None):
        self.pos += 5
        x,y,z = unpack("<HHB", self.data[self.pos - 5:self.pos]) 
        return Position(x, y, z, instance)
        
    def stackPosition(self, instance=None):
        self.pos += 6
        x,y,z, stackPos = unpack("<HHBB", self.data[self.pos - 6:self.pos]) 
        return StackPosition(x, y, z, stackPos, instance)
        
class TibiaPacket(object):
    __slots__ = ('data', 'stream', 'raw')
    def __init__(self, header=None):
        self.data = [""]
        self.stream = None
        self.raw = self.data.append        
        if header:
            self.uint8(header)
            
    def clear(self):
        self.data = [""]
        self.raw = self.data.append
        
    # 8bit - 1byte, C type: char
    def uint8(self, data, pack = pack):
        self.raw(pack("<B", data))
    def int8(self, data, pack=pack):
        self.raw(pack("<b", data))
        
    # 16bit - 2bytes, C type: short
    def uint16(self, data, pack=pack):
        self.raw(pack("<H", data))
    def int16(self, data, pack=pack):
        self.raw(pack("<h", data))

    # 32bit - 4bytes, C type: int
    def uint32(self, data, pack=pack):
        self.raw(pack("<I", data))
    def int32(self, data):
        self.raw(pack("<i", data))
    # 64bit - 8bytes, C type: long long
    def uint64(self, data):
        self.raw(pack("<Q", data))
    def int64(self, data):
        self.raw(pack("<q", data))

    def double(self, data):
        self.uint8(3)
        self.uint32((round(data, 3) * 1000) + 0x7FFFFFFF)
        
    def string(self, string, pack=pack):
        # HACK! Should be fixed before merge i hope. This gets a utf-8 that is NOT a unicode.
        """try:
            string = string.decode("utf-8").encode('iso8859-1')
        except UnicodeDecodeError:
            pass # From client or translated source
        """
        length = len(string)
        self.uint16(length)
        self.raw(string.encode('iso8859-1'))
        
    def put(self, string):
        self.raw(str(string))
        
    def send(self, stream, pack=pack, len=len, adler32=adler32, encryptXTEA=encryptXTEA, sum=sum, map=map):
        if not stream or len(self.data) < 2: return

        length = sum(map(len, self.data))
        self.data[0] = pack("<H", length)
        #data = "%s%s" % (pack("<H", le(self.data)), ''.join(self.data))

        if stream.xtea:
            data = encryptXTEA(self.data, stream.xtea, length+2)
        else:
            data = b''.join(self.data)

        stream.transport.write(pack("<HI", len(data)+4, adler32(data) & 0xffffffff)+data)   
        self.data = None
        
    #@inThread
    def sendto(self, list):
        if not list or not self.data:
            return # Noone to send to
        
        length = sum(map(len, self.data))
        self.data[0] = pack("<H", length)

        #data = "%s%s" % (pack("<H", len(self.data)), ''.join(self.data))
        for client in list:
            if not client:
                continue

            if client.xtea:
                data = encryptXTEA(self.data, client.xtea, length+2)
            else:
                data = b''.join(self.data)
            client.transport.write(pack("<HI", len(data)+4, adler32(data) & 0xffffffff)+data)
            
    # For use with with statement. Easier :)
    def __exit__(self, type, value, traceback):
        if not type:
            self.send(self.stream)

    def __enter__(self):
        return self
