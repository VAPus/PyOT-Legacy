
def effectOverTime(creature, damage, perTime, effect, forTicks, ticks=0):
    if not creature.alive:
        return

    ticks += 1
    creature.onHit(None, -thing.fieldDamage, getattr(game.enum, thing.field.upper()), False)
    creature.magicEffect(effect)


    if ticks < forTicks:
        callLater(perTime, effectOverTime, creature, damage, perTime, effect, forTicks, ticks)

def callback(creature, thing, **k):
    if thing.fieldDamage:
        try:
            effect, effectOverTime = typeToEffect(thing.field)[0:2]
        except:
            effect = EFFECT_POFF
            effectOverTime = EFFECT_POFF

        creature.magicEffect(effect)
        creature.onHit(None, -thing.fieldDamage, getattr(game.enum, thing.field.upper()), False)

        if thing.fieldCount:
            callLater(thing.fieldTicks / 1000, effectOverTime, creature, thing.fieldDamage, thing.fieldTicks / 1000, effectOverTime, thing.fieldCount)

registerForAttr('walkOn', 'fieldDamage', callback)
