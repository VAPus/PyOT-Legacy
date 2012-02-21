# Autoconverted script for PyOT
# Untested. Please remove this message when the script is working properly!

def onUseWith(creature, thing, position, onThing, onPosition, **k):
    random = random.randint(1, 2)
    if onThing.itemId == 7528:
        onThing.transform(7529, onPosition)
    elif onThing.itemId == 7529:
        if random == 1:
            onThing.transform(7530, onPosition)
        elif random == 2:
            onThing.transform(7531, onPosition)
    elif onThing.itemId == 7530:
        if random == 1:
            onThing.transform(7532, onPosition)
        elif random == 2:
            onThing.transform(7533, onPosition)
    elif onThing.itemId == 7532:
        if random == 1:
            onThing.transform(7534, onPosition)
        elif random == 2:
            onThing.transform(7535, onPosition)
    
    return True

register("useWith", 2600, onUseWith)
