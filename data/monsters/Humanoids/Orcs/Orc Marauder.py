
orc_marauder = game.monster.genMonster(_("Orc Marauder "), (342, 11254), _("an orc marauder "))
orc_marauder.setHealth(185, healthmax=185)
orc_marauder.bloodType(color="blood")
orc_marauder.setDefense(armor=17, fire=1, earth=1.1, energy=0.8, ice=1, holy=0.9, death=1.1, physical=1, drown=1)
orc_marauder.setExperience(215)
orc_marauder.setSpeed(390)
orc_marauder.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=490, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
orc_marauder.walkAround(energy=1, fire=1, poison=1)
orc_marauder.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=1)
orc_marauder.voices("Grrrrrr")
orc_marauder.regMelee(80)#unknown
orc_marauder.loot( ("orc tooth", 3.25), ("broken crossbow", 5.25), ("orc leather", 4.5), ("bow", 5.75), (2148, 100, 88), ("shaggy tail", 10.75), ("meat", 24.25), ("crossbow", 0.25), ("obsidian lance", 1.25), ("orcish axe", 1.0), ("silkweaver bow", 0.0025) )