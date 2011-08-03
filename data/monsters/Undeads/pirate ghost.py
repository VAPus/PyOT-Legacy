import game.monster

pirate_ghost = game.monster.genMonster("Pirate Ghost", (35, 5995), "a pirate ghost")
pirate_ghost.setHealth(275)
pirate_ghost.bloodType(color="undead")
pirate_ghost.setDefense(25, armor=20, fire=1, earth=0, energy=1, ice=1, holy=1.25, death=0, physical=0, drown=1)
pirate_ghost.setExperience(250)
pirate_ghost.setSpeed(230)
pirate_ghost.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=1, convinceable=0, pushable=1, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
pirate_ghost.walkAround(energy=1, fire=1, poison=0)
pirate_ghost.setImmunity(paralyze=1, invisible=0, lifedrain=1, drunk=0)
pirate_ghost.voices("Yooh Ho Hooh Ho!", "Hell is waiting for You!", "It's alive!", "The curse! Aww the curse!", "You will not get my treasure!")