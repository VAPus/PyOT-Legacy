def _houseCheck(creature):
    houseId = getHouseId(creature.position)
    if not houseId:
        creature.message("Your not standing in a house")
        return False
    
    house = getHouseById(houseId)
    if not house:
        creature.message("MAPPING/SQL ERROR! House not found")
        return False

    if creature.data["id"] != house.owner:
        creature.message("Your not the owner of this house")
        return False
    
    return house

def guestList(creature, **k):
    house = _houseCheck(creature)
    if house:
        _text = '\n'.join(house.data["guests"])
        windowId = creature.houseWindow(_text)
        def writeback(text):
            if text != _text:
                # Update guestlist
                house.data["guests"] = text.split("\n")

                # Force save
                house.save = True
                
                creature.message("Guestlist have been updated!")
        
        # Register the writeback event
        creature.setWindowHandler(windowId, writeback)

    # Return False to not display text
    return False

def doorAccess(creature, **k):
    house = _houseCheck(creature)
    if house:
        # Get the tile in front of the player
        tile = getTile(creature.positionInDirection(creature.direction))

        # Check if there is a item with a doorId
        for item in tile.getItems():
            doorId = item.doorId
            if doorId:
                break

        # No doorId?
        if not doorId:
            creature.message("Your not standing in front of a door (with a doorId)")
            return False

        _text = '\n'.join(house.getDoorAccess(doorId))
        windowId = creature.houseWindow(_text)
        def writeback(text):
            if text != _text:
                # Update guestlist
                house.data["doors"][doorId] = text.split("\n")
                
                # Force save
                house.save = True
                
                creature.message("door access have been updated!")
        
        # Register the writeback event
        creature.setWindowHandler(windowId, writeback)

    # Return False to not display text
    return False
    
def subownerList(creature, **k):
    house = _houseCheck(creature)
    if house:
        
        _text = '\n'.join(house.data["subowners"])
        windowId = creature.houseWindow(_text)
        def writeback(text):
            # We do this so we can compare and only invalidate the saved state of the house when it's actually updated!
            if text != _text:
                # Update sub-owner list
                house.data["subowners"] = text.split("\n")

                # Force save
                house.save = True
                
                creature.message("sub-owner list have been updated!")
        
        # Register the writeback event
        creature.setWindowHandler(windowId, writeback)

    # Return False to not display text
    return False
    
reg("talkaction", "aleta sio", guestList)
reg("talkaction", "aleta som", subownerList)
reg("talkaction", "aleta grav", doorAccess)