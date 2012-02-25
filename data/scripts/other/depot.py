depots = (2594, 2592)

def openDepot(creature, thing, **k):
    if thing.owners and creature not in thing.owners:
        creature.message("This depot box is already in use by someone else")
        return False
        
    if thing.depotId:
        thing.owners = [creature]
        if thing.depotId in creature.depot:
            thing.container.items = creature.depot[thing.depotId]

def closeDepot(creature, thing, **k):
    if thing.depotId:
        creature.depot[thing.depotId] = thing.container.items[:]
        thing.container.items = []
        thing.owners = []

registerFirst('use', depots, openDepot) # We got to register it first so we call it before container open
register('close', depots, closeDepot)