import game.monster

demon_skeleton = game.monster.genMonster("Demon Skeleton", (37, 5963), "a demon skeleton")
demon_skeleton.setHealth(400)
demon_skeleton.bloodType(color="undead")
demon_skeleton.setDefense(armor=25, fire=0, earth=0, energy=1, ice=1, holy=1.25, death=0, physical=1, drown=0)
demon_skeleton.setExperience(240)
demon_skeleton.setSpeed(230)
demon_skeleton.setBehavior(summonable=620, attackable=1, hostile=1, illusionable=1, convinceable=620, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
demon_skeleton.walkAround(energy=1, fire=0, poison=0)
demon_skeleton.setImmunity(paralyze=1, invisible=0, lifedrain=1, drunk=1)