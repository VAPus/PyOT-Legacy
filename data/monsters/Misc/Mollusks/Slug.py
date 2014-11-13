# bad
Slug = genMonster("Slug", (407, 6079), "a slug") # not right yet
Slug.setTargetChance(10)
Slug.type("blood")
Slug.health(255)
Slug.experience(70)
Slug.speed(200) #incorrect
Slug.walkAround(1,1,1) # energy, fire, poison
Slug.behavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Slug.immunity(0,0,0) # paralyze, invisible, lifedrain
Slug.defense(9, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Slug.loot( ('gold coin', 62.5, 40), ('worm', 5, 3) )
Slug.regMelee(45)