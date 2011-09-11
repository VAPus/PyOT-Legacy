from game.scriptsystem import reg
from game.engine import transformItem, updateTile
import random
import game.enum as enum

wheat = 2694
flour = 2692
dough = 2693
bread = 2689
mills = (1381, 1382, 1383, 1384)

def flourToDough(creature, position, thing, onThing, **k):
    print thing.itemId
    print onThing.itemId

    creature.removeItem(position)
    item.itemId = dough
    creature.itemToContainer(creature.inventory[2], item)

reg('useWith', (2692, 2693, 2694), flourToDough)