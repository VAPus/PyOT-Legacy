import game.monster

orc_leader = game.monster.genMonster("Orc Leader", (59, 6001), "an orc leader")
orc_leader.setHealth(450, healthmax=450)
orc_leader.bloodType(color="blood")
orc_leader.setDefense(armor=20, fire=0, earth=1.1, energy=0.8, ice=1, holy=0.8, death=1.1, physical=1, drown=1)
orc_leader.setExperience(270)
orc_leader.setSpeed(230)
orc_leader.setBehavior(summonable=640, hostile=1, illusionable=1, convinceable=640, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
orc_leader.walkAround(energy=1, fire=0, poison=1)
orc_leader.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=1)
orc_leader.voices("Ulderek futgyr human!")
orc_leader.regMelee(185)