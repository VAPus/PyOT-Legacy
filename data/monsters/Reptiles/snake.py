import game.monster

snake = game.monster.genMonster("Snake", (28, 2817), "a snake")
snake.setHealth(15)
snake.bloodType(color="blood")
snake.setDefense(armor=2, fire=1.1, earth=0, energy=0.8, ice=1.1, holy=1, death=1, physical=1, drown=1)
snake.setExperience(10)
snake.setSpeed(120)
snake.setBehavior(summonable=205, hostile=1, illusionable=1, convinceable=205, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
snake.walkAround(energy=1, fire=1, poison=0)
snake.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
snake.voices("Zzzzzzt")
snake.regMelee(8) #it Poison with 1 hp/turn