import copy

# Ops:
"""
    I: Item
    M: Monster
    MM: Multimonster
    T: Tile
    V: Alias for a precached (reference) version of T(I(100))
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

### Mainmap
class Map:
    def __init__(self, xA, yA, ground=100):
        self.area = {7:[]}
        self.size = (xA, yA)
        self._author = ""
        self._description = ""
        self.towns = {}
        self.waypoints = {}
        
        for x in xrange(0, xA+1):
            self.area[7].append([])
            for y in xrange(0, yA+1):
                self.area[7][x].append([])
                if ground == None:
                    self.area[7][x][y] = []
                elif isinstance(ground, int):
                    self.area[7][x][y] = [Item(ground)]
                else:
                    self.area[7][x][y] = [ground]

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
        if not level in self.area:
            self.area[level] = []
            for x in xrange(0, self.size[0]+1):
                self.area[level].append([])
                for y in xrange(0, self.size[1]+1):
                    self.area[level][x].append([])
                    if ground == None:
                        self.area[level][x][y] = []
                    elif isinstance(ground, int):
                        self.area[level][x][y] = [Item(ground)]
                    else:
                        self.area[level][x][y] = [ground]
                        
    def addTo(self,x,y,thing,level=7):
        self._level(level)
        self.area[level][x][y].append(thing)
        
    def add(self, thing):
        # Certain things like Tile() might want to add itself to a level beyond what we have generated so far
        self._level(thing.level)
        self.area[thing.level][thing.x][thing.y] = thing.area[thing.x][thing.y][thing.level]

    def _levelsTo(self, x, y): # Rather heavy!
        levels = []

        for level in self.area.keys():
            try:
                len(self.area[level][x][y]) # Raise a error, then it's skipped
                levels.append(level)
            except:
                pass
            
        return levels
    def compile(self, areas=(32,32)):
        print "--Begin compilation"
        areaX = 0
        areaY = 0
        toX = self.size[0] / areas[0]
        toY = self.size[1] / areas[1]
	nothingness = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        for xA in xrange(areaX, toX):
            for yA in xrange(areaY, toY):
                
                sector = {}
                extras = []
                
                for xS in xrange(0, areas[0]):
                    for yS in xrange(0, areas[1]):
                        for level in self._levelsTo((xA*areas[0])+xS, (yA*areas[1])+yS):
                            if not level in sector:
                                sector[level] = []

                            if len(sector[level]) <= xS:
                                sector[level].append([])
                            
                            if len(sector[level][xS]) <= yS:
                                sector[level][xS].append([])

                            for thing in self.area[level][(xA*areas[0])+xS][(yA*areas[1])+yS]:
                                e,extras = thing.gen((xA*areas[0])+xS, (yA*areas[1])+yS,level,xS,yS, extras)
                                if e:
                                    sector[level][xS][yS].append(e)
                
                # Begin by rebuilding ranges of tiles in x,y,z
                global opR
                opR = "m="
                def opM():
                    global opR
                    if opR == "m=":
                        opR = "+"
                        return "m="
                    return opR
                       
                # Level 3, y compare:
                def yComp(xCom):
                    yCom = []
                    yCount = 0
                    output = ""

                    for y in copy.copy(xCom):
                        if yCom == y:
                            yCount += 1
                            xCom.remove(y)
                        else:
                            if yCount > 1:
                                output += "(T("+(','.join(yCom))+"),)*%d+" % yCount
                            elif yCount:
                                output += "(T("+(','.join(yCom))+"),)+"
                            yCom = y
                            yCount = 1
                    if yCount > 1:
                        output += "(T("+(','.join(yCom))+"),)*%d+" % yCount
                    elif yCount:
                        output += "(T("+(','.join(yCom))+"),)+"
                        
                    return "("+output[:-1].replace("T()", "None").replace("T(I(100))", 'V')+",)" # None is waay faster then T(), T(I(100)) is also known as V
                
                # Level 2, X compare
                def xComp(zCom):
                    xCom = []
                    xCount = 0
                    output = ""
                    for x in copy.copy(zCom):
                        if xCom == x:
                            xCount += 1
                            zCom.remove(x)
                        else:
                            if xCount > 1:
                                # Begin building
                                output += yComp(xCom)+"*%d+" % xCount
                            elif xCount:
                                output += yComp(xCom)+"+"
                            xCom = x
                            xCount = 1

                    if xCount > 1:
                        output += yComp(xCom)+"*%d+" % xCount
                    elif xCount:
                        output += yComp(xCom)+"+"
                    
                    return output[:-1]
                
                output = ""
                for zPos in sector:
                    data = xComp(sector[zPos])
                    if data == "((None,)*%d,)*%d" % (areas[0], areas[1]): # Big load of nothing
                        print "--Note: %d is a level of nothingness, ignore it" % zPos
                        continue
		    else:
			if zPos in nothingness:
				nothingness.remove(zPos)
                    output += str(zPos)+":"+data+","
                if output:
                    output = "m={"+output[:-1]+"}"
                else: # A very big load of nothing
                    output = "m={}"
                
                if extras:
                    # Monster ops
                    # TODO: Reorder monsters first!
                    monsters = {}
                    monsterPos = {}
                    handled = {}
                    for x in extras:
                        if x[0] == "M":
                            args = list(x.split('(')[1].split(')')[0].split(','))
                            if len(args) == 3:
                                args.append('7')
                            
                            subs = args[0].split("'")
                            if not subs[1] in monsters:
                                monsters[subs[1]] = {}
                                monsterPos[subs[1]] = {}
                            if not args[3] in monsterPos[subs[1]]:
                                monsters[subs[1]][args[3]] = 1
                                monsterPos[subs[1]][args[3]] = [args[1], args[2]]
                            else:
                                monsters[subs[1]][args[3]] += 1
                                monsterPos[subs[1]][args[3]].append(args[1])
                                monsterPos[subs[1]][args[3]].append(args[2])
                                
                    # Run two, with new count 
                    for x in copy.copy(extras):
                        if x[0] == "M":
                            args = list(x.split('(')[1].split(')')[0].split(','))
                            if len(args) == 3:
                                args.append('7')
                            subs = args[0].split("'")
                            if monsters[subs[1]][args[3]] > 1:
                                if not args[3] in handled:
                                    handled[args[3]] = []
                                    
                                if not subs[1] in handled[args[3]]:
                                    extras[extras.index(x)] = "MM('%s',%s%s)" % ( subs[1], ','.join(monsterPos[subs[1]][args[3]]), ','+args[3] if int(args[3]) != 7 else '' )
                                    handled[args[3]].append(subs[1])
                                    curr = subs[1]
                                else:
                                    del extras[extras.index(x)]
                                    
                    output += "\ndef l():"+';'.join(extras)

                open('%d.%d.sec' % (xA, yA), 'w').write(output)
                
                print "--Wrote %d.%d.sec\n" % (xA, yA)
        output = ""
        output += "width = %d\n" % self.size[0]
        output += "height = %d\n" % self.size[1]
        output += "author = '%s'\n" % self._author
        output += "description = '%s'\n" % self._description
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
	print "Northingness on: %s" % (nothingness)
	output += "levels = (%d, %d)" % (num, low)        
        open('info.py', "w").write(output)
        print "---Wrote info.py"

### Areas
class Area:
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

class Tile:
    def __init__(self, x,y, ground=100, level=7):
        self.x = x
        self.y = y
        self.level = level
        if isinstance(ground, int):
            self.area = {x: {y: {level: [Item(ground)]}}}
        elif ground:
            self.area = {x: {y: {level: [ground]}}}
        else:
            self.area = {x: {y: {level: []}}}
    def add(self, thing):
        self.area[self.x][self.y][self.level].append(thing)
        
    def get(self): # Unique for tiles i presume
        return self.area[self.x][self.y][self.level]
        
### Things
class Item:
    def __init__(self, id):
        self.id = id
        self.attributes = {}
        self.actions = []
        
    def attribute(self, key, value):
        self.attributes[key] = value
    
    def action(self, id):
        self.actions.append(id)
    def gen(self, x,y,z,rx,ry,extras):
        extra = ""
        if self.actions:
            self.attributes["actions"] = self.actions
            
        if self.attributes:
            eta = []
            for key in self.attributes:
                eta.append("%s=%s" % (key, str(self.attributes[key]) if type(self.attributes[key]) != str else '"""%s"""' % self.attributes[key]))
                
            extra = ',%s' % ','.join(eta)
        return ('I(%d%s)' % (self.id, extra), extras)

class RSItem:
    def __init__(self, *argc):
        self.ids = argc
    def gen(self, x,y,z,rx,ry,extras):
        import random
        return ('I(%d)' % random.choice(self.ids), extras)    
class Monster:
    def __init__(self, name):
        self.name = name

            
    def gen(self, x,y,z,rx,ry, extras):
        extras.append("M('%s',%d,%d%s)" % (self.name, x, y, ',%d'%z if z != 7 else ''))
        return (None, extras)
       
