import game.map
import config

# A cache, this can probably get pretty big, but right now it's not something I'll think about
RouteCache = {} # {(FromX, FromY, ToZ, ToY, Z): [Route]}
    
def clear():
    RouteCache = {}
    
# FIXME: Not make this a global...

CACHE_CURRENT = config.pathfinderCache

class Node(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cost = 0
        #self.distance = 0
        self.parent = None
        self.state = True
        self.tileTried = False
                
    def verify(self, z, instanceId, checkCreature):
        global CACHE_CURRENT # XXX: Fixme!
        if self.tileTried:
            return self.state
        else:
            self.tileTried = True
            tile = game.map.getTileConst(self.x, self.y, z, instanceId)
            if tile:
                for thing in tile.getItems():
                    if thing.solid:
                        self.state = False
                        break
                if self.state and checkCreature:
                    self.state = checkCreature.verifyMove(tile)
            else:
                self.state = False
                
            return self.state
            
    
class AStar(object):
    def __init__(self, checkCreature, zStart, xStart, yStart, xGoal, yGoal, instanceId):
        global CACHE_CURRENT # XXX: fixme
        CACHE_CURRENT = config.pathfinderCache
        self.nodes = {}
        self.openNodes = set()
        self.closedNodes = set() 
        self.final = self.getNode(xGoal, yGoal)
        self.checkCreature = checkCreature
        self.found = True
        self.z = zStart
        self.instanceId = instanceId
        self.cache = True
        
        self.startNode = self.getNode(xStart, yStart)
        currentNode = self.startNode
        
        if not self.final.verify(zStart, instanceId, None):
            self.result = []
            return
        
        # Speedups
        _closedNodes = self.closedNodes
        _openNodes = self.openNodes
        _getCheapest = self.getCheapest
        _aroundNode = self.aroundNode
        _final = self.final
        
        # Add the first node to the openNodes
        _openNodes.add(currentNode)
        
        # Perform A*
        while currentNode != _final:
            # Add the current node to the closed set and remove it from the open one
            _closedNodes.add(currentNode)
            _openNodes.remove(currentNode)

            # Get the nodes around the current one
            _aroundNode(currentNode)

            # Get the "cheapest" (shortest) route
            t = _getCheapest()
            
            # If no route can be found, we didn't find a path
            if t is None:
                self.found = False
                return
            else:
                currentNode = t
                
        # Make a result
        n = currentNode
        prev = self.startNode
        
        # Not possible.
        if not n.verify():
            self.found = None
            return

        _result = [n.step]
        
        prev = n
        n = n.parent
        if not n:
            self.result = _result
            return
            
        while n.parent != None:
            _result.append(n.step)

            prev = n
            n = n.parent
            if not n:
                break
        _result.reverse()
        
        self.result = _result
    
    def getNode(self, x, y):
        point = x + (y << 16)
        try:
            return self.nodes[point]
        except KeyError:
            node = Node(x,y)
            self.nodes[point] = node
            return node
            
    def getCheapest(self):
        min = 100000
        min_n = None
        if self.final in self.openNodes:
            return self.final
            
        for n in self.openNodes:
            if n.cost < min:
                min_n = n
                min = n.cost
        return min_n
        
    def aroundNode(self, node):
        # Make node locals to speed things up
        x = node.x
        y = node.y
        cost = node.cost
        
        diagonalSouth = False
        diagonalNorth = False
        diagonalWest = False
        diagonalEast = False

        # Make locals to speed things up
        #_nodes = self.nodes
        _closedNodes = self.closedNodes
        _openNodes = self.openNodes
        _final = self.final
        _getNode = self.getNode

        # Inlined test for all the steps we might take.
        
        n = _getNode(x, y - 1)
        if n not in _closedNodes and n.verify(self.z, self.instanceId, self.checkCreature) and (n not in _openNodes): # or (n.cost + 10) < cost):
            n.parent = node
            n.cost = cost + 10
            #n.distance = abs(n.x - _final.x) + abs(n.y - _final.y)
            n.step = NORTH
            _openNodes.add(n)   

        if not n.state:
            diagonalNorth = True

        n = _getNode(x - 1, y)
        if n not in _closedNodes and n.verify(self.z, self.instanceId, self.checkCreature) and (n not in _openNodes): # or (n.cost + 10) < cost):
            n.parent = node
            n.cost = cost + 10
            #n.distance = abs(n.x - _final.x) + abs(n.y - _final.y)
            n.step = WEST
            _openNodes.add(n)   

        if not n.state:
            diagonalWest = True

        n = _getNode(x + 1, y)
        if n not in _closedNodes and n.verify(self.z, self.instanceId, self.checkCreature) and (n not in _openNodes): # or (n.cost + 10) < cost):
            n.parent = node
            n.cost = cost + 10
            #n.distance = abs(n.x - _final.x) + abs(n.y - _final.y)
            n.step = EAST
            _openNodes.add(n)  
            
        if not n.state:
            diagonalEast = True

        n = _getNode(x, y + 1)
        if n not in _closedNodes and n.verify(self.z, self.instanceId, self.checkCreature) and (n not in _openNodes): # or (n.cost + 10) < cost):
            n.parent = node
            n.cost = cost + 10
            #n.distance = abs(n.x - _final.x) + abs(n.y - _final.y)
            n.step = SOUTH
            _openNodes.add(n)
            
        if not n.state:
            diagonalWest = True

        if config.findDiagonalPaths:
            if diagonalNorth and diagonalWest:
                n = _getNode(x - 1, y - 1)
                if n not in _closedNodes and n.verify(self.z, self.instanceId, self.checkCreature) and (n not in _openNodes): # or (n.cost + (15 * config.diagonalWalkCost)) < cost):
                    n.parent = node
                    n.cost = cost + (10 * config.diagonalWalkCost)
                    #n.distance = abs(n.x - _final.x) + abs(n.y - _final.y)
                    n.step = NORTHWEST
                    _openNodes.add(n)

            if diagonalSouth and diagonalWest:
                n = _getNode(x - 1, y + 1)
                if n not in _closedNodes and n.verify(self.z, self.instanceId, self.checkCreature) and (n not in _openNodes): # or (n.cost + (15 * config.diagonalWalkCost)) < cost):
                    n.parent = node
                    n.cost = cost + (10 * config.diagonalWalkCost)
                    #n.distance = abs(n.x - _final.x) + abs(n.y - _final.y)
                    n.step = SOUTHWEST
                    _openNodes.add(n)   
            if diagonalNorth and diagonalEast:
                n = _getNode(x + 1, y - 1)
                if n not in _closedNodes and n.verify(self.z, self.instanceId, self.checkCreature) and (n not in _openNodes): # or (n.cost + (15 * config.diagonalWalkCost)) < cost):
                    n.parent = node
                    n.cost = cost + (10 * config.diagonalWalkCost)
                    #n.distance = abs(n.x - _final.x) + abs(n.y - _final.y)
                    n.step = NORTHEAST
                    _openNodes.add(n)  
            if diagonalSouth and diagonalEast:    
                n = _getNode(x + 1, y + 1)
                if n not in _closedNodes and n.verify(self.z, self.instanceId, self.checkCreature) and (n not in _openNodes): # or (n.cost + (15 * config.diagonalWalkCost)) < cost):
                    n.parent = node
                    n.cost = cost + (10 * config.diagonalWalkCost)
                    #n.distance = abs(n.x - _final.x) + abs(n.y - _final.y)
                    n.step = SOUTHEAST
                    _openNodes.add(n)            
            
def findPath(checkCreature, zStart, xStart, yStart, xGoal, yGoal, instanceId):
    cachePoint = (xStart, yStart, xGoal, yGoal, zStart, instanceId)
    if config.pathfinderCache:
        try:
            return RouteCache[cachePoint]
        except:
            pass
    
    """if abs(xStart-xGoal) < 2 and abs(yStart-yGoal) < 2:
       pattern = []
       if xStart > xGoal:
           pattern.append(WEST)
       elif xStart < xGoal:
           pattern.append(EAST)
       if yStart > yGoal:
           pattern.append(NORTH)
       elif yStart < yGoal:
           pattern.append(SOUTH)
       
       if config.pathfinderCache:
           RouteCache[cachePoint] = pattern
       return pattern"""

    aStar = AStar(checkCreature, zStart, xStart, yStart, xGoal, yGoal, instanceId)
    
    if aStar.found:
        if CACHE_CURRENT:
            RouteCache[cachePoint] = aStar.result
        return aStar.result
    else:
        if CACHE_CURRENT:
            RouteCache[cachePoint] = None
        return None
    
