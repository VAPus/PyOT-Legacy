import game.monster

deer = game.monster.genMonster("Deer", (31, 5970), "a deer")
deer.setHealth(25)
deer.setDefence(2)
deer.setBehavior(summonable=1, pushItems=0, pushCreatures=0, runOnHealth=25)