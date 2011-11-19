DISTILLERY = (5469, 5470, 5513, 5514)

def onUseWith(creature, thing, position, onThing, onPosition, **k):
    if onThing.itemId in DISTILLERY:
        if 'DISTILLERY_FULL' not in onThing.actions:
            onThing.description = 'It is full.'
            onThing.actions.append('DISTILLERY_FULL')
            creature.modifyItem(thing, position, stackpos, -1)
        else:
            creature.message('The machine is already full with bunches of sugar cane.')
        return True
    
    return False


reg("useWith", 5467, onUseWith)
