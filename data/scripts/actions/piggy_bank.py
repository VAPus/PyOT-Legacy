BROKEN_PIGGY_BANK = 2115

def onUse(creature, thing, position, **k):
    if random.randint(1, 6) != 1:
        creature.magicEffect(EFFECT_POFF)
        creature.addItem(Item(2148, 1))
        thing.transform(BROKEN_PIGGY_BANK, position)
    else:
        creature.magicEffect(EFFECT_SOUND_YELLOW)
        creature.addItem(Item(2152, 1))
    return True



register("use", 2114, onUse)
