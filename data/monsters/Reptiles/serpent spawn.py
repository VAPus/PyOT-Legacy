import game.monster

serpent_spawn = game.monster.genMonster("Serpent Spawn", (220, 4323), "a serpent spawn")
serpent_spawn.setHealth(3000)
serpent_spawn.bloodType(color="slime")
serpent_spawn.setDefense(armor=25, fire=1.1, earth=0, energy=1.1, ice=0.8, holy=1, death=1, physical=1, drown=1)
serpent_spawn.setExperience(3050)
serpent_spawn.setSpeed(240)
serpent_spawn.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=275)
serpent_spawn.walkAround(energy=1, fire=1, poison=0)
serpent_spawn.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=1)
serpent_spawn.voices("HISSSS", "I bring your deathhh, mortalssss", "Sssssouls for the one", "Tsssse one will risssse again")