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

    def __hash__(self):
        """ Python3 requirement, override hash. """
        # Just make it non hashable.
        return None
        
    def copy(self):
        """ Return a copy of this position. """
        return Position(self.x, self.y, self.z, self.instanceId)
    
    def inRange(self, other, x, y, z=0):
        """ Is this position in x,y,z range from the other position? Returns True/False. """
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
        """ Returns the Tile of this position, similar to :func:`game.map.getTile` with this as the position. """
        return getTile(self)

    def setTile(self, tile):
        """ Sets the tile of this position, similar to :func:`game.map.setTile` with this as the position. """
        return setTile(self, tile)
        
    def distanceTo(self, position):
        "Return the absolute x,y distance to this other position."
        return abs(self.x-position.x)+abs(self.y-position.y)
    
    def roundPoint(self, steps):
        """ Return a MultiPosition with all the steps away from this tile. """
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

    def setStackpos(self, stack):
        """ Return a StackPosition with `stack` as the stack position and this as the x,y,z,instance position. """
        return StackPosition(self.x, self.y, self.z, stack, self.instanceId)

    def exists(self):
        """ Check if this position exists (holds a tile) """
        tile = knownMap.get((self.x, self.y, self.z, self.instanceId), False)

        if tile:
            return True
        else:
            return False

class MultiPosition(Position):
    def __init__(self, instanceId=0, *argc):
        self.positions = argc
        self.index = 0
        self.instanceId = instanceId
    
    @property
    def x(self):
        """ Return the current x point """
        return self.positions[self.index][0]
        
    @property
    def y(self):
        """ Return the current y point """
        return self.positions[self.index][1]
        
    @property
    def z(self):
        """ Return the current z point """
        return self.positions[self.index][2]
        
    def __iter__(self):
        return self
        
    def next(self):
        """ Increase the index, change to that position in the position list. """
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
        """ Return the thing on this StackPosition """
        return self.getTile().getThing(self.stackpos)

    def setStackpos(self, stack):
        """ Change the stack position on this x,y,z position. """
        self.stackpos = stack
        return self
