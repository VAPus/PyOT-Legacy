convert = {}
convert[2956] = 5905 # Vampire dust
convert[2916] = 5906 # Demon dust

@register("useWith", 5942)
def useWith(creature, thing, onThing, onPosition, **k):
    if not onThing.itemId in convert:
        return

    if random.randint(1,15) == 1:
        try:
            creature.addItem(Item(convert[onThing.itemId]))
            magicEffect(onPosition, EFFECT_STUN)
        except:
            creature.notPossible()
            return
    else:
        magicEffect(onPosition, EFFECT_BLOCKHIT)

    onThing.transform(onThing.itemId + 1)

