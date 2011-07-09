#!/usr/bin/env python
# -*- coding: latin-1 -*-

import struct, sys

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
        self.alsoKnownAs = []
        self.junk = False
otbFile = open("items.otb")
otb = Reader(otbFile.read())

# This file is somewhat designed as a XMl file



# Now, we could naturally just read shit, but some idiot figured we should use some junky escape system in the file, since we don't, we just got to remove the escape system entierly
# This code is probably 50%+ of the entier execution time
nLen = 0
nData = b""
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
        majorVersion = otb.uint32()
        minorVersion = otb.uint32()
        buildVersion = otb.uint32()
        
        print "-- OTB version %d.%d (client: 9.0, build: %d)" % (majorVersion, minorVersion, buildVersion)
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

        if (flags & 1) == 1:
            item.flags["solid"] = True
        if (flags & 2) == 2:
            item.flags["blockprojectile"] = True
        if (flags & 4) == 4:
            item.flags["blockpath"] = True
        if (flags & 8) == 8:
            item.flags["hasheight"] = True
        if (flags & 16) == 16:
            item.flags["usable"] = True
        if (flags & 32) == 32:
            item.flags["pickable"] = True
        if (flags & 64) == 64:
            item.flags["movable"] = True
        if (flags & 128) == 128:
            item.flags["stackable"] = True
        if (flags & 256) == 256:
            item.flags["ontop"] = True
        if (flags & 512) == 512:
            item.flags["vertical"] = True
        if (flags & 1024) == 1024:
            item.flags["horizontal"] = True
        if (flags & 2048) == 2048:
            item.flags["hangable"] = True
        if (flags & 4096) == 4096:
            item.flags["distanceread"] = True
        if (flags & 8192) == 8192:
            item.flags["rotatable"] = True
        if (flags & 16384) == 16384:
            item.flags["readable"] = True
        if (flags & 32768) == 32768:
            item.flags["charges"] = True
        if (flags & 65536) == 65536:
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
                    item.flags["speed"] = otb.uint16()
                elif attr is 0x37:
                    item.flags["order"] = otb.uint8()
                else:
                    if attr is 0xFE:
                        otb.pos -= 4
                        break
                    else:
                        otb.pos += datalen
                    
        except:
            pass
        try:
            otb.uint8() # 0xFF
        except:
            pass
             # Fix a bug with last closing
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
     xArticle = xItem.getAttribute("article")
     xPlural = xItem.getAttribute("plural")
     xAttributes = xItem.getElementsByTagName("attribute")

     prep = {"name":xName, "plural":xPlural, "article":xArticle}
     for attr in xAttributes:
         try:
            prep[attr.getAttribute("key")] = int(attr.getAttribute("value"))
         except:
            prep[attr.getAttribute("key")] = attr.getAttribute("value")
     if xId:
         data[int(xId)] = prep

     elif xFromId and xToId:
         for x in range(int(xFromId), int(xToId)+1):
             data[int(x)] = prep
             
#print data
# Current suggested format:
# sid, cid, name, refids, flags, description, weight, worth, slot, duration, decayTo, floorchange
#id = raw_input("ID? ")
id = 0
if id:
    for item in items:
        if item.sid is id:
            items = [item]
            break

import copy
print "CREATE TABLE IF NOT EXISTS `items` (`sid` INT( 8 ) NOT NULL ,`cid` INT( 8 ) NOT NULL ,`name` VARCHAR( 32 ), `article` VARCHAR(3), `plural` VARCHAR( 32 ) ,`known_as` MEDIUMTEXT NULL DEFAULT NULL ,`attributes` TEXT NULL DEFAULT NULL ,PRIMARY KEY ( `sid` ) ,INDEX ( `cid` )) ENGINE = MYISAM ;"
for item in items:
    if item.sid in data:
        # Dirty way to fix the attributes:
        item.flags.update(data[item.sid])
        if "name" in item.flags:
            del item.flags["name"]
        
        if "solid" in item.flags and "speed" in item.flags:
            del item.flags["speed"]
            
        article = ""
        if "article" in item.flags:
            article = copy.deepcopy(item.flags["article"])
            del item.flags["article"]
        
        plural = ""
        if "plural" in item.flags:
            plural = copy.deepcopy(item.flags["plural"])
            del item.flags["plural"]            
        print(("INSERT INTO items VALUES(%d, %d, '%s', '%s', '%s', %s, %s);" % (item.sid, item.cid, data[item.sid]["name"].replace("'", "\\'"), article, plural.replace("'", "\\'"), "'"+json.dumps(item.alsoKnownAs, separators=(',', ':'))+"'" if item.alsoKnownAs else "NULL", "'"+json.dumps(item.flags, separators=(',', ':')).replace("'", "\\'")+"'" if item.flags else "NULL")).encode("utf-8"))
    #else:
    #    print("---WARNING, item with sid=%d not no data!" % item.sid)
