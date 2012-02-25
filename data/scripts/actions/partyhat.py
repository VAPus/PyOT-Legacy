# Autoconverted script for PyOT
# Untested. Please remove this message when the script is working properly!

def onUse(creature, thing, position, **k):
    if thing.itemId == creature.inventory[SLOT_HEAD].itemId:
        magicEffect(creature.position, EFFECT_GIFT_WRAPS)
    return True

register("use", 6578, onUse)
