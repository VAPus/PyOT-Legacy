def onUseWith(creature, thing, position, onThing, onPosition, **k):
    rand = random.randint(1, 2)
    if onThing.itemId == 7528:
        onThing.transform(7529, onPosition)
    elif onThing.itemId == 7529:
        if rand == 1:
            onThing.transform(7530, onPosition)
        elif rand == 2:
            onThing.transform(7531, onPosition)
    elif onThing.itemId == 7530:
        if rand == 1:
            onThing.transform(7532, onPosition)
        elif rand == 2:
            onThing.transform(7533, onPosition)
    elif onThing.itemId == 7532:
        if rand == 1:
            onThing.transform(7534, onPosition)
        elif rand == 2:
            onThing.transform(7535, onPosition)
    
    return True

register("useWith", 2600, onUseWith)
