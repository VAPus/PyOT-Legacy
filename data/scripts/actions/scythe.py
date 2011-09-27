ITEM_PRE_WHEAT = 2739
ITEM_WHEAT = 2737
ITEM_BUNCH_WHEAT = 2694
ITEM_PRE_SUGAR_CANE = 5471
ITEM_SUGAR_CANE = 5463
ITEM_BUNCH_SUGAR_CANE = 5467

def onUseWith(creature, thing, position, onThing, onPosition, **k):
    if onThing.itemId == ITEM_PRE_WHEAT:
        doTransformItem(onThing.uid, ITEM_WHEAT)
        placeItem(Item(ITEM_BUNCH_WHEAT, 1), onPosition)
    elif onThing.itemId == ITEM_PRE_SUGAR_CANE:
        doTransformItem(onThing.uid, ITEM_SUGAR_CANE)
        placeItem(Item(ITEM_BUNCH_SUGAR_CANE, 1), onPosition)
    else:
        return False
    onThing.decay(onPosition)
    return True



reg("useWith", 2550, onUseWith)

