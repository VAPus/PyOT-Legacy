import game.monster

kongra = game.monster.genMonster("Kongra", (116, 6043), "a kongra")
kongra.setHealth(340)
kongra.voices("Hugah!", "Ungh! Ungh!", "Huaauaauaauaa!")
kongra.setDefense(18, 1,2, 1.1, 1.05, 1, 0.95) # armor, defense, fire, earth, energy, ice, holy, death

def onFollow(creature, target):
    target.say("Help me! Wild kongra on the run! <Scripted event>")
    
kongra.regOnFollow(onFollow) # can also be done as game.monster.getMonster("kongra").regOnFollow(function)