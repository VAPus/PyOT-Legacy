import game.monster

quara_mantassin_scout = game.monster.genMonster("Quara Mantassin Scout", (72, 6064), "a quara mantassin scout")
quara_mantassin_scout.setHealth(220)
quara_mantassin_scout.bloodType(color="blood")
quara_mantassin_scout.setDefense(armor=15, fire=0, earth=1.1, energy=1.1, ice=0, holy=1, death=1, physical=1, drown=0)
quara_mantassin_scout.setExperience(100)
quara_mantassin_scout.setSpeed(270)
quara_mantassin_scout.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=480, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=40)
quara_mantassin_scout.walkAround(energy=1, fire=0, poison=1)
quara_mantassin_scout.setImmunity(paralyze=1, invisible=0, lifedrain=0, drunk=1)
quara_mantassin_scout.voices("Shrrrr", "Zuerk Pachak!")
quara_mantassin_scout.regMelee(110)