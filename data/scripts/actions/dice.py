def onUse(creature, thing, position, **k):
    rolled = random.randint(1,6)
    creature.say("%s rolled a %d" % (creature.name(), rolled))
    thing.transform(5791 + rolled, position)
    
    creature.magicEffect(EFFECT_CRAPS)

reg("use", 5792, onUse, 5797)