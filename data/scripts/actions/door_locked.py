lockedDoors = 1209, 1212, 1231, 1234, 1249, 1252, 3535, 3544, 4913, 4616, 5098, 5107, 5116, 5125, 5134, 5137, 5140, 5143, 5278, 5281, 5732, 5735,\
                6192, 6195, 6249, 6252, 6891, 6900, 7033, 7042, 8541, 8544, 9165, 9168, 9267, 9270, 10268, 10271, 10468, 10477
                
keys = range(2086, 2092+1)

@register('use', lockedDoors)
def onUseDoor(creature, thing, position, **k):
    if not thing.actions:
        # Shouldn't happend
        print "Bad door on %s. It might bug" % str(position)
        transformItem(thing, thing.itemId+2, position)
    else:
        if "houseDoor" in thing.actions:
            houseId = game.map.getTile(position).houseId
            if creature.data["id"] == game.house.houseData[houseId].owner or creature.data["id"] in game.house.houseData[houseId].data["subowners"]:
                transformItem(thing, thing.itemId+2, position)
                return
        creature.lmessage("It is locked.")

@register('useWith', keys)
def onUseKey(creature, thing, onThing, onPosition, **k):
    if not onThing.actions or not onThing.itemId in lockedDoors or not onThing.itemId-1 in lockedDoors or not onThing.itemId-2 in lockedDoors:
        return
    
    canOpen = False
    for aid in thing.actions:
        if aid in onThing.actions:
            canOpen = True
            
    if not canOpen:
        creature.lmessage("The key does not match.")
        return
        
    if onThing.itemId in lockedDoors:
        transformItem(onThing, onThing.itemId+2, onPosition)
    elif onThing.itemId-2 in lockedDoors:
        transformItem(onThing, onThing.itemId-2, onPosition)
    else:
        transformItem(onThing, onThing.itemId-1, onPosition)