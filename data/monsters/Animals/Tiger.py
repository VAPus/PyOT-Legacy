import game.monster

Tiger = game.monster.genMonster("Tiger", (125, 6051), "a tiger")
Tiger.setTargetChance(10)
Tiger.bloodType("blood")
Tiger.setHealth(75)
Tiger.setExperience(40)
Tiger.setSpeed(200) #correct
Tiger.walkAround(1,1,1) # energy, fire, poison
Tiger.setBehavior(summonable=420, attackable=1, hostile=1, illusionable=420, convinceable=420, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Tiger.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Tiger.setDefense(5, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.05, physical=1.0, drown=1.0)
Tiger.regMelee(50)

# Notice on loot, there is 3 formats (name/id, chance) chance equals the chance to get 1, (name/id, chance, maxCount) if chance checksout random one between 1 to maxCount, (name/id, chance, maxCount, minCount), same as previous, but always yields minCount
# Chance can be a float number with max two desimals (more will just be rounded upwards)
# Etc 100 or 12.5 or 55.52
# maxCount can be more then 100 (it splits internally), but minCount is max 100

Tiger.loot( ('meat', 100, 3), ('striped fur', 11) )