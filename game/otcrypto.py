import config
from struct import pack, unpack
import codecs
D = int(config.RSAKeys["d"])
N = int(config.RSAKeys["n"])

def bytes( long_int ):
    bytes = bytearray()
    while long_int != 0:
        b = long_int & 255
        bytes.append( b )
        long_int >>= 8
    bytes.append( 0 )
    bytes.reverse()
    return bytes

def decryptRSA(stream):
    return bytes(pow(int.from_bytes(stream, 'big'), D, N))

def decryptXTEA(stream, k):
    length = len(stream) >> 2
    bstr = "<%dL" % length
    packs = list(unpack(bstr, stream))

    for pos in range(0, length, 2):
        v0 = packs[pos]
        v1 = packs[pos+1]
        for i in range(32):
            v1 = (v1 - (((v0<<4 ^ v0>>5) + v0) ^ k[63-i])) & 0xffffffff
            v0 = (v0 - (((v1<<4 ^ v1>>5) + v1) ^ k[31-i])) & 0xffffffff
        packs[pos] = v0
        packs[pos+1] = v1

    return pack(bstr, *packs)

def encryptXTEA(stream, k, length):
    pad = 8 - (length & 7)
    if pad:
        stream.append(b"\x33" * pad)
    length += pad
    length >>= 2
    try:
        stream = b''.join(stream)
    except:
        print(stream)
    bstr = "<%dL" % length
    
    packs = list(unpack(bstr, stream))

    for pos in range(0, length, 2):
        v0 = packs[pos]
        v1 = packs[pos+1]
        for i in range(32):
            v0 = (v0 + (((v1<<4 ^ v1>>5) + v1) ^ k[i])) & 0xffffffff
            v1 = (v1 + (((v0<<4 ^ v0>>5) + v0) ^ k[32 + i])) & 0xffffffff
        packs[pos] = v0
        packs[pos+1] = v1


    return pack(bstr, *packs)
