import copy

# Ops:
"""
    I: Item
    M: Monster
    MM: Multimonster
"""

class Map:
    def __init__(self, xA, yA, ground=100):
        self.area = []
        self.size = (xA, yA)
        
        for x in xrange(0, xA+1):
            self.area.append([])
            for y in xrange(0, yA+1):
                if isinstance(ground, int):
                    self.area[x].append({7: [Item(ground)]})
                else:
                    self.area[x].append({7: [ground]})

    def merge(self, obj, offsetX, offsetY, overrideLevel=None):
        xO = offsetX
        yO = offsetY
        
        for x in obj.area:
            for y in x:
                for z in y:
                    self.area[xO][yO][z if not overrideLevel else overrideLevel] = y[z]

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
                
                sector = []
                extras = []
                for xS in xrange(0, areas[0]):
                    sector.append([])
                    
                    for yS in xrange(0, areas[1]):
                        sector[xS].append([])
                        for zS in self.area[(xA*areas[0])+xS][(yA*areas[1])+yS]:
                            sector[xS][yS] = {7:[]}
                            for thing in self.area[(xA*areas[0])+xS][(yA*areas[1])+yS][zS]:
                                e,extras = thing.gen((xA*areas[0])+xS, (yA*areas[1])+yS, zS, extras)
                                if e:
                                    sector[xS][yS][zS].append(e)
                
                # Begin by rebuilding ranges of tiles in x,y,z
                xCom = []
                xCount = 0
                global opR
                opR = "m="
                def opM():
                    global opR
                    if opR == "m=":
                        opR = "+"
                        return "m="
                    return opR
                       
                # Level 2, y compare:
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
                output = ""
                # Level 1, X compare
                for x in copy.copy(sector):
                    if xCom == x:
                        xCount += 1
                        sector.remove(x)
                    else:
                        if xCount > 1:
                            # Begin building
                            output += "%s"%opM()+yComp(xCom)+"*%d" % xCount
                        elif xCount:
                            output += "%s"%opM()+yComp(xCom)+""
                        xCom = x
                        xCount = 1
                if xCount > 1:
                    output += "%s"%opM()+yComp(xCom)+"*%d" % xCount
                elif xCount:
                    output += "%s"%opM()+yComp(xCom)+""
                    
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
                                    
                    output += "\n"+'\n'.join(extras)

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

class Item:
    def __init__(self, id):
        self.id = id
    def gen(self, x,y,z,extras):
        return ('I(%d)' % self.id, extras)

class RSItem:
    def __init__(self, *argc):
        self.ids = argc
    def gen(self, x,y,z,extras):
        import random
        return ('I(%d)' % random.choice(self.ids), extras)    
class Monster:
    def __init__(self, name):
        self.name = name

            
    def gen(self, x,y,z, extras):
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
