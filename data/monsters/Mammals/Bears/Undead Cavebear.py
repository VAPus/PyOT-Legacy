undead_cavebear = game.monster.genMonster(_("Undead Cavebear"), (384, 5995), _("an undead cavebear"))#unknown corpse
undead_cavebear.setHealth(450)
undead_cavebear.bloodType(color="undead")
undead_cavebear.setDefense(armor=2, fire=1, earth=0, energy=1, ice=1, holy=1.01, death=0, physical=1, drown=1)
undead_cavebear.setExperience(600)
undead_cavebear.setSpeed(100)#unknown speed
undead_cavebear.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
undead_cavebear.walkAround(energy=0, fire=0, poison=0)
undead_cavebear.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=0)
undead_cavebear.voices("Grrrrrrrrrrr")
undead_cavebear.regMelee(150) #not accurate