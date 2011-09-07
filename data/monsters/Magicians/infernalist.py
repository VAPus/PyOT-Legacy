import game.monster

infernalist = game.monster.genMonster("Infernalist", (130, 6080), "a infernalist")
infernalist.setOutfit(78, 76, 94, 115) #needs 2 addons
infernalist.setHealth(3650, healthmax=3650)
infernalist.bloodType(color="blood")
infernalist.setDefense(armor=20, fire=0, earth=0.05, energy=0, ice=1.05, holy=0.8, death=0.9, physical=1.05, drown=1)
infernalist.setExperience(4000)
infernalist.setSpeed(260)
infernalist.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=4, runOnHealth=1150)
infernalist.walkAround(energy=0, fire=0, poison=0)
infernalist.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
infernalist.voices("Nothing will remain but your scorched bones!", "Some like it hot!", "It's cooking time!", "Feel the heat of battle!")