from core.game.item import BaseItem

def getTile(pos):
    try:
        return knownMap[ pos[0] ][ pos[1] ][ pos[2] ]
    except:
        return None

def placeCreature(creature, pos):
    try:
        return getTile(pos).placeCreature(creature)
    except:
        return False

class Tile(BaseItem):
    def __init__(self, id):
        self.itemId = id
        self.items = []
        self.creatures = []

    def placeCreature(self, creature):
        return self.creatures.append(creature)
    
    def removeCreature(self,player):
        return self.creatures.remove(creature)

    
knownMap = {}
mapSizeX = 250
mapSizeY = 250
r = 0
for x in range (0, mapSizeX):
    knownMap[x] = {}
    for y in range(0, mapSizeY):
        knownMap[x][y] = {}
        knownMap[x][y][7] = Tile(106 + r)
        
        if r:
	    r = 0
	else:
	    r = 1
