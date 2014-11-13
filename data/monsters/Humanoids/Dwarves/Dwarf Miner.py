#some unknown information
dwarf_miner = genMonster("Dwarf Miner", (160, 5980), "a dwarf miner")#corpse
dwarf_miner.setOutfit(95, 95, 95, 95)#
dwarf_miner.health(120)
dwarf_miner.type("blood")
dwarf_miner.defense(armor=9, fire=1.05, earth=0.9, energy=1, ice=1, holy=1, death=1.05, physical=1, drown=1)
dwarf_miner.experience(60)
dwarf_miner.speed(220)#
dwarf_miner.behavior(summonable=420, hostile=1, illusionable=1, convinceable=420, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
dwarf_miner.walkAround(energy=0, fire=0, poison=0)
dwarf_miner.immunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)
dwarf_miner.voices("Work, work!", "Intruders in the mines!", "Mine, all mine!")
dwarf_miner.regMelee(35)