def _verify(creature, thing, position):
    if creature.position != position: return

    if not creature.hasCondition(getattr(game.enum, 'CONDITION_%s' % (thing.field.upper()))):
        every = (thing.fieldTicks or 2000)/1000
        creature.condition(Condition(getattr(game.enum, 'CONDITION_%s' % (thing.field.upper())), length=every * (thing.fieldCount or 1), every=every, damage=thing.fieldDamage))
    callLater((thing.fieldTicks or 2000)/1000, _verify, creature, thing, position)

def callback(creature, thing, position, **k):
    if thing.fieldDamage:
        every = (thing.fieldTicks or 2000)/1000
        creature.condition(Condition(getattr(game.enum, 'CONDITION_%s' % (thing.field.upper())), length=every * (thing.fieldCount or 1), every=every, damage=thing.fieldDamage))
        callLater(every, _verify, creature, thing, position)
    
registerForAttr('walkOn', 'fieldDamage', callback)
