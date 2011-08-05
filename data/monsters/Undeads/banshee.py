import game.monster

banshee = game.monster.genMonster("Banshee", (78, 6019), "a banshee")
banshee.setHealth(1000)
banshee.bloodType(color="blood")
banshee.setDefense(15, fire=0, earth=0, energy=1, ice=1, holy=1.25, death=0, physical=1, drown=0)
banshee.setExperience(900)
banshee.setSpeed(220)
banshee.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=599)
banshee.walkAround(energy=1, fire=0, poison=0)
banshee.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
banshee.voices("Dance for me your dance of death!", "Let the music play!", "I will mourn your death!", "Are you ready to rock?", "Feel my gentle kiss of death.", "That's what I call easy listening!", "IIIIEEEeeeeeehhhHHHH!")