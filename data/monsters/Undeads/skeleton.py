import game.monster

skeleton = game.monster.genMonster("Skeleton", (33, 5972), "a skeleton")
skeleton.setHealth(50)
skeleton.bloodType(color="undead")
skeleton.setDefense(armor=8, fire=1, earth=1, energy=1, ice=1, holy=1.25, death=0, physical=1, drown=1)
skeleton.setExperience(35)
skeleton.setSpeed(154)
skeleton.setBehavior(summonable=300, attackable=1, hostile=1, illusionable=1, convinceable=300, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
skeleton.walkAround(energy=1, fire=1, poison=1)
skeleton.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
skeleton.regMelee(17)