butterfly = game.monster.genMonster("Butterfly", (213, 4993), "a butterfly")
butterfly.setHealth(2)
butterfly.bloodType(color="slime")
butterfly.setSpeed(300)
butterfly.setBehavior(summonable=0, hostile=0, illusionable=1, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
butterfly.walkAround(energy=1, fire=1, poison=1)
#note 4313 is an old used butterfly corpse sprite or second stage of decay?