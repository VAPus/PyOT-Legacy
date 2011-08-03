import game.monster

mummy = game.monster.genMonster("Mummy", (65, 6004), "a mummy")
mummy.setHealth(240)
mummy.bloodType(color="undead")
mummy.setDefense(20, armor=14, fire=1, earth=1, energy=1, ice=0.8, holy=1.25, death=1, physical=1, drown=1)
mummy.setExperience(150)
mummy.setSpeed(220)
mummy.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
mummy.walkAround(energy=1, fire=1, poison=0)
mummy.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=0)
mummy.voices("I will ssswallow your sssoul!", "Mort ulhegh dakh visss.", "Flesssh to dussst!", "I will tassste life again!", "Ahkahra exura belil mort!", "Yohag Sssetham!")