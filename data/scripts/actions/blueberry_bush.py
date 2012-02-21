def onUse(thing, position, **k):
    thing.transform(2786, position)
    placeItem(Item(2677, 3), position)
    thing.decay(position)

reg("use", 2785, onUse)