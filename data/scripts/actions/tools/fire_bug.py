thingId = 5466
fireBugs = 5468
#need to be able to burn spider webs and light empty coal basins

@register('useWith', thingId)
def onUse(creature, position, onThing, onPosition, **k):
    if onThing.itemId == 5466: # Sugar cane
        if(random.randint(0,20) == 0):
            creature.modifyHealth(-5)
            magicEffect(position, EFFECT_EXPLOSIONAREA)
            creature.removeItem(position)

        onThing.transform(5465)

    else:
        return False