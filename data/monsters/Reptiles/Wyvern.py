
wyvern = game.monster.genMonster("Wyvern", (239, 6302), "a wyvern")
wyvern.setHealth(795)
wyvern.bloodType(color="blood")
wyvern.setDefense(armor=18, fire=1, earth=0, energy=0.8, ice=0.9, holy=1, death=1, physical=1, drown=1)
wyvern.setExperience(515)
wyvern.setSpeed(200)
wyvern.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=300)
wyvern.walkAround(energy=1, fire=1, poison=0)
wyvern.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
wyvern.voices("Shriiiek")
wyvern.regMelee(120) #(poisons you, starting from up to 24