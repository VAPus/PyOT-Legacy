elder_mummy = genMonster("Elder Mummy", (65, 6004), "a eder mummy")
elder_mummy.health(850)
elder_mummy.type("undead")
elder_mummy.defense(armor=15, fire=1, earth=1, energy=1, ice=0.8, holy=1, death=1, physical=1, drown=1)#
elder_mummy.experience(560)
elder_mummy.speed(250)#
elder_mummy.behavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
elder_mummy.walkAround(energy=1, fire=1, poison=0)
elder_mummy.immunity(paralyze=1, invisible=1, lifedrain=1, drunk=0)
elder_mummy.regMelee(120, condition=CountdownCondition(CONDITION_POISON, 3), conditionChance=100)