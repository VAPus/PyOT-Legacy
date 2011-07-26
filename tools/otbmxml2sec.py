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

class L:
    def __init__(self, val):
        self.value = val
        
class Node:
    def __init__(self, otbm, level):
        self.data = b""
        self.nodes = []
        byte = otbm.uint8()
        nextIsEscaped = False
        while byte != None:
            if byte == 0xFE and not nextIsEscaped:
                node = self.handleBlock(otbm, level)

            elif byte == 0xFF and not nextIsEscaped:
                level.value -= 1
                if level.value < 0:
                    print "DEBUG!"
                break
                
            elif byte == 0xFD and not nextIsEscaped:
                nextIsEscaped = True
                
            else:
                nextIsEscaped = False 
                self.data += struct.pack("<B", byte)
                
            byte = otbm.uint8()
        self.data = Reader(self.data)
    def handleBlock(self, otbm, level):
        level.value += 1
        node = Node(otbm, level)
        self.nodes.append(node)
        return node
        
    def next(self):
        if self.nodes:
            return self.nodes.pop(0)
        else:
            return None

_map_ = []
        
otbmFile = open("map.otbm")
otbm = Reader(otbmFile.read())

otbm.pos += 5
root = Node(otbm, L(1)) # Begin on level 1
root.data.pos += 1

version = root.data.uint32()
width = root.data.uint16()
height = root.data.uint16()
majorVersionItems = root.data.uint32()
minorVersionItems = root.data.uint32()

# Prepopulate _map_
print "OTBM v%d, %dx%d" % (version, width, height) 
_map_ = [[{}]*height]*width

nodes = root.next()
nodes.data.pos += 1
description = ""
spawns = ""
house = ""

while nodes.data.peekUint8():
    attr = nodes.data.uint8()
    if attr == 1:
        description = nodes.data.string()
        print description+"\n"
    elif attr == 11:
        spawns = nodes.data.string()
    elif attr == 13:
        house = nodes.data.string()
    else:
        print "Unknown nodes data"

node = nodes.next()

while node:
    type = node.data.uint8()
    if type == 4: # Tile area
        baseX = node.data.uint16()
        baseY = node.data.uint16()
        baseZ = node.data.uint8()
        
        tile = node.next()
        while tile:
            tileType = tile.data.uint8()
            if tileType == 5 or tileType == 14: # Tile
                tileX = tile.data.uint8() + baseZ
                tileY = tile.data.uint8() + baseY
                if tileType == 14:
                    # TODO
                    tile.data.uint32()
                    
                # Attributes
                while tile.data.peekUint8():
                    attr = tile.data.uint8()
                    if attr == 3: # OTBM_ATTR_TILE_FLAGS
                        flags = tile.data.uint32() # TODO, parse those
                        
                    elif attr == 9: # ITEM, ground item
                        itemId = tile.data.uint16() # TODO, parse item
                        
                    else:
                        print "Unknown tile attrubute"
                        
                
                item = tile.next()
                while item:
                    if item.data.uint8() == 6: # more items
                        itemId = item.data.uint16()
                        
                        # Unserialie attributes
                        while item.data.peekUint8():
                            attr = item.data.uint8()
                            if attr == 10: # depotId
                                item.data.uint16() # TODO: care?
                            elif attr == 14: # houseDoorId
                                item.data.uint8() # TODO: care? We can autodetect it
                            elif attr == 20: # Sleeperguid
                                item.data.uint32() # TODO: care?
                            elif attr == 21: # sleepstart
                                item.data.uint32()
                            elif attr == 8: # Teleport destination
                                teleDest = [item.data.uint16(),item.data.uint16(),item.data.uint8()]
                            elif attr == 15: # Item count
                                count = item.data.uint8()
                            elif attr == 4: # action id
                                actionId = item.data.uint16()
                            elif attr == 5:
                                uniqueId = item.data.uint16() # We don't support this
                            elif attr == 6:
                                text = item.data.string()
                            elif attr == 18:
                                writtenDate = item.data.uint32()
                            elif attr == 19:
                                writenBy = item.data.string()
                            elif attr == 7:
                                specialDescription = item.data.string() # It will probably work diffrently
                            elif attr == 12:
                                runeCharges = item.data.uint8()
                            elif attr == 22:
                                charges = item.data.uint8()
                            elif attr == 16:
                                duration = item.data.uint32()
                            elif attr == 17:
                                decayState = item.data.uint8()
                            elif attr == 23:
                                count = item.data.uint32()
                                break # All after this is container items
                            else:
                                print "Unknown item attribute %d" % attr
                                
                    else:
                        print "Unknown item header"
                    item = tile.next()
            else:
                print "Unknown tile node"
            tile = node.next()
            
    elif type == 12: # Towns
        town = node.next()
        
        while town:
            townType = town.data.uint8()
            if townType == 13:
                townId = town.data.uint32()
                townName = town.data.string()
                temple = [town.data.uint16(),town.data.uint16(),town.data.uint8()]
            else:
                print "Unknown town node"
                
            town = node.next()
            
            
    elif type == 15 and version >= 2: # Waypoints
        waypoint = node.next()
        
        while waypoint:
            waypointType = waypoint.data.uint8()
            if waypointType == 16:
                name = waypoint.data.string()
                cords = [waypoint.data.uint16(),waypoint.data.uint16(),waypoint.data.uint8()]
            else:
                print "Unknown waypoint type"
            waypoint = node.next()
    node = nodes.next()
print "DONE!"    