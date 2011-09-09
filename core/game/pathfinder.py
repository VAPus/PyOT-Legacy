## {{{ http://code.activestate.com/recipes/577519/ (r3)
# A* Shortest Path Algorithm
# FB - 201012256

# Heavily modified by Stian Andreassen to gain speed and functionality (original script was totally broken for our usage and used 5 times longer to calculate) :)
from heapq import heappush, heappop # for priority queue
import game.map

class node(object):
    __slots__ = ('xPos', 'yPos', 'distance', 'priority')
    def __init__(self, xPos, yPos, distance, priority):
        self.xPos = xPos
        self.yPos = yPos
        self.distance = distance
        self.priority = priority
    def __lt__(self, other): # comparison method for priority queue
        return self.priority < other.priority
    def updatePriority(self, xDest, yDest):
        self.priority = self.distance + self.estimate(xDest, yDest) * 10 # A*
    # give higher priority to going straight instead of diagonally
    def nextMove(self, d): # d: direction to move
        if d % 2:
            self.distance += 2
        else:
            self.distance += 1

    # Estimation function for the remaining distance to the goal.
    def estimate(self, xDest, yDest):
        # Euclidian Distance
        """xd = xDest - self.xPos
        yd = yDest - self.yPos
        return math.sqrt(xd * xd + yd * yd)"""
        return abs(xDest - self.xPos) + abs(yDest - self.yPos)

# A-star algorithm.
# The path returned will be a string of digits of directions.
def findPath(mapZ, relX, relY, xB, yB):
    _goalX = xB
    _goalY = yB
    _fromX = relX
    _fromY = relY
    
    """dx = [1, 1, 0, -1, -1, -1, 0, 1]
    dy = [0, 1, 1, 1, 0, -1, -1, -1]"""
    dx = [0, 1, 0, -1]
    dy = [-1, 0, 1, 0]
    xA = 15
    yA = 15
    xB = xB - relX + 15
    yB = yB - relY + 15
    
    """dy = [0, 1, 0, -1, -1, 1, -1, 1]
    dx = [1, 0, -1, 0, 1, 1, -1, -1]"""
    closed_nodes_map = [] # map of closed (tried-out) nodes
    open_nodes_map = [] # map of open (not-yet-tried) nodes
    dir_map = [] # map of dirs
    row = [0] * 30
    for i in xrange(30): # create 2d arrays
        closed_nodes_map.append(row[:])
        open_nodes_map.append(row[:])
        dir_map.append(row[:])

    pq = [[], []] # priority queues of open (not-yet-tried) nodes
    pqi = 0 # priority queue index
    # create the start node and push into list of open nodes
    n0 = node(xA, yA, 0, 0)
    n0.updatePriority(xB, yB)
    heappush(pq[pqi], n0)
    open_nodes_map[yA][xA] = n0.priority # mark it on the open nodes map

    # A* search
    while pq[pqi]:
        # get the current node w/ the highest priority
        # from the list of open nodes
        n1 = pq[pqi][0] # top node
        n0 = node(n1.xPos, n1.yPos, n1.distance, n1.priority)
        x = n0.xPos
        y = n0.yPos
        heappop(pq[pqi]) # remove the node from the open list
        open_nodes_map[y][x] = 0
        closed_nodes_map[y][x] = True # mark it on the closed nodes map

        # quit searching when the goal is reached
        # if n0.estimate(xB, yB) == 0:
        if x == xB and y == yB:
            # generate the path from finish to start
            # by following the dirs

            path = []
            while not (x == xA and y == yA):
                j = dir_map[y][x]
                c = (j + 4 / 2) % 4
                path.append(c)
                x += dx[j]
                y += dy[j]
            path.reverse()
            return path

        # generate moves (child nodes) in all possible dirs
        for i in xrange(4):
            xdx = x + dx[i]
            ydy = y + dy[i]
            mx = x+relX-15
            my = y+relY-15
            isSolid = False
            tile = game.map.getTile((mx, my, mapZ))

            try:
                if not (xdx < 0 or xdx > 29 or ydy < 0 or ydy > 29 or not tile or closed_nodes_map[ydy][xdx]):
                    if not (mx == _fromX and my == _fromY) and not (mx == _goalX and my == _goalY):
                        for t in tile.things:
                            if t.solid:
                                print t
                                isSolid = True
                                break
                        if isSolid:
                            continue
                    #print "%d %d" % (mx, my)
                    # generate a child node
                    m0 = node(xdx, ydy, n0.distance, n0.priority)
                    m0.nextMove(i)
                    m0.updatePriority(xB, yB)
                    # if it is not in the open list then add into that
                    if open_nodes_map[ydy][xdx] == 0:
                        open_nodes_map[ydy][xdx] = m0.priority
                        heappush(pq[pqi], m0)
                        # mark its parent node direction
                        dir_map[ydy][xdx] = (i + 4 / 2) % 4
                    elif open_nodes_map[ydy][xdx] > m0.priority:
                        # update the priority
                        open_nodes_map[ydy][xdx] = m0.priority
                        # update the parent direction
                        dir_map[ydy][xdx] = (i + 4 / 2) % 4
                        # replace the node
                        # by emptying one pq to the other one
                        # except the node to be replaced will be ignored
                        # and the new node will be pushed in instead
                        while not (pq[pqi][0].xPos == xdx and pq[pqi][0].yPos == ydy):
                            heappush(pq[1 - pqi], pq[pqi][0])
                            heappop(pq[pqi])
                        heappop(pq[pqi]) # remove the target node
                        # empty the larger size priority queue to the smaller one
                        if len(pq[pqi]) > len(pq[1 - pqi]):
                            pqi = 1 - pqi
                        while pq[pqi]:
                            heappush(pq[1-pqi], pq[pqi][0])
                            heappop(pq[pqi])      
                        pqi = 1 - pqi
                        heappush(pq[pqi], m0) # add the better node instead
            except:
                pass # Out of map position
    return [] # if no route found 