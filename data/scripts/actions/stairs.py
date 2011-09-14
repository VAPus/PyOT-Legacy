import game.scriptsystem as scriptsystem
import game.map
import config

# Stairfronts
"""stairnorth = None,
stairsouth = None
stairwest = 1390,
staireast = 1389,

def walker(direction):
    def callback(creature, **k):
        creature.move(direction)
    return callback
    
scriptsystem.get("walkOn").reg(stairwest, walker(3))
scriptsystem.get("walkOn").reg(staireast, walker(1))"""

def floorchange(creature, thing, position, **k):
    # Check if we can do this
    if not config.monsterStairHops and not creature.isPlayer():
        return
        
    # Note this is the correct direction
    if thing.floorchange == "north":
        creature.move(0, level=-1)
        
    elif thing.floorchange == "south":
        creature.move(2, level=-1)
        
    elif thing.floorchange == "east":
        creature.move(1, level=-1)
        
    elif thing.floorchange == "west":
        creature.move(3, level=-1)
        
    elif thing.floorchange == "down":  
        # This is a reverse direction, get the tile under it, then all four sides checked depending on it
        destTile = game.map.getTile([position[0], position[1], position[2]+1])
        destThing = destTile.getThing(1)

        # Note: It's the reverse direction
        if destThing.floorchange == "north":
            creature.move(2, level=1)
            
        elif destThing.floorchange == "south":
            creature.move(0, level=1)
            
        elif destThing.floorchange == "west":
            creature.move(1, level=1)
            
        elif destThing.floorchange == "east":
            creature.move(3, level=1)

def itemFloorChange(thing, position, onPosition, onThing, **k):
    newPos = position[:]
    if thing.floorchange == "north":
        newPos[1] -= 1
        newPos[2] -= 1
        
    elif thing.floorchange == "south":
        newPos[1] += 1
        newPos[2] -= 1
        
    elif thing.floorchange == "east":
        newPos[0] += 1
        newPos[2] -= 1
        
    elif thing.floorchange == "west":
        newPos[0] -= 1
        newPos[2] -= 1
        
    elif thing.floorchange == "down":  
        # This is a reverse direction, get the tile under it, then all four sides checked depending on it
        destTile = game.map.getTile([position[0], position[1], position[2]+1])
        destThing = destTile.getThing(1)
        newPos[2] += 1
        # Note: It's the reverse direction
        if destThing.floorchange == "north":
            newPos[1] += 1
            
        elif destThing.floorchange == "south":
            newPos[1] -= 1
            
        elif destThing.floorchange == "west":
            newPos[0] += 1
            
        elif destThing.floorchange == "east":
            newPos[1] -= 1
            
    game.engine.teleportItem(onThing, onPosition, newPos)
    
    return False
    
def floorup(creature, thing, position, **k):
    if creature.inRange(position, 1, 1, 0):
        creature.teleport([position[0],position[1],position[2]-1])
    
def floordown(creature, thing, position, **k):
    if creature.inRange(position, 1, 1, 0):
        creature.teleport([position[0],position[1],position[2]+1])

def teleportDirection(creature, thing, position, **k):
    # Check if we can do this
    if not config.monsterStairHops and not creature.isPlayer():
        return
        
    # Grab the position of the player/creature    
    pos = creature.position[:]
    pos[2] -= 1
    
    # Change the position to match the floorchange.
    if thing.floorchange == "north":
        pos[1] -= 1
    elif thing.floorchange == "south":
        pos[1] += 1
        
    elif thing.floorchange == "east":
        pos[0] += 1
        
    elif thing.floorchange == "west":
        pos[0] -= 1
        
    creature.teleport(pos)
    
# Stairs
stairs = 410, 429, 411, 432, 4834, 1385, 1396, 4837, 3687, 3219, 3138
scriptsystem.get("walkOn").reg(stairs, floorchange)
scriptsystem.reg('useWith', stairs, itemFloorChange)

# Ramps
ramps = 1390, 1388, 1394, 1392, 1398, 459
scriptsystem.get("walkOn").reg(ramps, teleportDirection)

# Ladders up
laddersUp = 1386, 3678, 5543, 8599
scriptsystem.get("use").reg(laddersUp, floorup)

# Ladders down
laddersDown = 369, 370, 408, 409, 427, 428, 430, 433, 924, 3135, 3136, 5545, 5763, 8170, 8276, 8277, 8279, 8280, 8281, 8284, 8285, 8286, 8595, 8596, 9606
scriptsystem.get("use").reg(laddersDown, floordown)

# Trapdoors, holes etc
trapsAndHoles = 462, 9625, 294, 383, 392, 469, 470, 482, 484, 485, 489, 7933, 7938, 8249, 8250, 8251, 8252, 8253, 8254, 8255, 8256, 8323, 8380, 8567, 8585, 8972
scriptsystem.get("walkOn").reg(trapsAndHoles, floordown)