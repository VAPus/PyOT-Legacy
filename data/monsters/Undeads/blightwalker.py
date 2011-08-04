import game.monster

blightwalker = game.monster.genMonster("Blightwalker", (246, 6354), "a blightwalker")
blightwalker.setHealth(8900)
blightwalker.bloodType(color="undead")
blightwalker.setDefense(15, armor=15, fire=0.5, earth=0, energy=0.8, ice=0.5, holy=1.3, death=0, physical=1.1, drown=1)
blightwalker.setExperience(5850)
blightwalker.setSpeed(240)
blightwalker.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
blightwalker.walkAround(energy=1, fire=0, poison=0)
blightwalker.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=0)
blightwalker.voices("I can see you decaying!", "Let me taste your mortality!", "Your lifeforce is waning!)