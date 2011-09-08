import game.monster

orc_warlord = game.monster.genMonster("Orc Warlord", (2, 6008), "an orc warlord")
orc_warlord.setHealth(950, healthmax=950)
orc_warlord.bloodType(color="blood")
orc_warlord.setDefense(armor=22, fire=0.2, earth=1.1, energy=0.8, ice=1, holy=0.9, death=1.05, physical=1, drown=1)
orc_warlord.setExperience(670)
orc_warlord.setSpeed(290)
orc_warlord.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
orc_warlord.walkAround(energy=1, fire=0, poison=1)
orc_warlord.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=0)
orc_warlord.voices("Ikem rambo zambo!", "Orc buta bana!", "Ranat Ulderek!", "Fetchi Maruk Buta")
orc_warlord.regMelee(250)