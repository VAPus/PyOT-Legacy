def onUse(creature, thing, position, **k):
    if thing.itemId == creature.inventory[SLOT_HEAD].itemId:
        magicEffect(creature.position, EFFECT_GIFT_WRAPS)
    return True

register("use", 6578, onUse)
