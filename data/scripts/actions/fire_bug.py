thingId = 5466
fireBugs = 5468
#need to be able to burn spider webs and light empty coal basins
def onUse(creature, position, stackpos, onId, onThing, onPosition, onStackpos, **k):
    if onId == 5466: # Sugar cane
        if(random.randint(0,20) == 0):
            creature.modifyHealth(-5)
            magicEffect(position, EFFECT_EXPLOSIONAREA)
            creature.removeItem(position, stackpos)

        onThing.transform(5465, onPosition)

    else:
        return False

reg('useWith', thingId, onUse)