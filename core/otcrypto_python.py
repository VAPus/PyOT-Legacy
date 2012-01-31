import config
import struct

D = int(config.RSAKeys["d"])
N = int(config.RSAKeys["n"])

def bytes( long_int ):
    bytes = []
    while long_int != 0:
        b = long_int%256
        bytes.insert( 0, chr(b) )
        long_int //= 256
    bytes.insert( 0, "\x00" )
    return ''.join(bytes)

def decryptRSA(stream):
    return bytes(pow(int(stream.encode("hex"), 16), D, N))

def decryptXTEA(stream, k):
    buffer = ""
    pos = 0
    while pos < (len(stream)):
        v0,v1 = struct.unpack("<2L", stream[pos:pos+8])
        sum = (0x9E3779B9 * 32) & 0xffffffff
        for i in xrange(32):
            v1 = (v1 - (((v0<<4 ^ v0>>5) + v0) ^ (sum + k[sum>>11 & 3]))) & 0xffffffff
            sum = (sum - 0x9E3779B9) & 0xffffffff
            v0 = (v0 - (((v1<<4 ^ v1>>5) + v1) ^ (sum + k[sum & 3]))) & 0xffffffff
        buffer += struct.pack("<2L", v0, v1)
        pos += 8

    return buffer

def encryptXTEA(stream, k):
    
    buffer = ""
    pos = 0

    pad = (8 - (len(stream) % 8)) % 8
    if pad:
        stream += "\x33" * pad

    pos = 0
    while pos < (len(stream)):
        v0, v1= struct.unpack("<2L", stream[pos:pos+8])
        sum = 0
        for i in xrange(32):
            v0 = (v0 + (((v1<<4 ^ v1>>5) + v1) ^ (sum + k[sum & 3]))) & 0xffffffff
            sum = (sum + 0x9E3779B9) & 0xffffffff
            v1 = (v1 + (((v0<<4 ^ v0>>5) + v0) ^ (sum + k[sum>>11 & 3]))) & 0xffffffff
        buffer += struct.pack("<2L", v0, v1)
        pos += 8


    return buffer