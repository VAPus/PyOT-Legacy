from game.scriptsystem import reg
from game.engine import transformItem, updateTile
import random
import game.enum as enum

thingId = 5466
fireBugs = 5468

def onUse(creature, position, stackpos, onId, onThing, onPosition, onStackpos, **k):
    if onId == 5466: # Sugar cane
        if(random.randint(0,20) == 0):
            creature.modifyHealth(-5)
            creature.magicEffect(position, enum.EFFECT_EXPLOSIONAREA)
            creature.removeItem(position, stackpos)

        transformItem(onThing, 5465, onPosition)

    else:
        return False

reg('useWith', thingId, onUse)