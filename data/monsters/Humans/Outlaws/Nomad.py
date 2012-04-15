Nomad = game.monster.genMonster(_("Nomad"), (146, 6080), _("a Nomad"))
Nomad.setOutfit(114, 20, 22, 2)
Nomad.setAddons(3)
Nomad.setTargetChance(10)
Nomad.bloodType("blood")
Nomad.setHealth(160)
Nomad.setExperience(60)
Nomad.setSpeed(190) # Correct
Nomad.walkAround(1,1,1) # energy, fire, poison
Nomad.setBehavior(summonable=420, hostile=1, illusionable=0, convinceable=420, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=25)
Nomad.voices("I will leave your remains to the vultures!", "We are the true sons of the desert!", "We are swift as the wind of the desert!", "Your riches will be mine!")
Nomad.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Nomad.setDefense(6, fire=0.8, earth=1.0, energy=1.0, ice=1.1, holy=0.8, death=1.1, physical=1.1, drown=1.0)
Nomad.regMelee(80)
Nomad.loot( (2148, 100, 39), ("axe", 18.75), ("leather legs", 8.75), ("brass shield", 10.25), ("mace", 7.5), ("brass armor", 2.25), ("chain helmet", 2.75), ("steel shield", 0.75), (8838, 8.25, 3), ("iron helmet", 0.75), ("parchment", 0.25), ("rope belt", 2.75), (12412, 1.0) )