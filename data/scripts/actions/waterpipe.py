def onUse(creature, thing, position, **k):
    magicEffect(creature.position, EFFECT_POFF)

register("use", 2093, onUse)