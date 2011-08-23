import game.monster

fury = game.monster.genMonster("Fury", (149, 6081), "a fury")
fury.setOutfit(94, 77, 96, 0) #needs addons
fury.setHealth(4100, healthmax=4100)
fury.bloodType(color="blood")
fury.setDefense(armor=20, fire=0, earth=1.1, energy=1.1, ice=0.7, holy=0.7, death=1.1, physical=1.1, drown=1)
fury.setExperience(4000)
fury.setSpeed(460)
fury.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
fury.walkAround(energy=0, fire=0, poison=0)
fury.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
fury.voices("Ahhhhrrrr!", "Waaaaah!", "Carnage!", "Dieee!")