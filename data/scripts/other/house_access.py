def _houseCheck(creature):
    houseId = getHouseId(creature.position)
    if not houseId:
        creature.message("Your not standing in a house")
        return False
    
    house = getHouseById(houseId)
    if not house:
        creature.message("MAPPING/SQL ERROR! House not found")
        return False

    if creature.data["id"] != house.owner and not house.isSubOwner(creature):
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
        # Perform owner check
        if creature.data["id"] != house.owner:
            creature.message("Your not the owner of this house")
            return False  
            
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

# Is he allowed to enter the house?
def guestListCheck(creature, thing, newTile, **k):
    try:
        house = getHouseById(newTile.houseId)
        if not house:
            return True
        
        elif house.isGuest(creature) or house.isSubOwner(creature) or creature.data["id"] == house.owner:
            return True

        else:
            return False
    except:
        return True # Not a house. Mapping bug.

# Close door?
def houseDoorUseCheck(creature, thing, position, **k):
    try:
        if not thing.doorId:
            return True # No doorId on this door.
            
        house = getHouseById(getTile(position).houseId)
        if not house:
            return True
        
        elif house.haveDoorAccess(thing.doorId, creature) or house.isSubOwner(creature) or creature.data["id"] == house.owner:
            return True

        else:
            return False
    except:
        return True # Not a house. Mapping bug.

def kickFromHouse(creature, text, **k):
    if creature.name() == text:
        creature.kickFromHouse()
        return

    house = getHouseById(getTile(position).houseId)
    if not house:
        return
    elif house.isSubOwner(creature) or creature.data["id"] == house.owner:
        # Player is online?
        try:
            player = game.player.allPlayers[text]
            
            # Is he in our house?
            if getTile(player.position).houseId == house.id:
                creature.kickFromHouse()
            
        except:
            return
    
registerFirst("use", "houseDoor", houseDoorUseCheck)
registerFirst("preWalkOn", "houseDoor", guestListCheck)
register("talkaction", "aleta sio", guestList)
register("talkaction", "aleta som", subownerList)
register("talkaction", "aleta grav", doorAccess)
register("talkactionFirstWord", "alana sio", kickFromHouse)