import game.monster

sea_serpent = game.monster.genMonster("Sea Serpent", (275, 8307), "a sea serpent")
sea_serpent.setHealth(1750)
sea_serpent.bloodType(color="blood")
sea_serpent.setDefense(armor=25, fire=0.7, earth=1, energy=1.05, ice=0, holy=1, death=0.9, physical=1.1, drown=0)
sea_serpent.setExperience(2300)
sea_serpent.setSpeed(300)
sea_serpent.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=300)
sea_serpent.walkAround(energy=0, fire=0, poison=0)
sea_serpent.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
sea_serpent.voices("CHHHRRRR", "HISSSS")