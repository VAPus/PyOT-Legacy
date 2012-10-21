death_priest = genMonster("Death Priest", (99, 6028), "a death_priest")#unknown corpse might be ash
death_priest.setHealth(800)
death_priest.bloodType(color="undead")
death_priest.setDefense(armor=42, fire=1, earth=1, energy=1, ice=1, holy=1, death=1, physical=1, drown=1)
death_priest.setExperience(750)
death_priest.setSpeed(320)
death_priest.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
death_priest.walkAround(energy=0, fire=1, poison=0)
death_priest.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
death_priest.regMelee(200)#unknown?
death_priest.loot( (2148, 100, 143), ("white pearl", 3.25), ("health potion", 13.5), ("hieroglyph banner", 24.0), ("scarab coin", 22.0, 3), ("orichalcum pearl", 11.5, 4), ("mana potion", 16.0), ("spellbook", 3.25), ("ring of healing", 1.5) )