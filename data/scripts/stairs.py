import game.scriptsystem as scriptsystem
import game.map

def floorchange(creature, item, position):
    print position
    if item.floorchange == "north":
        creature.move(0, level=-1)

    elif item.floorchange == "down":  
        # This is a reverse behavior, get the tile under it, then all four sides, if it's a floor change tile, then tele to it
        destTile = game.map.getTile([position[0], position[1], position[2]+1])
        destThing = destTile.getThing(1)

        if destThing.floorchange == "north":
            creature.move(2, level=1)
        elif destThing.floorchange == "south":
            creature.move(0, level=1)
            
def floorup(creature, item, position):
    creature.teleport([position[0],position[1],position[2]-1])
    
def floordown(creature, item, position):
    creature.teleport([position[0],position[1],position[2]+1])
    
scriptsystem.get("walkOn").reg(1385, floorchange)
scriptsystem.get("walkOn").reg(429, floorchange)
scriptsystem.get("walkOn").reg(427, floorchange)
scriptsystem.get("walkOn").reg(4834, floorchange)
scriptsystem.get("walkOn").reg(4837, floorchange)
scriptsystem.get("walkOn").reg(8282, floorchange)
scriptsystem.get("walkOn").reg(411, floordown)

# Ladders
scriptsystem.get("walkOn").reg(1386, floorup)
scriptsystem.get("walkOn").reg(3678, floorup)
scriptsystem.get("walkOn").reg(8599, floorup)
scriptsystem.get("walkOn").reg(10035, floorup)

scriptsystem.get("walkOn").reg(408, floordown)
scriptsystem.get("walkOn").reg(427, floordown)
scriptsystem.get("walkOn").reg(8284, floordown)
scriptsystem.get("walkOn").reg(8279, floordown)