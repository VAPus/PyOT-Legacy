import game.monster

killer_caiman = game.monster.genMonster("Killer Caiman ", (358, 11138), "a killer caiman ")
killer_caiman.setHealth(1500)
killer_caiman.bloodType(color="blood")
killer_caiman.setDefense(armor=45, fire=1, earth=0.8, energy=1.05, ice=0.9, holy=1, death=1, physical=0.95, drown=1)
killer_caiman.setExperience(800)
killer_caiman.setSpeed(240)
killer_caiman.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
killer_caiman.walkAround(energy=1, fire=1, poison=1)
killer_caiman.setImmunity(paralyze=0, invisible=1, lifedrain=0, drunk=0)
killer_caiman.regMelee(180)