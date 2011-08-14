import game.monster

young_sea_serpent = game.monster.genMonster("Young Sea Serpent", (317, 8307), "a young sea serpent")
young_sea_serpent.setHealth(1050)
young_sea_serpent.bloodType(color="blood")
young_sea_serpent.setDefense(armor=20, fire=0.7, earth=0, energy=1.1, ice=0, holy=1, death=1.15, physical=1.2, drown=0)
young_sea_serpent.setExperience(1000)
young_sea_serpent.setSpeed(350)
young_sea_serpent.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=300)
young_sea_serpent.walkAround(energy=0, fire=0, poison=0)
young_sea_serpent.setImmunity(paralyze=1, invisible=0, lifedrain=1, drunk=1)
young_sea_serpent.voices("HISSSS", "CHHHRRRR")