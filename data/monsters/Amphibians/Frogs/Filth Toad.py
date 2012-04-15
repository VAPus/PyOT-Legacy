Filth_Toad = game.monster.genMonster("Filth Toad", (222, 6077), "a filth toad")
Filth_Toad.setTargetChance(10)
Filth_Toad.bloodType("slime") ##?
Filth_Toad.setHealth(185)
Filth_Toad.setExperience(90)
Filth_Toad.setSpeed(280) ##?
Filth_Toad.walkAround(1,1,1) # energy, fire, poison
Filth_Toad.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0) ##convince?
Filth_Toad.voices("Ribbit!", "Ribbit! Ribbit!")
Filth_Toad.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Filth_Toad.setDefense(7, fire=1, earth=1, energy=1, ice=1, holy=1, death=1, physical=1, drown=1)

Filth_Toad.regSelfSpell("Haste", 360, 360, length=5, check=chance(21)) #?
Filth_Toad.regTargetSpell(2292, 8, 34, check=chance(21)) #is the range 1?
Filth_Toad.regMelee(4) #poisons you 1 hp for 5 turns