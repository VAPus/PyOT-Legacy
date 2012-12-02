@register("use", 3699)
def onUse(thing, position, **k):
    thing.transform(3700)
    Item(2677, 3).place(position)
    thing.decay()

