import game.scriptsystem as scriptsystem

depots = (2594, 2592)

def openDepot(creature, thing, **k):
    if thing.depotId:
        if thing.depotId in creature.depot:
            thing.container.items = creature.depot[thing.depotId]

def closeDepot(creature, thing, **k):
    if thing.depotId:
        creature.depot[thing.depotId] = thing.container.items[:]
        thing.container.items = []

scriptsystem.regFirst('use', depots, openDepot) # We got to register it first so we call it before container open
scriptsystem.reg('close', depots, closeDepot)