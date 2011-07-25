import copy
# Ops:
"""
    I: Item
    M: Monster
"""

class Map:
    def __init__(self, xA, yA, ground=100):
        self.area = []
        self.size = (xA, yA)
        
        for x in xrange(0, xA+1):
            self.area.append([])
            for y in xrange(0, yA+1):
                self.area[x].append({7: [Item(ground)]})

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
                        for zS in self.area[xS][yS]:
                            sector[xS][yS] = {7:[]}
                            for thing in self.area[xS][yS][zS]:
                                e,extras = thing.gen(xS, yS, zS, extras)
                                if e:
                                    sector[xS][yS][zS].append(e)
                
                # Begin by rebuilding ranges of tiles in x,y,z
                xCom = []
                xCount = 0
                global opR
                opR = "="
                def opM():
                    global opR
                    if opR == "=":
                        opR = "+="
                        return "="
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
                                output += str([yCom]).replace(': ', ':').replace(', ', ',').replace("'I", 'I').replace(")'", ')')+"*%d," % yCount
                            elif yCount:
                                output += str(yCom).replace(': ', ':').replace(', ', ',').replace("'I", 'I').replace(")'", ')')+","
                            yCom = y
                            yCount = 1
                    if yCount > 1:
                        output += str([yCom]).replace(': ', ':').replace(', ', ',').replace("'I", 'I').replace(")'", ')')+"*%d," % yCount
                    
                    return output[:-1]
                output = ""
                # Level 1, X compare
                for x in copy.copy(sector):
                    if xCom == x:
                        xCount += 1
                        sector.remove(x)
                    else:
                        if xCount > 1:
                            # Begin building
                            output += "M%s["%opM()+yComp(xCom)+"]*%d\n" % xCount
                        elif xCount:
                            output += "M%s["%opM()+yComp(xCom)+"]\n"
                        xCom = x
                        xCount = 1
                if xCount > 1:
                    output += "M%s["%opM()+yComp(xCom)+"]*%d\n" % xCount

                output += '\n'.join(extras)
                open('map_%d_%d.sec' % (xA, yA), 'wb').write(output[:-1])
        
class Area:
    def __init__(self, xA, yA, ground=100, level=7):
        self.z = level
        self.area = []
        for x in xrange(0, xA+1):
            self.area.append([])
            for y in xrange(0, yA+1):
                self.area[x].append({level: [Item(ground)]})
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
