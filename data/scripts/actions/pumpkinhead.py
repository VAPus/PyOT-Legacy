PUMPKIN = 2683
PUMPKINHEAD_LIGHT_OFF = 2096
PUMPKINHEAD_LIGHT_ON = 2097
CANDLE = 2048
KNIFE = 2566

def onUseWith(creature, thing, position, onThing, onPosition, **k):
    if thing.itemId == PUMPKINHEAD_LIGHT_OFF and onThing.itemId == CANDLE:
        thing.transform(PUMPKINHEAD_LIGHT_ON, position)
        creature.removeItem(onPosition)
    elif thing.itemId == KNIFE and onThing.itemId == PUMPKIN:
        onThing.transform(PUMPKINHEAD_LIGHT_OFF, onPosition)
    else:
        return False
    
    return True



register("useWith", (2566, 2096), onUseWith)