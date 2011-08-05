import game.monster

undead_prospector = game.monster.genMonster("Undead Prospector", (18, 5976), "an undead prospector")
undead_prospector.setHealth(100)
undead_prospector.bloodType(color="blood")
undead_prospector.setDefense(armor=17, fire=1, earth=0.8, energy=0.7, ice=0.9, holy=1.25, death=0, physical=1, drown=0)
undead_prospector.setExperience(85)
undead_prospector.setSpeed(180)
undead_prospector.setBehavior(summonable=440, attackable=1, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)#convinceable?
undead_prospector.walkAround(energy=1, fire=1, poison=1)
undead_prospector.setImmunity(paralyze=1, invisible=0, lifedrain=0, drunk=1)
undead_prospector.voices("Our mine... leave us alone.", "Turn back...", "These mine is ours... you shall not pass.")