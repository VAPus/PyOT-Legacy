
dark_apprentice = game.monster.genMonster("Dark Apprentice", (133, 3058), "a dark apprentice")
dark_apprentice.setOutfit(78, 38, 95, 115) #needs addon
dark_apprentice.setHealth(225, healthmax=225)
dark_apprentice.bloodType(color="blood")
dark_apprentice.setDefense(armor=16, fire=1, earth=1, energy=1, ice=1, holy=1, death=1.05, physical=1, drown=1)
dark_apprentice.setExperience(100)
dark_apprentice.setSpeed(220)
dark_apprentice.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=4, runOnHealth=80)
dark_apprentice.walkAround(energy=1, fire=1, poison=1)
dark_apprentice.setImmunity(paralyze=0, invisible=1, lifedrain=0, drunk=0)
dark_apprentice.voices("Outch!", "I must dispose of my masters enemies!", "Oops, I did it again.", "From the spirits that I called Sir, deliver me!")
dark_apprentice.regMelee(30)
dark_apprentice.loot( ("wand of dragonbreath", 2.0), ("dead frog", 12.25), ("health potion", 3.25), ("blank rune", 16.0, 3), (2148, 100, 45), ("mana potion", 3.0), ("wand of decay", 0.0025), ("reins", 0.0025) )