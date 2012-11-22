ghoulish_hyaena = genMonster("Ghoulish Hyaena", (94, 6026), "a ghoulish hyaena")
ghoulish_hyaena.setHealth(400)
ghoulish_hyaena.bloodType("blood")
ghoulish_hyaena.setDefense(armor=22, fire=1, earth=0.3, energy=1, ice=1, holy=1, death=0, physical=1, drown=1)
ghoulish_hyaena.setExperience(195)
ghoulish_hyaena.setSpeed(240)#unknown speed
ghoulish_hyaena.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=30)
ghoulish_hyaena.walkAround(energy=0, fire=0, poison=0)
ghoulish_hyaena.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)
ghoulish_hyaena.voices("Grawrrr!!", "Hoouu!")
ghoulish_hyaena.regMelee(170)#incorrect
ghoulish_hyaena.loot( (2148, 100, 40), ("health potion", 19.0), ("meat", 47.75), (3976, 100, 7), ("small ruby", 5.75, 2) )