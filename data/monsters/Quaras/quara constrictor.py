import game.monster

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