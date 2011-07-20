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
        
        #print "-- OTB version %d.%d (client: 9.0, build: %d)" % (majorVersion, minorVersion, buildVersion)
# Cheat the position to avoid junk
otb.pos = 13 + dataLen
items = []
lastRealItem = None

# A new node, the item nodes
if True:
    while otb.pos < otb.length:
        if otb.uint8() is not 0xFE: # this ain't suppose to happend, but if you fuck the file up, then sure :p
            b = otb.peekUint8()
            if b:
                print "DEBUG: Not 0xFE opening, next byte is: %d" % b
                continue
            else:
                break
        item = Item()
        item.type = otb.uint8()
        flags = otb.uint32()

        if (flags & 1) == 1:
            item.flags["solid"] = 1
        if (flags & 2) == 2:
            item.flags["blockprojectile"] = 1
        if (flags & 4) == 4:
            item.flags["blockpath"] = 1
        if (flags & 8) == 8:
            item.flags["hasheight"] = 1
        if (flags & 16) == 16:
            item.flags["usable"] = 1
        if (flags & 32) == 32:
            item.flags["pickable"] = 1
        if (flags & 64) == 64:
            item.flags["movable"] = 1
        if (flags & 128) == 128:
            item.flags["stackable"] = 1
        if (flags & 256) == 256:
            item.flags["ontop"] = 1
        if (flags & 512) == 512:
            item.flags["vertical"] = 1
        if (flags & 1024) == 1024:
            item.flags["horizontal"] = 1
        if (flags & 2048) == 2048:
            item.flags["hangable"] = 1
        if (flags & 4096) == 4096:
            item.flags["distanceread"] = 1
        if (flags & 8192) == 8192:
            item.flags["rotatable"] = 1
        if (flags & 16384) == 16384:
            item.flags["readable"] = 1
        if (flags & 32768) == 32768:
            item.flags["charges"] = 1
        if (flags & 65536) == 65536:
            item.flags["lookthrough"] = 1
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
            prep[attr.getAttribute("key")] = attr.getAttribute("value").replace("'", "\\'")
     if xId:
         data[int(xId)] = prep

     elif xFromId and xToId:
         for x in range(int(xFromId), int(xToId)+1):
             data[int(x)] = {"name":xName, "plural":xPlural, "article":xArticle}
             for attr in xAttributes:
                 try:
                    data[int(x)][attr.getAttribute("key")] = int(attr.getAttribute("value"))
                 except:
                    data[int(x)][attr.getAttribute("key")] = attr.getAttribute("value").replace("'", "\\'")
             
             
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
print "CREATE TABLE `items` ( \n\
`sid` SMALLINT NOT NULL,\n\
`cid` SMALLINT NOT NULL,\n\
`subtypes` TINYINT NOT NULL, \n\
`name` VARCHAR( 32 ) NOT NULL,\n\
`article` CHAR( 3 ) NOT NULL DEFAULT '',\n\
`plural` VARCHAR( 32 ) NOT NULL DEFAULT '',\n\
`speed` SMALLINT NOT NULL, \n\
`solid` BOOL NOT NULL DEFAULT 0,\n\
`blockprojectile` BOOL NOT NULL DEFAULT 0,\n\
`blockpath` BOOL NOT NULL DEFAULT 0,\n\
`hasheight` BOOL NOT NULL DEFAULT 0,\n\
`usable` BOOL NOT NULL DEFAULT 0,\n\
`pickable` BOOL NOT NULL DEFAULT 0,\n\
`movable` BOOL NOT NULL DEFAULT 0,\n\
`stackable` BOOL NOT NULL DEFAULT 0,\n\
`ontop` BOOL NOT NULL DEFAULT 0,\n\
`vertical` BOOL NOT NULL DEFAULT 0,\n\
`horizontal` BOOL NOT NULL DEFAULT 0,\n\
`hangable` BOOL NOT NULL DEFAULT 0,\n\
`distanceread` BOOL NOT NULL DEFAULT 0,\n\
`rotatable` BOOL NOT NULL DEFAULT 0,\n\
`readable` BOOL NOT NULL DEFAULT 0,\n\
`charges` BOOL NOT NULL DEFAULT 0,\n\
`lookthrough` BOOL NOT NULL DEFAULT 0,\n\
`custom` BOOL NOT NULL DEFAULT 0,\n\
PRIMARY KEY ( `sid` )\n\
) ENGINE = MYISAM; \n\
CREATE TABLE `item_attributes` ( \n\
`sid` SMALLINT NOT NULL ,\n\
`key` VARCHAR( 20 ) NOT NULL ,\n\
`value` VARCHAR( 64 ) NOT NULL ,\n\
`custom` BOOL NOT NULL DEFAULT '0'\n\
) ENGINE = MYISAM ;"
for item in items:
    if item.sid in data:
        # Dirty way to fix the attributes:
        #item.flags.update(data[item.sid])
        
        if "solid" in item.flags and "speed" in item.flags:
            del item.flags["speed"]

        print ("INSERT INTO items (`sid`, `cid`, `name`%s%s%s%s) VALUES(%d, %d, '%s'%s%s%s%s);" % (', `article`' if data[item.sid]["article"] else '', ', `plural`' if data[item.sid]["plural"] else '',', `subtypes`' if item.alsoKnownAs else '', ', `'+"`, `".join(item.flags.keys())+'`' if item.flags else '', item.sid, item.cid, data[item.sid]["name"].replace("'", "\\'"), ", '"+data[item.sid]["article"]+"'" if data[item.sid]["article"] else '', ", '"+data[item.sid]["plural"].replace("'", "\\'")+"'" if data[item.sid]["plural"] else '', ", "+str(len(item.alsoKnownAs)) if item.alsoKnownAs else '', ", '"+"', '".join(map(str, item.flags.values()))+"'" if item.flags else '')).encode("utf-8")

        del data[item.sid]["name"]
        del data[item.sid]["plural"]
        del data[item.sid]["article"]
        
        if data[item.sid]:
            print "INSERT INTO item_attributes (`sid`, `key`, `value`) VALUES"
            k = False
            for key in data[item.sid]:
                print "%s(%d, '%s', '%s')" % (',' if k else '', item.sid, key, data[item.sid][key])
                if not k:
                    k = True
            print ';'
        print ''
        #print(("INSERT INTO items VALUES(%d, %d, '%s', '%s', '%s', %s, %s);" % (item.sid, item.cid, data[item.sid]["name"].replace("'", "\\'"), article, plural.replace("'", "\\'"), "'"+json.dumps(item.alsoKnownAs, separators=(',', ':'))+"'" if item.alsoKnownAs else "NULL", "'"+json.dumps(item.flags, separators=(',', ':')).replace("'", "\\'")+"'" if item.flags else "NULL")).encode("utf-8"))
    #else:
    #    print("---WARNING, item with sid=%d not no data!" % item.sid)
