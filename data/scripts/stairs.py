import game.scriptsystem as scriptsystem
import game.map

def floorchange(creature, item, position):
    # Note this is the correct direction
    print "Floor change"
    print item.floorchange
    if item.floorchange == "north":
        creature.move(0, level=-1)
        
    elif item.floorchange == "south":
        creature.move(2, level=-1)
        
    elif item.floorchange == "east":
        creature.move(1, level=-1)
        
    elif item.floorchange == "west":
        creature.move(3, level=-1)
        
    elif item.floorchange == "down":  
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
            
def floorup(creature, item, position, index=None): # By using index=None, this function will work on both walkOn and useItem
    if creature.inRange(position, 1, 1, 0):
        creature.teleport([position[0],position[1],position[2]-1])
    
def floordown(creature, item, position, index=None):
    if creature.inRange(position, 1, 1, 0):
        creature.teleport([position[0],position[1],position[2]+1])

# Stairs
scriptsystem.get("walkOn").reg(1385, floorchange)
scriptsystem.get("walkOn").reg(429, floorchange)
scriptsystem.get("walkOn").reg(427, floorchange)
scriptsystem.get("walkOn").reg(4834, floorchange)
scriptsystem.get("walkOn").reg(4837, floorchange)
scriptsystem.get("walkOn").reg(8282, floorchange)
scriptsystem.get("walkOn").reg(411, floorchange)

# Ladders
scriptsystem.get("use").reg(1386, floorup)
scriptsystem.get("use").reg(3678, floorup)
scriptsystem.get("use").reg(8599, floorup)
scriptsystem.get("use").reg(10035, floorup)


# Trapdoors etc
scriptsystem.get("walkOn").reg(408, floordown)
scriptsystem.get("walkOn").reg(427, floordown)
scriptsystem.get("walkOn").reg(8284, floordown)
scriptsystem.get("walkOn").reg(8279, floordown)