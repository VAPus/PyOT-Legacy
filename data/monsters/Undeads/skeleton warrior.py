import game.monster

skeleton_warrior = game.monster.genMonster("Skeleton Warrior", (298, 5972), "a skeleton warrior")
skeleton_warrior.setHealth(65)
skeleton_warrior.bloodType(color="undead")
skeleton_warrior.setDefense(armor=10, fire=1, earth=1, energy=1, ice=1, holy=1.25, death=0, physical=1, drown=1)
skeleton_warrior.setExperience(45)
skeleton_warrior.setSpeed(180)
skeleton_warrior.setBehavior(summonable=350, attackable=1, hostile=1, illusionable=1, convinceable=350, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
skeleton_warrior.walkAround(energy=1, fire=1, poison=1)
skeleton_warrior.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=0)