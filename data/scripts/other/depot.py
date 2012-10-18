depots = (2594, 2592)

@registerFirst('use', 2594) # We got to register it first so we call it before container open
def openDepot(creature, thing, **k):
    if thing.owners and creature not in thing.owners:
        creature.lmessage("This depot box is already in use by someone else")
        return False
        
    if thing.depotId:
        thing.owners = [creature]
        if thing.depotId in creature.depot:
            thing.container.items = creature.depot[thing.depotId]

@register('close', 2594)
def closeDepot(creature, thing, **k):
    if thing.depotId:
        creature.depot[thing.depotId] = thing.container.items[:]
        thing.container.items = []
        thing.owners = []

@registerFirst('use', 2592)
def openLocker(creature, thing, **k):
    depot = Item(2594)
    depot.depotId = thing.depotId
    thing.containerSize = 3
    thing.container = [depot, Item(2334)]
    