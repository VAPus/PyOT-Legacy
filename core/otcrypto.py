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
    buffer = []
    length = len(stream) >> 2
    bstr = "<%dL" % length
    packs = unpack(bstr, stream)

    for pos in xrange(0, length, 2):
        v0, v1 = packs[pos], packs[pos+1]
        for i in xrange(32):
            v1 = (v1 - (((v0<<4 ^ v0>>5) + v0) ^ k[63-i])) & 0xffffffff
            v0 = (v0 - (((v1<<4 ^ v1>>5) + v1) ^ k[31-i])) & 0xffffffff
        buffer.append(v0)
        buffer.append(v1)

    return pack(bstr, *buffer)

def encryptXTEA(stream, k, length):
    buffer = []
    pad = 8 - (length & 7)
    if pad:
        stream.append("\x33" * pad)
    length += pad
    length >>= 2
    stream = ''.join(stream)
    bstr = "<%dL" % length
    packs = unpack(bstr, stream)
    buffer_append = buffer.append

    for pos in xrange(0, length, 2):
        v0 = packs[pos]
        v1 = packs[pos+1]
        for i in xrange(32):
            v0 = (v0 + (((v1<<4 ^ v1>>5) + v1) ^ k[i])) & 0xffffffff
            v1 = (v1 + (((v0<<4 ^ v0>>5) + v0) ^ k[32 + i])) & 0xffffffff
        buffer_append(v0)
        buffer_append(v1)


    return pack(bstr, *buffer)
