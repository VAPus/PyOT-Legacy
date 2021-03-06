fire_devil = genMonster("Fire Devil", 40, 5985)
fire_devil.health(200)
fire_devil.type("blood")
fire_devil.defense(armor=13, fire=0, earth=0.8, energy=0.7, ice=1.2, holy=1.1, death=0.8, physical=0.9, drown=1)
fire_devil.experience(145)
fire_devil.speed(190)
fire_devil.behavior(summonable=530, hostile=True, illusionable=True, convinceable=530, pushable=False, pushItems=True, pushCreatures=False, targetDistance=4, runOnHealth=0)
fire_devil.walkAround(energy=1, fire=0, poison=1)
fire_devil.immunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)
fire_devil.voices("Hot, eh?", "Hell, oh, hell!")
fire_devil.melee(35)
fire_devil.loot( ("guardian shield", 0.5), ("small pitchfork", 20.5), ("blank rune", 10.5), ("double axe", 1.75), ("torch", 2.0, 2), ("cleaver", 1.25), ("scimitar", 4.75), ("necrotic rod", 0.5), ("small amethyst", 0.25) )