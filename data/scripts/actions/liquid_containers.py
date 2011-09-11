from game.scriptsystem import reg

containers = 2005

def onUse(creature, thing, position, stackpos, onThing, **k):
    print thing.itemId
    print onThing.itemId
    if not thing.type and onThing.type:
        thing.type = onThing.type
    creature.removeItem(position, stackpos)
    creature.itemToContainer(creature.inventory[2], thing)
    
reg('useWith', containers, onUse)