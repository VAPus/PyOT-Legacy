import game.monster

kongra = game.monster.genMonster("Kongra", (116, 6043), "a kongra")
kongra.setHealth(340)
kongra.voices("Hugah!", "Ungh! Ungh!", "Huaauaauaauaa!")
kongra.setDefense(18, 14, 1,2, 1.1, 1.05, 1, 0.95) # armor, defense, fire, earth, energy, ice, holy, death

# Note, kongra is not spawned on map, so we spawn it ourself for test purposes
"""import game.map

def onPostLoadSector():
    game.monster.getMonster("Kongra").spawn([75,75,7])

game.map.regPostLoadSector(2,2, onPostLoadSector)"""