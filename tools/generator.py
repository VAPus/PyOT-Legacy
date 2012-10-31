import copy
import sys
sys.path.append('../')
import config
import MySQLdb
import struct
import io

### Load all solid and movable items
topitems = set()
movable = set()
db = MySQLdb.connect(host=config.sqlHost, user=config.sqlUsername, passwd=config.sqlPassword, db=config.sqlDatabase)
cursor = db.cursor()
cursor.execute("SELECT sid FROM items WHERE ontop = 1")
for row in cursor.fetchall():
    topitems.add(row[0])
cursor.close()

cursor = db.cursor()
cursor.execute("SELECT sid FROM items WHERE movable = 1")
for row in cursor.fetchall():
    movable.add(row[0])
cursor.close()

db.close()
    
# Format (Work in Progress):
"""
    <uint8>floor_level
    floorLevel < 60
        <loop>32x32

        <uint16>itemId
        <uint8>attributeCount / other
        
        itemId >= 100:
            every attributeCount (
                See attribute format
            )

        itemId == 50:
            <int32> Tile flags
            
        itemId == 51:
            <uint32> houseId
            
        itemId == 0:
            skip attributeCount fields
            
        {
            ; -> go to next tile
            | -> skip the remaining y tiles
            ! -> skip the remaining x and y tiles
            , -> more items
        }
        
    floorLevel == 60:
        <uint16>center X
        <uint16>center Y
        <uint8>center Z
        <uint8> Radius from center creature might walk
        <uint8> count (
            <uint8> type (61 for Monster, 62 for NPC)
            <uint8> nameLength
            <string> Name
             
            <int8> X from center
            <int8> Y from center
                
            <uint16> spawntime in seconds
                       
            }
        )
    Attribute format:
    
    {
        <uint8>attributeId
        <char>attributeType
        {
            attributeType == i (
                <int32>value
            )
            attributeType == s (
                <uint16>valueLength
                <string with length valueLength>value
            )
            attributeType == b (
                <bool>value
            )
            attributeType == l (
                <uint8>listItems
                <repeat this block for listItems times> -> value
            )
        }
        
        
    }
"""

### Behavior
def replacer(old, new):
    if new:
        return new
    return old
    
def keeper(old, new):
    if old:
        return old
    return new

def merger(old, new):
    for i in new:
        old.append(i)
    return old
    
# I replace ground, and put old stuff onto new ground
def iReplacer(old, new):
    old[0] = new[0]
    if len(new) > 1:
        for i in new[1:]:
            old.append(i)
    return old

# Python 3
try:
    xrange()
except:
    xrange = range
    
class Map(object):
    def __init__(self, xA, yA, ground=100, zs=16):
        self.levels = zs
        self.size = [xA, yA]
        self._author = ""
        self._description = ""
        self.towns = {}
        self.waypoints = {}
        self.houses = {}
        self.flags = {}
        self.DICT_MODE = False

        # Level 7 always got to be filled up.
        self.area = {7:[]}
        if ground != None and not isinstance(ground, Item):
            ground = Item(ground)

        if ground != None:
            for x in xrange(0, xA+1):
                self.area[7].append([])
                for y in xrange(0, yA+1):
                    self.area[7][x].append([])
                    if ground == None:
                        self.area[7][x][y] = None
                    else:
                        self.area[7][x][y] = [ground]
        else:
            self.area[7] = []

    def author(self, name):
        self._author = name
    
    def description(self, desc):
        self._description = desc
        
    def town(self, id, name, pos):
        self.towns[id] = (name, pos)
        
    def waypoint(self, name, pos):
        self.waypoints[name] = pos
        
    def merge(self, obj, offsetX, offsetY, overrideLevel=None):
        xO = offsetX
        yO = offsetY
        if not (7 if not overrideLevel else overrideLevel) in self.area:
            self.area[7 if not overrideLevel else overrideLevel] = []
        for x in obj.area:
            for y in x:
                for z in y:
                    self.area[7 if not overrideLevel else overrideLevel][xO][yO] = y[z]

                yO += 1
            yO = offsetY
            xO += 1

    def _level(self, level, ground=None):
        try:
            self.area[level]
        except:
            self.area[level] = []
            """for x in xrange(0, self.size[0]+1):
                self.area[level].append([])
                for y in xrange(0, self.size[1]+1):
                    self.area[level][x].append([])
                    if ground == None:
                        self.area[level][x][y] = None
                    elif isinstance(ground, int):
                        self.area[level][x][y] = [Item(ground)]
                    else:
                        self.area[level][x][y] = [ground]
            """
    def _ensureRange(self, x,y,z):
        try:
            self.area[z][x][y]
            return
        except:
            self._level(z)
            
            lX = len(self.area[z]) - 1
            diffX = x - lX
            if diffX > 0:
                for n in xrange(diffX):
                    self.area[z].append(None)
            
            try:
                lY = len(self.area[z][x]) -1
            except:
                self.area[z][x] = []
                lY = -1
                
            diffY = y - lY

            if diffY > 0:
                for n in xrange(diffY):
                    if not isinstance(self.area[z][x], list):
                        self.area[z][x] = []
                    self.area[z][x].append(None) # Dealth with in addTo
                
            if self.size[0] < x:
                self.size[0] = x
                
            if self.size[1] < y:
                self.size[1] = y
            
    def addTo(self,x,y,thing,level=7):
        self._ensureRange(x,y,level)
        
        if type(thing) != list:
            try:
                self.area[level][x][y].append(thing)
            except:
                self.area[level][x][y] = [thing]
        else:
            self.area[level][x][y] = thing
                
    def add(self, thing):
        # Certain things like Tile() might want to add itself to a level beyond what we have generated so far
        try:
            if isinstance(thing, Tile):
                self._ensureRange(thing.pos[0], thing.pos[1], thing.pos[2])
                self.area[thing.pos[2]][thing.pos[0]][thing.pos[1]] = thing.area
            else:
                self._ensureRange(thing.x, thing.y, thing.level)
                self.area[thing.level][thing.x][thing.y] = thing.area[thing.x][thing.y][thing.level]
        except:
            
            self.size = (thing.x if thing.x > self.size[0] else self.size[0], thing.y if thing.y > self.size[1] else self.size[1])
            while True:
                try:
                    self.area[thing.level][thing.x]
                    break
                except:
                    self.area[thing.level].append([])
            while True:
                try:
                    self.area[thing.level][thing.x][thing.y]
                    break
                except:
                    self.area[thing.level][thing.x].append([])                
            self.area[thing.level][thing.x][thing.y] = thing.area[thing.x][thing.y][thing.level]
    def _levelsTo(self, x, y): # Rather heavy!
        levels = []
        for level in list(self.area.keys()):
            try:
                if self.area[level][x][y]: # Raise a error, then it's skipped
                    levels.append(level)
            except:
                pass

        return levels
    def compile(self, areas=(32,32)):
        print("--Begin compilation")
        areaX = 0
        areaY = 0
        toX = int(self.size[0] / areas[0])
        toY = int(self.size[1] / areas[1])
        nothingness = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        doubleNull = chr(0) + chr(0)
        trippelNull = chr(0) * 3
        HiFormat = struct.Struct("<Hi")
        
        for xA in xrange(areaX, toX):
            for yA in xrange(areaY, toY):
                
                sector = {}
                extras = []
                
                for xS in xrange(0, areas[0]):
                    for yS in xrange(0, areas[1]):
                        for level in self._levelsTo((xA*areas[0])+xS, (yA*areas[1])+yS):
                            if self.area[level][(xA*areas[0])+xS][(yA*areas[1])+yS] == None:
                                continue
                            
                            if not level in sector:
                                sector[level] = []
                                for _x in xrange(areas[0]):
                                    sector[level].append([])
                                    for _y in xrange(areas[1]):
                                        sector[level][_x].append([])
                                        sector[level][_x][_y] = []

                            if len(self.area[level][(xA*areas[0])+xS][(yA*areas[1])+yS]) > 1:
                                # Reorder
                                insert = 1
                                for thing in self.area[level][(xA*areas[0])+xS][(yA*areas[1])+yS][1:]:
                                    if isinstance(thing, Item):
                                        if thing.id in topitems:
                                            self.area[level][(xA*areas[0])+xS][(yA*areas[1])+yS].remove(thing)
                                            self.area[level][(xA*areas[0])+xS][(yA*areas[1])+yS].insert(insert, thing)
                                            insert += 1
                                
                            for thing in self.area[level][(xA*areas[0])+xS][(yA*areas[1])+yS]:
                                e,extras = thing.gen((xA*areas[0])+xS, (yA*areas[1])+yS,level,xS,yS, extras)
                                if e:
                                    sector[level][xS][yS].append(e)

                # Begin by rebuilding ranges of tiles in x,y,z
                       
                # Level 3, y compare:
                def yComp(xCom, z, x):
                    output = []
                    row = 0
                    nullRows = 0
                    
                    for y in xCom:
                        pos = (x+(xA*areas[0]),row+(yA*areas[1]),z)

                        if y:
                            if nullRows:
                                output.append(doubleNull + chr(nullRows))
                                nullRows = 0
                                
                            if pos in self.houses:
                                y.append(HiFormat.pack(50, self.houses[pos]))
                                if not pos in self.flags:
                                    self.flags[pos] = 1
                                elif not self.flags[pos] & 1:
                                    self.flags[pos] += 1
                                    
                            if pos in self.flags:
                                y.append(HiFormat.pack(51, self.flags[pos]))

                            output.append(','.join(y))
                        else:
                            nullRows += 1
                        

                        row += 1
                    if nullRows:
                        output.append(doubleNull + chr(nullRows))
   
                    if output:
                        # Apply skipping if necessary
                        data = ';'.join(output)
                        
                        # A walk in the park to remove the aditional 0 stuff here
                        count = 0
                        for code in output[::-1]:
                            if code == trippelNull: count += 1
                            else: break
      
                        if count:
                            output = output[:len(output)-count]
                            
                            if not output:
                                return "\x00\x00\x00|"
                            
                            data = ';'.join(output) 
                        else:    
                            data = data

                        return data + "|"
                    else:
                        return "\x00\x00\x00|"
                    
                # Level 2, X compare
                def xComp(zCom, z):
                    output = []
                    row = 0
                    for x in zCom:
                        t = yComp(x, z, row)
                        if t:
                            output.append(t)

                        row += 1
                    if not output:
                        return None
                    else:
                        # A walk in the park to remove the aditional 0 stuff here
                        count = 0
                        remove = trippelNull + '|'
                        for code in output[::-1]:
                            if code == remove: count += 1
                            else: break
                                
                        if count:
                            output = output[:len(output)-count]
                            
                        if not output:
                            return None
                            
                        output[-1] = output[-1][:len(output[-1])-1] + "!" # Change ;/| -> !
                        
                    #if not noRows >= areas[0]:
                    return ''.join(output)
                
                output = []
                for zPos in sector:
                    data = xComp(sector[zPos], zPos)
                    if data:
                        if zPos in nothingness:
                            nothingness.remove(zPos)
                        output.append("%s%s" % (chr(zPos), data))

                if extras:
                    output.append(''.join(extras))
                if output:
                    output = ''.join(output)
                    with io.open('%d.%d.sec' % (xA, yA), 'wb') as f:
                        f.write(output)
                    print("--Wrote %d.%d.sec\n" % (xA, yA))
                    
                else: # A very big load of nothing
                    print("--Skipped %d.%d.sec\n" % (xA, yA))
                    continue

                    
                        
                
                    
                    
        output = ""
        output += "width = %d\n" % self.size[0]
        output += "height = %d\n" % self.size[1]
        output += "author = '%s'\n" % self._author
        output += 'description = """%s"""\n' % self._description
        output += "sectorSize = (%d, %d)\n" % (areas[0], areas[1])
        output += "towns = %s\n" % str(self.towns)
        output += "waypoints = %s\n" % str(self.waypoints)
        low = 15
        num = 0
        for level in self.area:
            if level in nothingness:
                continue
            if level < low:
                low = level
        num += 1
        print("Northingness on: %s" % (nothingness))
        output += "levels = (%d, %d)" % (num, low)
        with open('info.py', "w") as f:
            f.write(output)
        print("---Wrote info.py")

### Areas
class Area(object):
    __slots__ = ('level', 'area')
    def __init__(self, xA, yA, ground=100, level=7):
        self.level = level
        self.area = []
        for x in xrange(0, xA+1):
            self.area.append([])
            for y in xrange(0, yA+1):
                if isinstance(ground, int):
                    self.area[x].append({level: [Item(ground)]})
                else:
                    self.area[x].append({level: [ground]})

    def add(self, x,y,thing):
        self.area[x][y][self.level].append(thing)
        
    def merge(self, obj, offsetX, offsetY):
        for x in obj.area:
            for y in obj.area[x]:
                for z in obj.area[x][y]:
                    self.area[x+offsetX][y+offsetY][self.level] = obj.area[x][y][z] 

    def border(self, offset=0, north=None,south=None,east=None,west=None,northeast=None,northwest=None,southeast=None,southwest=None,behavior=iReplacer):
        # Run East
        if east:
            for sideY in self.area[offset][offset:(offset*-1)-1]:
                sideY[self.level] = behavior(sideY[self.level], east if isinstance(east, tuple) else [east])
        
        # Run West
        if west:
            for sideY in self.area[(offset*-1)-1][offset:(offset*-1)-1]:
                sideY[self.level] = behavior(sideY[self.level], west if isinstance(west, tuple) else [west])
                
        # Run North
        if north:
            for sideX in self.area[offset:(offset*-1)-1]:
                sideX[offset][self.level] = behavior(sideX[offset][self.level], north if isinstance(east, tuple) else [north])
        
        # Run South
        if south:
            for sideX in self.area[offset:(offset*-1)-1]:
                sideX[(offset*-1)-1][self.level] = behavior(sideX[(offset*-1)-1][self.level], south if isinstance(south, tuple) else [south])
                
        # Run northeast
        if northeast:
            self.area[(offset*-1)-1][offset][self.level] = behavior(self.area[(offset*-1)-1][offset][self.level], northeast if isinstance(northeast, tuple) else [northeast])
            
        # Run southeast
        if southeast:
            self.area[(offset*-1)-1][(offset*-1)-1][self.level] = behavior(self.area[(offset*-1)-1][(offset*-1)-1][self.level], southeast if isinstance(southeast, tuple) else [southeast])
            
        # Run northwest
        if northwest:
            self.area[offset][offset][self.level] = behavior(self.area[offset][offset][self.level], northwest if isinstance(northwest, tuple) else [northwest])
            
        # Run southwest
        if southwest:
            self.area[offset][(offset*-1)-1][self.level] = behavior(self.area[offset][(offset*-1)-1][self.level], southewst if isinstance(southwest, tuple) else [southwest])     

class Tile(object):
    __slots__ = ('area', 'pos')
    def __init__(self, x,y, ground=100, level=7):
        self.pos = (x,y,level)
        
        if isinstance(ground, int):
            self.area = [Item(ground)]
        elif ground:
            self.area = [ground]
        else:
            self.area = None
        
    def add(self, thing):
        self.area.append(thing)
        
    def get(self): # Unique for tiles i presume
        return self.area

                
### Things
class Item(object):
    __slots__ = ('id', 'attributes', 'actions')
    attributeIds = ('actions', 'count', 'solid','blockprojectile','blockpath','usable','pickable','movable','stackable','ontop','hangable','rotatable','animation', 'doorId', 'depotId', 'text', 'written', 'writtenBy', 'description', 'teledest')
    def __init__(self, id):
        self.id = id
        self.attributes = {}
        self.actions = []
        
    def attribute(self, key, value):
        attrId = self.attributeIds.index(key)
        
        self.attributes[attrId] = value
    
    def action(self, id):
        self.actions.append(id)

    # Attribute writer function. Needs to be a function so it can call itself in case of a list.
    def writeAttribute(self, name, value):
        # Only toplevel attributes got a name, since we're called from a list too, we need to verify this one.
        if name != None:
            string = chr(name)
        else:
            string = ''
        
        # Is the value a number?
        if isinstance(value, int):
            string += "i" + struct.pack("<i", value)
            
        # A string?
        elif isinstance(value, str):
            string += "s" + struct.pack("<i", len(value)) + value
            
        # A bool?
        elif isinstance(value, bool):
            string += "b" + chr(value)
            
        # Or a list (actions etc)
        elif isinstance(value, list) or isinstance(value, tuple):
            string += "l" + chr(len(value))
            for attr in value:
                string += self.writeAttribute(None, attr)
                
        return string
    
    def gen(self, x,y,z,rx,ry,extras):
        code = struct.pack("<H", self.id)

        if self.actions:
            self.attributes[0] = self.actions
        
        if self.id in movable:
            print ("Notice: Movable item (ID: %d) on (%d,%d,%d) have been unmovabilized" % (self.id, x,y,z))
            self.attributes[7] = False
        
        
        if self.attributes:
            eta = []
            for key in self.attributes:
                eta.append(self.writeAttribute(key, self.attributes[key]))
            code += chr(len(eta))
            code += ''.join(eta)
        else:
            code += "\x00"
        return code, extras


class RSItem(object):
    __slots__ = ('ids')
    def __init__(self, *argc):
        self.ids = argc
    def gen(self, x,y,z,rx,ry,extras):
        import random
        return ('I(%d)' % random.choice(self.ids), extras) 

class Spawn(object):
    __slots__ = ('radius', 'cret', 'center')
    def __init__(self, radius, centerPoint):
        self.radius = radius
        self.cret = []
        self.center = centerPoint
    def monster(self, name,x,y,z, spawntime):
        self.cret.append(chr(61) + chr(len(name)) + name + struct.pack("<bbH", x, y, spawntime))
        
    def npc(self, name,x,y,z, spawntime):
        self.cret.append(chr(62) + chr(len(name)) + name + struct.pack("<bbH", x, y, spawntime))
        
    def gen(self, x,y,z,rx,ry, extras):
        if self.cret:
            #extras.append( "%s.%s" % ("S(%d,%d%s%s)" % (self.center[0], self.center[1], ',%d'%z if z != 7 or self.radius != 5 else '', ",%d"%self.radius if self.radius != 5 else ''), '.'.join(self.cret)) )
            code = struct.pack("<BHHBBB", 60, self.center[0], self.center[1], z, self.radius, len(self.cret)) # opCode + amount of creatures + radius
            extras.append(code + ''.join(self.cret))
            return (None, extras)
        return (None, extras)
        
       
