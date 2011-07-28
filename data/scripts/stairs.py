import game.scriptsystem as scriptsystem
import game.map

def floorchange(creature, item, position):
    print position
    if item.floorchange == "north":
        creature.move(0, level=-1)
        
    elif item.floorchange == "down":  
        """# This is a reverse behavior, get the tile under it, then all four sides, if it's a floor change tile, then tele to it
        destTile = game.map.getTile([position[0]+1, position[1], position[2]+1])
        print destTile.getThing(0).cid
        if destTile.getThing(0).floorchange:
            creature.teleport([position[0], position[1], position[2]+1])

        # North then
        destTile = game.map.getTile([position[0]+1, position[1]-1, position[2]+1])
        print destTile.getThing(0).cid
        if destTile.getThing(0).floorchange:
            creature.teleport([position[0]-1, position[1]-1, position[2]+1])   
            
        # South then
        destTile = game.map.getTile([position[0]+1, position[1]+1, position[2]+1])
        print destTile.getThing(0).cid
        if destTile.getThing(0).floorchange:
            creature.teleport([position[0]+1, position[1]+1, position[2]+1]) """   
            
scriptsystem.get("walkOn").reg(1385, floorchange)
scriptsystem.get("walkOn").reg(429, floorchange)