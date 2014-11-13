herald_of_gloom = genMonster("Herald of Gloom", (320, 9915), "a herald of gloom")
herald_of_gloom.health(450, healthmax=450)
herald_of_gloom.type("blood")#undead?
herald_of_gloom.defense(armor=24, fire=0.6, earth=0.3, energy=1, ice=1, holy=1.1, death=0.9, physical=1.05, drown=1)
herald_of_gloom.experience(450)
herald_of_gloom.speed(300)#
herald_of_gloom.behavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
herald_of_gloom.walkAround(energy=0, fire=0, poison=0)
herald_of_gloom.immunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
herald_of_gloom.regMelee(100)
herald_of_gloom.loot( ("midnight shard", 3.0) )