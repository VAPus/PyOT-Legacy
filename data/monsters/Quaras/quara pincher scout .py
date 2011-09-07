import game.monster

quara_pincher_scout = game.monster.genMonster("Quara Pincher Scout", (77, 6063), "a quara pincher scout")
quara_pincher_scout.setHealth(1800)
quara_pincher_scout.bloodType(color="blood")
quara_pincher_scout.setDefense(armor=80, fire=0, earth=1.1, energy=1.1, ice=0, holy=1, death=1, physical=1, drown=0)
quara_pincher_scout.setExperience(1200)
quara_pincher_scout.setSpeed(250)
quara_pincher_scout.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
quara_pincher_scout.walkAround(energy=1, fire=0, poison=1)
quara_pincher_scout.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)
quara_pincher_scout.voices("Clank! Clank!", "Clap!", "Crrrk! Crrrk!")