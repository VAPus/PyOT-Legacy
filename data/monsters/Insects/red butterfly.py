butterfly = game.monster.genMonster("Butterfly", (228, 4992), "a butterfly")
butterfly.setHealth(2)
butterfly.bloodType(color="slime")
butterfly.setSpeed(380)#incorrect speed
butterfly.setBehavior(summonable=0, hostile=0, illusionable=1, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
butterfly.walkAround(energy=1, fire=1, poison=1)