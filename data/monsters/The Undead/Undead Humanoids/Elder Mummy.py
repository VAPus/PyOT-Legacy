elder_mummy = game.monster.genMonster(_("Elder Mummy"), (65, 6004), _("a eder mummy"))
elder_mummy.setHealth(850)
elder_mummy.bloodType(color="undead")
elder_mummy.setDefense(armor=15, fire=1, earth=1, energy=1, ice=0.8, holy=1, death=1, physical=1, drown=1)#
elder_mummy.setExperience(560)
elder_mummy.setSpeed(250)#
elder_mummy.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
elder_mummy.walkAround(energy=1, fire=1, poison=0)
elder_mummy.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=0)
elder_mummy.regMelee(120)#poison 3/turn