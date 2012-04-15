Gang_Member = game.monster.genMonster(_("Gang Member"), (151, 6080), _("a Gang Member"))
Gang_Member.setOutfit(114, 19, 42, 20)
Gang_Member.setTargetChance(0)
Gang_Member.bloodType("blood")
Gang_Member.setHealth(295)
Gang_Member.setExperience(70)
Gang_Member.setSpeed(190) # Correct
Gang_Member.walkAround(1,1,1) # energy, fire, poison
Gang_Member.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=450, pushable=1, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=35)
Gang_Member.voices("This is our territory!", "Help me guys!", "I don't like the way you look!", "You're wearing the wrong colours!", "Don't mess with us!")
Gang_Member.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Gang_Member.setDefense(9, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.05, physical=1.0, drown=1.0)
Gang_Member.regMelee(70)
Gang_Member.loot( (2148, 100, 30), ("leather legs", 15.5), ("brown bread", 4.25), ("mace", 9.5), ("club ring", 1.0), ("studded legs", 5.0) )