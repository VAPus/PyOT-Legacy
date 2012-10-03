#move to misc/shapeshifter folder
son_of_verminor = genMonster("Son Of Verminor", (19, 1496), "a son of verminor")
son_of_verminor.setHealth(8500)
son_of_verminor.bloodType(color="slime")
son_of_verminor.setDefense(armor=53, fire=0.9, earth=0, energy=0.8, ice=1, holy=1, death=1, physical=1, drown=1)
son_of_verminor.setExperience(5900)
son_of_verminor.setSpeed(120)#incorrect?
son_of_verminor.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
son_of_verminor.walkAround(energy=0, fire=1, poison=0)
son_of_verminor.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=0)
son_of_verminor.voices("Blubb.")
son_of_verminor.regMelee(460)
#Creature Illusion (appears as a Rat, Larva, Scorpion or Slime)