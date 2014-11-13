butterfly = genMonster("Butterfly", (10, 5014), "a butterfly")
butterfly.health(2)
butterfly.type("slime")
butterfly.defense(armor=2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1)
butterfly.speed(300) #incorrect speed
butterfly.behavior(summonable=0, hostile=0, illusionable=1, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
butterfly.walkAround(energy=1, fire=1, poison=1)