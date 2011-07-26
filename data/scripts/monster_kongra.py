import game.monster

kongra = game.monster.genMonster("Kongra", (116, 6043), "a kongra")
kongra.setHealth(340)
kongra.voices("Hugah!", "Ungh! Ungh!", "Huaauaauaauaa!")
kongra.setDefense(18, 14, 1,2, 1.1, 1.05, 1, 0.95) # armor, defense, fire, earth, energy, ice, holy, death

def onFollow(creature, target):
    target.say("Help me! Wild kongra on the run! <Scripted event>")
    
kongra.regOnFollow(onFollow) # can also be done as game.monster.getMonster("kongra").regOnFollow(function)

# Note, kongra is not spawned on map, so we spawn it ourself for test purposes
import game.map

def onPostLoadSector():
    game.monster.getMonster("Kongra").spawn([52,52,7])

game.map.regPostLoadSector(1,1, onPostLoadSector)