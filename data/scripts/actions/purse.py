ALLOWED_ITEMS = ()

@register("useWith", 'purse')
def dragOnPurse(creature, thing, onThing, **k):
    if thing not in ALLOWED_ITEMS:
        creature.lmessage("You can't place this item in a purse")
        return False