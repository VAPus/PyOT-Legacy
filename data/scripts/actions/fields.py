
def effectOverTime(creature, damage, perTime, effect, forTicks, ticks=0):
    if not creature.alive:
        return

    ticks += 1
    creature.modifyHealth(-damage)
    creature.magicEffect(effect)


    if ticks < forTicks:
        callLater(perTime, effectOverTime, creature, damage, perTime, effect, forTicks, ticks)

def callback(creature, thing, **k):
    if thing.fieldDamage:
        creature.magicEffect(typeToEffect(thing.field)[0])
        creature.modifyHealth(-thing.fieldDamage)
        if thing.turns:
            try:
                effect = typeToEffect(thing.field)[1]
            except:
                effect = EFFECT_POOF

            effectOverTime(creature, thing.fieldDamage, thing.fieldTicks / 1000,effect, thing.fieldCount)

registerForAttr('walkOn', 'fieldDamage', callback)
