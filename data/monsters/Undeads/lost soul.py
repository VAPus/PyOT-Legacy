import game.monster

lost_soul = game.monster.genMonster("Lost Soul", (232, 6310), "a lost soul")
lost_soul.setHealth(5800)
lost_soul.bloodType(color="undead")
lost_soul.setDefense(armor=25, fire=0, earth=0, energy=0.9, ice=0.5, holy=1.25, death=0, physical=1, drown=1)
lost_soul.setExperience(4000)
lost_soul.setSpeed(250)
lost_soul.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
lost_soul.walkAround(energy=1, fire=0, poison=0)
lost_soul.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=0)
lost_soul.voices("Mouuuurn meeee!", "Forgive Meee!", "Help meee!")
lost_soul.regMelee(420)