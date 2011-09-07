import game.monster

quara_predator_scount = game.monster.genMonster("Quara Predator Scount", (20, 6067), "a quara predator scount")
quara_predator_scount.setHealth(890)
quara_predator_scount.bloodType(color="blood")
quara_predator_scount.setDefense(armor=30, fire=0, earth=1.1, energy=1.1, ice=0, holy=1, death=1, physical=1, drown=0)
quara_predator_scount.setExperience(400)
quara_predator_scount.setSpeed(290)
quara_predator_scount.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
quara_predator_scount.walkAround(energy=1, fire=0, poison=1)
quara_predator_scount.setImmunity(paralyze=1, invisible=0, lifedrain=0, drunk=0)
quara_predator_scount.voices("Gnarrr!", "Tcharrr!", "Rrrah!", "Rraaar!")