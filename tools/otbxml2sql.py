
import struct

# The reader class:
class Reader:
    def __init__(self, data):
        self.length = len(data)
        self.pos = 0
        self.data = data

    # 8bit - 1byte, C type: char
    def uint8(self):
        self.pos += 1
        return struct.unpack("<B", self.data[self.pos-1:self.pos])[0]
        
    def peekUint8(self):
        try:
            a = self.uint8()
            self.pos -= 1
            return a
        except:
            return None
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

    def string(self):
        length = self.uint16()
        self.pos += length
        return ''.join(map(str, struct.unpack("%ds" % length, self.data[self.pos-length:self.pos])))

    def getX(self, size):
        self.pos += size
        return ''.join(map(str, struct.unpack_from("B"*size, self.data, self.pos - size)))

    def getXString(self, size):
        self.pos += size
        return ''.join(map(str, struct.unpack("%ds" % size, self.data[self.pos-size:self.pos])))
        
    def getData(self):
        return self.data[self.pos:]
    
class Item:
    def __init__(self):
        self.type = 0
        self.flags = {}
        self.attr = {}
        self.cid = 0
        self.sid = 0
        self.speed = 0
        self.order = 0
        self.alsoKnownAs = []
        self.junk = False
otbFile = open("items.otb")
otb = Reader(otbFile.read())

# This file is somewhat designed as a XMl file



# Now, we could naturally just read shit, but some idiot figured we should use some junky escape system in the file, since we don't, we just got to remove the escape system entierly
# This code is probably 50%+ of the entier execution time
nLen = 0
nData = b""
escape = ""
for x in range(0, otb.length):
    char = otb.uint8()
    if char is not 0xFD or not otb.peekUint8() in (0xFD, 0xFE, 0xFF):
        nData += struct.pack("<B", char)
        nLen += 1      

otb.data = nData
otb.length = nLen

# Skip the first 4bytes, they're just NULLs
otb.pos = 4

# The root node
if otb.uint8() == 0xFE:
    # The get props code:
    otb.uint8() # Yet anther NULL byte
    flags = otb.uint32()
    nodeType = otb.uint8()
    if nodeType == 0x01:
        dataLen = otb.uint16()
        print "DEBUG len: %d" % dataLen
        majorVersion = otb.uint32()
        minorVersion = otb.uint32()
        buildVersion = otb.uint32()
        
        print "OTB version %d.%d (client: 9.0, build: %d)" % (majorVersion, minorVersion, buildVersion)
# Cheat the position to avoid junk
otb.pos = 13 + dataLen
items = []
lastRealItem = None

# A new node, the item nodes
if True:
    while otb.pos < otb.length:
        if otb.uint8() is not 0xFE: # this ain't suppose to happend, but if you fuck the file up, then sure :p
            print "DEBUG: Not 0xFE opening, next byte is: %d" % otb.peekUint8()
            continue
        item = Item()
        item.type = otb.uint8()
        flags = otb.uint32()
        # Ugly! And likely slow too
        flags = str(bin(flags)).replace("0b", "")
        numFlags = len(flags)
        if numFlags > 0 and int(flags[0]):
            item.flags["solid"] = True
        if numFlags > 1 and int(flags[1]):
            item.flags["blockprojectile"] = True
        if numFlags > 2 and int(flags[2]):
            item.flags["blockpath"] = True
        if numFlags > 3 and int(flags[3]):
            item.flags["hasheight"] = True
        if numFlags > 4 and int(flags[4]):
            item.flags["usable"] = True
        if numFlags > 5 and int(flags[5]):
            item.flags["pickable"] = True
        if numFlags > 6 and int(flags[6]):
            item.flags["movable"] = True
        if numFlags > 7 and int(flags[7]):
            item.flags["stackable"] = True
        if numFlags > 8 and int(flags[8]):
            item.flags["ontop"] = True
        if numFlags > 9 and int(flags[9]):
            item.flags["vertical"] = True
        if numFlags > 10 and int(flags[10]):
            item.flags["horizontal"] = True
        if numFlags > 11 and int(flags[11]):
            item.flags["hangable"] = True
        if numFlags > 12 and int(flags[12]):
            item.flags["distanceread"] = True
        if numFlags > 13 and int(flags[13]):
            item.flags["rotatable"] = True
        if numFlags > 14 and int(flags[14]):
            item.flags["readable"] = True
        if numFlags > 15 and int(flags[15]):
            item.flags["charges"] = True
        if numFlags > 16 and int(flags[16]):
            item.flags["lookthrough"] = True
        try:
            while otb.peekUint8() != 0xFF:
                attr = otb.uint8()
                datalen = otb.uint16()
                if attr is 0x10:
                    item.sid = otb.uint16()
                    
                elif attr is 0x11:
                    item.cid = otb.uint16()
                elif attr is 0x14:
                    item.speed = otb.uint16()
                elif attr is 0x37:
                    item.flags["order"] = otb.uint8()
                else:
                    otb.pos += datalen
                    
        except:
            pass
        try:
            otb.uint8() # 0xFF
        except:
            print "End parsing on %d (out of %d)" % (otb.pos, otb.length)
        if item.cid:
            items.append(item)
            lastRealItem = item
        else:
            lastRealItem.alsoKnownAs.append(item.sid)

import json, xml.dom.minidom as dom

data = {}
dom = dom.parse("items.xml")
for xItem in dom.getElementsByTagName("item"):
     xId = xItem.getAttribute("id")
     xFromId = xItem.getAttribute("fromid")
     xToId = xItem.getAttribute("toid")
     xName = xItem.getAttribute("name")
     if xId:
         data[int(xId)] = {"name":xName}
     elif xFromId and xToId:
         for x in range(int(xFromId), int(xToId)+1):
             data[int(x)] = {"name":xName}
print data
# Current suggested format:
# sid, cid, name, refids, flags, description, weight, worth, slot, duration, decayTo, floorchange
for item in items:
    if item.sid in data and item.alsoKnownAs:
        print("INSERT INTO items VALUES(%d, %d, '%s', '%s', '%s');" % (item.sid, item.cid, data[item.sid]["name"], json.dumps(item.alsoKnownAs, separators=(',', ':')) if item.alsoKnownAs else "", json.dumps(item.flags, separators=(',', ':'))))
    else:
        print("---WARNING, item with sid=%d not no data!" % item.sid)