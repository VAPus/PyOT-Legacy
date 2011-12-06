midnight_warrior = game.monster.genMonster("Midnight Warrior", (8, 5980), "a midnight warrior")
midnight_warrior.setOutfit(95, 95, 95, 95)#
midnight_warrior.setHealth(1000)
midnight_warrior.bloodType(color="blood")
midnight_warrior.setDefense(armor=24, fire=1.1, earth=0, energy=0.8, ice=0.8, holy=1, death=1, physical=0.85, drown=1)#
midnight_warrior.setExperience(750)
midnight_warrior.setSpeed(300)#
midnight_warrior.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
midnight_warrior.walkAround(energy=0, fire=0, poison=0)
midnight_warrior.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
midnight_warrior.voices("I am champion of darkness and you are nothing.")
midnight_warrior.regMelee(150)#+or more and poisons up to 7 hp/turn
midnight_warrior.loot( ("midnight shard", 9.25) )