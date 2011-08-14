import game.scriptsystem as scriptsystem
import game.map

def floorchange(creature, thing, position, **k):
    # Note this is the correct direction
    print "Floor change"
    print thing.floorchange
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
            
def floorup(creature, thing, position, **k):
    if creature.inRange(position, 1, 1, 0):
        creature.teleport([position[0],position[1],position[2]-1])
    
def floordown(creature, thing, position, **k):
    if creature.inRange(position, 1, 1, 0):
        creature.teleport([position[0],position[1],position[2]+1])

# Stairs
stairs = 1385, 429, 411, 4834, 1396
scriptsystem.get("walkOn").reg(stairs, floorchange)

# Ladders up
laddersUp = 1386, 3678, 5543, 8599
scriptsystem.get("use").reg(laddersUp, floorup)

# Ladders down
laddersDown = 369, 370, 408, 409, 427, 428, 430, 924, 3135, 3136, 5545, 5763, 8170, 8276, 8277, 8279, 8280, 8281, 8284, 8285, 8286, 8595, 8596, 9606
scriptsystem.get("use").reg(laddersDown, floordown)

# Trapdoors, holes etc
trapsAndHoles = 462, 9625, 294, 383, 392, 469, 470, 482, 484, 485, 489, 7933, 7938, 8249, 8250, 8251, 8252, 8253, 8254, 8255, 8256, 8323, 8380, 8567, 8585, 8972
scriptsystem.get("walkOn").reg(trapsAndHoles, floordown)