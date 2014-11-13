Filth_Toad = genMonster("Filth Toad", (222, 6077), "a filth toad")
Filth_Toad.setTargetChance(10)
Filth_Toad.type("slime") ##?
Filth_Toad.health(185)
Filth_Toad.experience(90)
Filth_Toad.speed(280) ##?
Filth_Toad.walkAround(1,1,1) # energy, fire, poison
Filth_Toad.behavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0) ##convince?
Filth_Toad.voices("Ribbit!", "Ribbit! Ribbit!")
Filth_Toad.immunity(0,0,0) # paralyze, invisible, lifedrain
Filth_Toad.defense(7, fire=1, earth=1, energy=1, ice=1, holy=1, death=1, physical=1, drown=1)

Filth_Toad.regMelee(4, condition=CountdownCondition(CONDITION_POISON, 1), conditionChance=100)
Filth_Toad.regSelfSpell("Haste", 360, 360, length=5, check=chance(21)) #?
Filth_Toad.regTargetSpell(2292, 8, 34, check=chance(21)) #is the range 1?