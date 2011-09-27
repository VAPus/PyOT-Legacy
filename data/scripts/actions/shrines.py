def onUseWith(creature, thing, position, onThing, onPosition, **k):
    if(onThing.itemId == HOTA_WEAK and thing.itemId == SMALL_RUBY):
        creature.modifyItem(thing, position, stackpos, -1)
        doTransformItem(onThing.uid, HOTA_FULL)
        doSendMagicEffect(onPosition, EFFECT_MAGIC_RED)
        return True
    
    if onThing.itemId in SHRINES[thing.itemId] == False:
        return False
    
    count = thing.type != 0 and thing.type or 1
    manaCost = 300 * count
    soulCost = 2 * count
    requiredLevel = 30
    
    if creature.data["level"] < requiredLevel:
        creature.notEnough('level')
        return True
    
    if creature.isPremium() == False:
        creature.needPremium()
        return True
    
    if creature.data["mana"] < manaCost:
        creature.notEnough('mana')
        return True
    
    if creature.data["soul"] < soulCost:
        creature.notEnough('soul')
        return True
    
    creature.modifyMana(-manaCost)
    creature.modifySoul(-soulCost)
    doTransformItem(thing.uid, ENCHANTED_GEMS[thing.itemId], count)
    
    return True


reg("useWith", (2146, 2147, 2149, 2150), onUseWith)

