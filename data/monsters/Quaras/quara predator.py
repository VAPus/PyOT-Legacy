import game.monster

quara_predator = game.monster.genMonster("Quara Predator", (20, 6067), "a quara predator")
quara_predator.setHealth(2200)
quara_predator.bloodType(color="blood")
quara_predator.setDefense(armor=40, fire=0, earth=1.1, energy=1.25, ice=0, holy=1, death=1, physical=1, drown=0)
quara_predator.setExperience(1600)
quara_predator.setSpeed(520)
quara_predator.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
quara_predator.walkAround(energy=1, fire=0, poison=1)
quara_predator.setImmunity(paralyze=1, invisible=0, lifedrain=0, drunk=0)
quara_predator.voices("Gnarrr!", "Tcharrr!", "Rrrah!", "Rraaar!")