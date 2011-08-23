import game.monster

necromancer = game.monster.genMonster("Necromancer", (9, 6080), "a necromancer")
necromancer.setHealth(580, healthmax=580)
necromancer.bloodType(color="blood")
necromancer.setDefense(armor=20, fire=1.05, earth=0, energy=0.8, ice=0.9, holy=1.05, death=0.5, physical=1.05, drown=1)
necromancer.setExperience(580)
necromancer.setSpeed(200)
necromancer.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=4, runOnHealth=0)
necromancer.walkAround(energy=1, fire=1, poison=0)
necromancer.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
necromancer.voices("Taste the sweetness of death!", "Your corpse will be mine.")