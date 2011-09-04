import game.monster

island_troll = game.monster.genMonster("Island Troll", (282, 7930), "an island troll")
island_troll.setHealth(50)
island_troll.bloodType(color="blood")
island_troll.setDefense(armor=7, fire=1, earth=1, energy=1, ice=1, holy=1, death=1, physical=1, drown=1)
island_troll.setExperience(20)
island_troll.setSpeed(190)
island_troll.setBehavior(summonable=290, attackable=1, hostile=1, illusionable=1, convinceable=290, pushable=1, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=15)
island_troll.walkAround(energy=1, fire=1, poison=1)
island_troll.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)
island_troll.voices("Hmmm, turtles", "Hmmm, dogs", "Hmmm, worms", "Groar", "Gruntz!")
island_troll.regMelee(10)