import game.monster

grave_guard = game.monster.genMonster("Grave Guard", (234, 6328), "a grave guard")#incorrect corpse?
grave_guard.setHealth(720)
grave_guard.bloodType(color="blood")
grave_guard.setDefense(20, armor=20, fire=0, earth=1, energy=1, ice=1.1, holy=1.1, death=1, physical=1, drown=1)
grave_guard.setExperience(485)
grave_guard.setSpeed(250)#unknown speed
grave_guard.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
grave_guard.walkAround(energy=0, fire=0, poison=0)
grave_guard.setImmunity(paralyze=0, invisible=1, lifedrain=0, drunk=1)