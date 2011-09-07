import game.monster

lich = game.monster.genMonster("Lich", (99, 6028), "a lich")
lich.setHealth(880)
lich.bloodType(color="undead")
lich.setDefense(armor=20, fire=1, earth=0, energy=0.2, ice=1, holy=1.2, death=0, physical=1, drown=1)
lich.setExperience(900)
lich.setSpeed(320)
lich.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
lich.walkAround(energy=0, fire=1, poison=0)
lich.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=0)
lich.voices("Doomed be the living!", "Death awaits all!", "Thy living flesh offends me!", "Death and Decay!", "You will endure agony beyond thy death!", "Pain sweet pain!", "Come to me my children!")
lich.regMelee(75)