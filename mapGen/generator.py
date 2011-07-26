import copy

# Ops:
"""
    I: Item
    M: Monster
    MM: Multimonster
"""

# Behavior
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
    
class Map:
    def __init__(self, xA, yA, ground=100):
        self.area = {7:[]}
        self.size = (xA, yA)
        
        for x in xrange(0, xA+1):
            self.area[7].append([])
            for y in xrange(0, yA+1):
                self.area[7][x].append([])
                if isinstance(ground, int):
                    self.area[7][x][y] = [Item(ground)]
                else:
                    self.area[7][x][y] = [ground]

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
    def add(x,y,thing,level=7):
        self.area[x][y][level].append(gen)
        
    def compile(self, areas=(32,32)):
        areaX = 0
        areaY = 0
        toX = self.size[0] / areas[0]
        toY = self.size[1] / areas[1]

        for xA in xrange(areaX, toX):
            for yA in xrange(areaY, toY):
                
                sector = {7:[]}
                extras = []
                for xS in xrange(0, areas[0]):
                    sector[7].append([])
                    for yS in xrange(0, areas[1]):
                        sector[7][xS].append([])
                        for thing in self.area[7][(xA*areas[0])+xS][(yA*areas[1])+yS]:
                            e,extras = thing.gen((xA*areas[0])+xS, (yA*areas[1])+yS,7,xS,yS, extras)
                            if e:
                                sector[7][xS][yS].append(e)
                
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
                                output += str([yCom]).replace(': ', ':').replace(', ', ',').replace("'I", 'I').replace(")'", ')')+"*%d+" % yCount
                            elif yCount:
                                output += str([yCom]).replace(': ', ':').replace(', ', ',').replace("'I", 'I').replace(")'", ')')+"+"
                            yCom = y
                            yCount = 1
                    if yCount > 1:
                        output += str([yCom]).replace(': ', ':').replace(', ', ',').replace("'I", 'I').replace(")'", ')')+"*%d+" % yCount
                    elif yCount:
                        output += str([yCom]).replace(': ', ':').replace(', ', ',').replace("'I", 'I').replace(")'", ')')+"+"
                    return "["+output[:-1]+"]"
                
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
                
                output = "{"
                for zPos in sector:
                    output += "7:"+xComp(sector[zPos])
                output += "}"
                output = "m="+output
                
                if extras:
                    # Monster ops
                    # TODO: Reorder monsters first!
                    monsters = {}
                    monsterPos = {}
                    handled = []
                    for x in extras:
                        if x[0] == "M":
                            args = x.split('(')[1].split(')')[0].split(',')
                            if len(args) > 3:
                                # TODO: Diffrent ground level then 7
                                continue
                            
                            subs = args[0].split("'")
                            if not subs[1] in monsters:
                                monsters[subs[1]] = 1
                                monsterPos[subs[1]] = [args[1], args[2]]
                            else:
                                monsters[subs[1]] += 1
                                monsterPos[subs[1]].append(args[1])
                                monsterPos[subs[1]].append(args[2])
                    # Run two, with new count 
                    for x in copy.copy(extras):
                        if x[0] == "M":
                            subs = x.split("'")
                            if monsters[subs[1]] > 1:
                                
                                if not subs[1] in handled:
                                    extras[extras.index(x)] = "MM('%s',%s)" % ( subs[1], ','.join(monsterPos[subs[1]]) )
                                    handled.append(subs[1])
                                    curr = subs[1]
                                else:
                                    del extras[extras.index(x)]
                                    
                    output += "\ndef l():"+';'.join(extras)

                open('%d.%d.sec' % (xA, yA), 'w').write(output)
        
class Area:
    def __init__(self, xA, yA, ground=100, level=7):
        self.z = level
        self.area = []
        for x in xrange(0, xA+1):
            self.area.append([])
            for y in xrange(0, yA+1):
                if isinstance(ground, int):
                    self.area[x].append({level: [Item(ground)]})
                else:
                    self.area[x].append({level: [ground]})
    def add(self, x,y,thing):
        self.area[x][y][self.z].append(thing)
        
    def merge(self, obj, offsetX, offsetY):
        for x in obj.area:
            for y in obj.area[x]:
                for z in obj.area[x][y]:
                    self.area[x+offsetX][y+offsetY][self.z] = obj.area[x][y][z] 

    def border(self, offset=0, north=None,south=None,east=None,west=None,northeast=None,northwest=None,southeast=None,southwest=None,behavior=iReplacer):
        # Run East
        if east:
            for sideY in self.area[offset][offset:(offset*-1)-1]:
                sideY[self.z] = behavior(sideY[self.z], east if isinstance(east, tuple) else [east])
        
        # Run West
        if west:
            for sideY in self.area[(offset*-1)-1][offset:(offset*-1)-1]:
                sideY[self.z] = behavior(sideY[self.z], west if isinstance(west, tuple) else [west])
                
        # Run North
        if north:
            for sideX in self.area[offset:(offset*-1)-1]:
                sideX[offset][self.z] = behavior(sideX[offset][self.z], north if isinstance(east, tuple) else [north])
        
        # Run South
        if south:
            for sideX in self.area[offset:(offset*-1)-1]:
                sideX[(offset*-1)-1][self.z] = behavior(sideX[(offset*-1)-1][self.z], south if isinstance(south, tuple) else [south])
                
        # Run northeast
        if northeast:
            self.area[(offset*-1)-1][offset][self.z] = behavior(self.area[(offset*-1)-1][offset][self.z], northeast if isinstance(northeast, tuple) else [northeast])
            
        # Run southeast
        if southeast:
            self.area[(offset*-1)-1][(offset*-1)-1][self.z] = behavior(self.area[(offset*-1)-1][(offset*-1)-1][self.z], southeast if isinstance(southeast, tuple) else [southeast])
            
        # Run northwest
        if northwest:
            self.area[offset][offset][self.z] = behavior(self.area[offset][offset][self.z], northwest if isinstance(northwest, tuple) else [northwest])
            
        # Run southwest
        if southwest:
            self.area[offset][(offset*-1)-1][self.z] = behavior(self.area[offset][(offset*-1)-1][self.z], southewst if isinstance(southwest, tuple) else [southwest])     

class Item:
    def __init__(self, id):
        self.id = id
    def gen(self, x,y,z,rx,ry,extras):
        return ('I(%d)' % self.id, extras)

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
        extras.append("M('%s',%d,%d%s)" % (self.name, x, y, ',%d'%z if z != z else ''))
        return (None, extras)
        
class Tile:
    def __init__(self, x,y, ground=100, level=7):
        self.x = x
        self.y = y
        self.z = level
        self.area = {x: {y: {level: [Item(ground)]}}}
    def add(self, thing):
        self.area[self.x][self.y][self.z].append(thing)
