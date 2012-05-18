overcharged_energy_element = genMonster("Overcharged Energy Elemental", (290, 8966), "a overcharged energy elemental")
overcharged_energy_element.setHealth(1750)
overcharged_energy_element.bloodType(color="undead")
overcharged_energy_element.setDefense(armor=37, fire=0, earth=1.2, energy=0, ice=0, holy=0, death=0.8, physical=0.9, drown=1)
overcharged_energy_element.setExperience(1300)
overcharged_energy_element.setSpeed(300)
overcharged_energy_element.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
overcharged_energy_element.walkAround(energy=0, fire=0, poison=1)
overcharged_energy_element.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
overcharged_energy_element.regMelee(100)
overcharged_energy_element.loot( (2148, 100, 175), ("energy soil", 16.5), ("ring of healing", 0.75), ("great health potion", 9.0), ("berserk potion", 0.75), ("small amethyst", 7.25, 2), ("wand of starstorm", 0.25) )