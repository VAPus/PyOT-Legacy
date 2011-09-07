import game.monster

quara_pincher = game.monster.genMonster("Quara Pincher", (77, 6063), "a quara pincher")
quara_pincher.setHealth(1800)
quara_pincher.bloodType(color="blood")
quara_pincher.setDefense(armor=20, fire=0, earth=1.1, energy=1.25, ice=0, holy=1, death=1, physical=1, drown=0)
quara_pincher.setExperience(1200)
quara_pincher.setSpeed(540)
quara_pincher.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
quara_pincher.walkAround(energy=1, fire=0, poison=1)
quara_pincher.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)
quara_pincher.voices("Clank! Clank!", "Clap!", "Crrrk! Crrrk!")