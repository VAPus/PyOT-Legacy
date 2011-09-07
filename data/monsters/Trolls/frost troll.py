import game.monster

frost_troll = game.monster.genMonster("Frost Troll", (53, 5998), "a frost troll")
frost_troll.setHealth(55)
frost_troll.bloodType(color="blood")
frost_troll.setDefense(armor=7, fire=0.6, earth=1.1, energy=1.15, ice=1, holy=0.9, death=1.1, physical=1, drown=1)
frost_troll.setExperience(23)
frost_troll.setSpeed(190)
frost_troll.setBehavior(summonable=300, hostile=1, illusionable=1, convinceable=300, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=10)
frost_troll.walkAround(energy=1, fire=1, poison=1)
frost_troll.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)
frost_troll.voices("Brrr", "Broar!")
frost_troll.regMelee(20)