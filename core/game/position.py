class Position(object):
    __slots__ = ('x', 'y', 'z', 'instanceId')
    def __init__(self, x, y, z=7, instanceId=0):
        self.x = x
        self.y = y
        self.z = z
        self.instanceId = instanceId
        
    def __eq__(self, other):
        return (self.x == other.x and self.y == other.y and self.z == other.z and self.instanceId == other.instanceId)
        
    def __ne__(self, other):
        return (self.x != other.x or self.y != other.y or self.z != other.z or self.instanceId != other.instanceId)
        
    def copy(self):
        return Position(self.x, self.y, self.z, self.instanceId)
    
    def inRange(self, other, x, y, z=0):
        return ( self.instanceId == other.instanceId and abs(self.x-other.x) <= x and abs(self.y-other.y) <= y and abs(self.z-other.z) <= y ) 

    # Support for the old behavior of list attributes.
    def __setitem__(self, key, value):
        # TODO: Kill!
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        else:
            raise IndexError("Position doesn't support being treated like a list with the key == %s" % key)
        
    def __getitem__(self, key):
        # TODO: Kill!
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
            
        raise IndexError("Position have no key == %s" % key)

    # Simplifiers
    def getTile(self):
        return getTile(self)

    def setTile(self, tile):
        return setTile(self, tile)
        
    def distanceTo(self, position):
        return abs(self.x-position.x)+abs(self.y-position.y)
    
    def roundPoint(self, steps):
        positions = []
        for x in xrange(-steps, steps+1):
            for y in xrange(-steps, steps+1):
                positions.append((x+self.x,y+self.y,self.z))
                
        return MultiPosition(self.instanceId, *positions)
        
    # For savings
    def __getstate__(self):
            return (self.x, self.y, self.z, self.instanceId)
            
    def __setstate__(self, data):
        self.x, self.y, self.z, self.instanceId = data
        if self.instanceId is None:
            self.instanceId = 0
    def __str__(self):
        if not self.instanceId:
            return "[%d, %d, %d]" % (self.x, self.y, self.z)
        else:
            return "[%d, %d, %d - instance %d]" % (self.x, self.y, self.z, self.instanceId)

    def setStackpos(self, x):
        return StackPosition(self.x, self.y, self.z, x, self.instanceId)

class MultiPosition(Position):
    def __init__(self, instanceId=0, *argc):
        self.positions = argc
        self.index = 0
        self.instanceId = instanceId
    
    @property
    def x(self):
        return self.positions[self.index][0]
        
    @property
    def y(self):
        return self.positions[self.index][1]
        
    @property
    def z(self):
        return self.positions[self.index][2]
        
    def __iter__(self):
        return self
        
    def next(self):
        self.index += 1
        if self.index >= len(self.positions):
            raise StopIteration
        return self
        
class StackPosition(Position):
    __slots__ = ('stackpos',)
    
    def __init__(self, x, y, z=7, stackpos=0, instanceId=0):
        self.x = x
        self.y = y
        self.z = z
        self.stackpos = stackpos
        self.instanceId = instanceId

    # For savings
    def __getstate__(self):
        return (self.x, self.y, self.z, self.stackpos, self.instanceId)
            
    def __setstate__(self, data):
        self.x, self.y, self.z, self.stackpos, self.instanceId = data

    def __str__(self):
        if not self.instanceId:
            return "[%d, %d, %d - stack %d]" % (self.x, self.y, self.z, self.stackpos)
        else:
            return "[%d, %d, %d - instance %d, stack - %d]" % (self.x, self.y, self.z, self.instanceId, self.stackpos)

    def getThing(self):
        return self.getTile().getThing(self.stackpos)

    def setStackpos(self, x):
        self.stackpos = x
