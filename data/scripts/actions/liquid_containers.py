containers = 2005

def onUse(creature, thing, position, onThing, **k):
    print thing.itemId
    print onThing.itemId
    if not thing.type and onThing.type:
        thing.type = onThing.type
    creature.removeItem(position)
    creature.addItem(thing)
    
register('useWith', containers, onUse)