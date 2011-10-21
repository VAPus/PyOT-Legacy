
quara_hydromancer = game.monster.genMonster("Quara Hydromancer", (47, 6066), "a quara hydromancer")
quara_hydromancer.setHealth(1100)
quara_hydromancer.bloodType(color="blood")
quara_hydromancer.setDefense(armor=17, fire=0, earth=1.1, energy=1.25, ice=0, holy=1, death=1, physical=1, drown=0)
quara_hydromancer.setExperience(800)
quara_hydromancer.setSpeed(520)
quara_hydromancer.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=30)
quara_hydromancer.walkAround(energy=1, fire=0, poison=1)
quara_hydromancer.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
quara_hydromancer.voices("Qua hah tsh!", "Teech tsha tshul!", "Quara tsha Fach!", "Tssssha Quara!", "Blubber.", "Blup.")
quara_hydromancer.regMelee(80) #poisons you for up to 5 hp/turn
quara_hydromancer.loot( (2148, 100, 90), ('white pearl', 1.75), ('black pearl', 2.0), ('small emerald', 1.25, 2), ('quara eye', 10.25), ('shrimp', 5.0), ('knight armor', 0.25), ('fish fin', 1.0, 3), ('wand of cosmic energy', 1.0), ('ring of healing', 0.5), ('great mana potion', 1.0) )