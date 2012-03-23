import game.map

# A cache, this can probably get pretty big, but right now it's not something I'll think about
AStarRouteCache = {} # {(FromX, FromY, ToZ, ToY, Z): [Route]}
    
def clear():
    AStarRouteCache = {}
    
class Node(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cost = 0
        self.distance = 0
        self.parent = None
        self.state = True
        self.tileTried = False
        
    def vertify(self, z, instanceId, checkCreature, allowCreatures=False):
        if self.tileTried:
            return self.state
        else:
            self.tileTried = True
            tile = game.map.getTileConst(self.x, self.y, z, instanceId)
            if tile:
                if checkCreature and not checkCreature.vertifyMove(tile):
                    self.state = False
                else:
                    for thing in tile.things:
                        if allowCreatures and isinstance(thing, game.creature.Creature):
                            break
                        elif thing.solid:
                            self.state = False
                            break
            else:
                self.state = False
                
            return self.state
            
    
class AStar(object):
    def __init__(self, checkCreature, zStart, xStart, yStart, xGoal, yGoal, instanceId):
        self.nodes = {}
        self.openNodes = set()
        self.closedNodes = set() 
        self.final = self.getNode(xGoal, yGoal)
        self.checkCreature = checkCreature
        self.found = True
        self.z = zStart
        self.instanceId = instanceId
        
        self.startNode = self.getNode(xStart, yStart)
        currentNode = self.startNode
        
        if not self.final.vertify(zStart, instanceId, checkCreature, True):
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
                break
            else:
                currentNode = t
                
        # Make a result
        n = currentNode
        prev = self.startNode
        _result = []
        if config.findDiagonalPaths:
            if n.y > prev.y and n.x > prev.x:
                _result.append(SOUTHEAST)
            elif n.y < prev.y and n.x > prev.x:
                _result.append(NORTHEAST)
            elif n.y > prev.y and n.x < prev.x:
                _result.append(SOUTHWEST)
            elif n.y < prev.y and n.x < prev.x:
                _result.append(NORTHWEST)
            elif n.y > prev.y:
                _result.append(SOUTH)
            elif n.y < prev.y:
                _result.append(NORTH)
            elif n.x > prev.x:
                _result.append(EAST)
            else:
                _result.append(WEST)
                
        else:
            if n.y > prev.y:
                _result.append(SOUTH)
            elif n.y < prev.y:
                _result.append(NORTH)
            elif n.x > prev.x:
                _result.append(EAST)
            else:
                _result.append(WEST)

        prev = n
        n = n.parent
        if not n:
            self.result = []
            return
            
        while n.parent != None:
            if config.findDiagonalPaths:
                if n.y > prev.y and n.x > prev.x:
                    _result.append(SOUTHEAST)
                elif n.y < prev.y and n.x > prev.x:
                    _result.append(NORTHEAST)
                elif n.y > prev.y and n.x < prev.x:
                    _result.append(SOUTHWEST)
                elif n.y < prev.y and n.x < prev.x:
                    _result.append(NORTHWEST)
                elif n.y > prev.y:
                    _result.append(NORTH)
                elif n.y < prev.y:
                    _result.append(SOUTH)
                elif n.x > prev.x:
                    _result.append(WEST)
                else:
                    _result.append(EAST)
            else:
                if n.y > prev.y:
                    _result.append(NORTH)
                elif n.y < prev.y:
                    _result.append(SOUTH)
                elif n.x > prev.x:
                    _result.append(WEST)
                else:
                    _result.append(EAST)

            prev = n
            n = n.parent
            if not n:
                break
        self.result = _result
    
    def getNode(self, x, y):
        try:
            return self.nodes[x,y]
        except KeyError:
            node = Node(x,y)
            self.nodes[x,y] = node
            return node
            
    def getCheapest(self):
        min = 100000
        min_n = None
        if self.final in self.openNodes:
            return self.final
            
        for n in self.openNodes:
            if n.distance < min:
                min_n = n
                min = n.distance
        return min_n
        
    def aroundNode(self, node):
        # Make node locals to speed things up
        x = node.x
        y = node.y
        cost = node.cost
        
        # Make locals to speed things up
        #_nodes = self.nodes
        _closedNodes = self.closedNodes
        _openNodes = self.openNodes
        _final = self.final
        _getNode = self.getNode

        # Inlined test for all the steps we might take.
        
        n = _getNode(x, y - 1)
        if n not in _closedNodes and n.vertify(self.z, self.instanceId, self.checkCreature) and (n not in _openNodes or n.cost < cost):
            n.parent = node
            n.cost = cost + 10
            n.distance = abs(n.x - _final.x) + abs(n.y - _final.y)
            _openNodes.add(n)   

        n = _getNode(x - 1, y)
        if n not in _closedNodes and n.vertify(self.z, self.instanceId, self.checkCreature) and (n not in _openNodes or n.cost < cost):
            n.parent = node
            n.cost = cost + 10
            n.distance = abs(n.x - _final.x) + abs(n.y - _final.y)
            _openNodes.add(n)   

        n = _getNode(x + 1, y)
        if n not in _closedNodes and n.vertify(self.z, self.instanceId, self.checkCreature) and (n not in _openNodes or n.cost < cost):
            n.parent = node
            n.cost = cost + 10
            n.distance = abs(n.x - _final.x) + abs(n.y - _final.y)
            _openNodes.add(n)  
            
        n = _getNode(x, y + 1)
        if n not in _closedNodes and n.vertify(self.z, self.instanceId, self.checkCreature) and (n not in _openNodes or n.cost < cost):
            n.parent = node
            n.cost = cost + 10
            n.distance = abs(n.x - _final.x) + abs(n.y - _final.y)
            _openNodes.add(n)
            
        if config.findDiagonalPaths:
            n = _getNode(x - 1, y - 1)
            if n not in _closedNodes and n.vertify(self.z, self.instanceId, self.checkCreature) and (n not in _openNodes or n.cost < cost):
                n.parent = node
                n.cost = cost + (10 * config.diagonalWalkCost)
                n.distance = abs(n.x - _final.x) + abs(n.y - _final.y)
                _openNodes.add(n)   

            n = _getNode(x - 1, y + 1)
            if n not in _closedNodes and n.vertify(self.z, self.instanceId, self.checkCreature) and (n not in _openNodes or n.cost < cost):
                n.parent = node
                n.cost = cost + (10 * config.diagonalWalkCost)
                n.distance = abs(n.x - _final.x) + abs(n.y - _final.y)
                _openNodes.add(n)   

            n = _getNode(x + 1, y - 1)
            if n not in _closedNodes and n.vertify(self.z, self.instanceId, self.checkCreature) and (n not in _openNodes or n.cost < cost):
                n.parent = node
                n.cost = cost + (10 * config.diagonalWalkCost)
                n.distance = abs(n.x - _final.x) + abs(n.y - _final.y)
                _openNodes.add(n)  
                
            n = _getNode(x + 1, y + 1)
            if n not in _closedNodes and n.vertify(self.z, self.instanceId, self.checkCreature) and (n not in _openNodes or n.cost < cost):
                n.parent = node
                n.cost = cost + (10 * config.diagonalWalkCost)
                n.distance = abs(n.x - _final.x) + abs(n.y - _final.y)
                _openNodes.add(n)            
            
def findPath(checkCreature, zStart, xStart, yStart, xGoal, yGoal, instanceId=None):
    return AStar(checkCreature, zStart, xStart, yStart, xGoal, yGoal, instanceId).result
    