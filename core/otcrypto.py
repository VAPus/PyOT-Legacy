import config
from struct import pack, unpack

D = int(config.RSAKeys["d"])
N = int(config.RSAKeys["n"])

def bytes( long_int ):
    bytes = []
    while long_int != 0:
        b = long_int & 255
        bytes.append( chr(b) )
        long_int >>= 8
    bytes.append( "\x00" )
    bytes.reverse()
    return ''.join(bytes)

def decryptRSA(stream):
    return bytes(pow(int(stream.encode("hex"), 16), D, N))

def decryptXTEA(stream, k):
    buffer = ""
    for pos in xrange(0, len(stream), 8):
        v0, v1 = unpack("<2L", stream[pos:pos+8])
        for i in xrange(32):
            v1 = (v1 - (((v0<<4 ^ v0>>5) + v0) ^ (k[63-i]))) & 0xffffffff
            v0 = (v0 - (((v1<<4 ^ v1>>5) + v1) ^ (k[31-i]))) & 0xffffffff
        buffer += pack("<2L", v0, v1)

    return buffer

def encryptXTEA(stream, k):
    buffer = ""
    pad = 8 - (len(stream) & 7)
    if pad:
        stream += "\x33" * pad

    for pos in xrange(0, len(stream), 8):
        v0, v1= unpack("<2L", stream[pos:pos+8])
        for i in xrange(32):
            v0 = (v0 + (((v1<<4 ^ v1>>5) + v1) ^ (k[i]))) & 0xffffffff
            v1 = (v1 + (((v0<<4 ^ v0>>5) + v0) ^ (k[32 + i]))) & 0xffffffff
        buffer += pack("<2L", v0, v1)


    return buffer