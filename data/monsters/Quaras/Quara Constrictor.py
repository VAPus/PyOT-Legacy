
quara_constrictor = game.monster.genMonster("Quara Constrictor", (46, 6065), "a quara constrictor")
quara_constrictor.setHealth(450)
quara_constrictor.bloodType(color="undead")
quara_constrictor.setDefense(armor=15, fire=0, earth=1.1, energy=1.25, ice=0, holy=1, death=1, physical=1, drown=0)
quara_constrictor.setExperience(250)
quara_constrictor.setSpeed(520)
quara_constrictor.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=670, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
quara_constrictor.walkAround(energy=1, fire=0, poison=1)
quara_constrictor.setImmunity(paralyze=1, invisible=0, lifedrain=0, drunk=1)
quara_constrictor.voices("Boohaa!", "Tssss!", "Gluh! Gluh!", "Gaaahhh!")
quara_constrictor.regMelee(150) #poisons you for 1 hp/turn
quara_constrictor.loot( (2148, 100, 100), ('fish fin', 0.5, 3), ('brass armor', 2.25), ('small amethyst', 0.25), ('longsword', 5.0), ('shrimp', 5.5), ('quara tentacle', 10.0) )