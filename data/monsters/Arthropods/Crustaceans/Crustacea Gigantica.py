Crustacea_Gigantica = genMonster("Crustacea Gigantica", (8, 5980), "a crustacea gigantica") ##looktype corpse
Crustacea_Gigantica.setHealth(1600, healthmax=1600)
Crustacea_Gigantica.bloodType(color="blood")
Crustacea_Gigantica.setDefense(armor=1, fire=1, earth=1, energy=1, ice=0, holy=1, death=1, physical=1, drown=1)
Crustacea_Gigantica.setExperience(1800)
Crustacea_Gigantica.setSpeed(300) ##?
Crustacea_Gigantica.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Crustacea_Gigantica.walkAround(energy=0, fire=0, poison=0)
Crustacea_Gigantica.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=0)
Crustacea_Gigantica.voices("Chrchrchr", "Klonklonk", "Chrrrrr")

Crustacea_Gigantica.regMelee(160)