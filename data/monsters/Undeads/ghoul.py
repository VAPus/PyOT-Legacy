import game.monster

ghoul = game.monster.genMonster("Ghoul", (18, 5976), "a ghoul")
ghoul.setHealth(100)
ghoul.bloodType(color="blood")
ghoul.setDefense(armor=8, fire=1, earth=0.8, energy=0.7, ice=0.9, holy=1.25, death=0, physical=1, drown=0)
ghoul.setExperience(85)
ghoul.setSpeed(144)
ghoul.setBehavior(summonable=450, attackable=1, hostile=1, illusionable=1, convinceable=450, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
ghoul.walkAround(energy=1, fire=1, poison=1)
ghoul.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
ghoul.regMelee(70)