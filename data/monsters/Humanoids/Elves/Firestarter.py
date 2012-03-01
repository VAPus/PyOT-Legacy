#mostly unknown
Firestarter = game.monster.genMonster("Firestarter", (159, 5980), "a firestarter")
Firestarter.setOutfit(95, 95, 95, 95)#wrong colors
Firestarter.setHealth(180)
Firestarter.bloodType(color="blood")
Firestarter.setDefense(armor=15, fire=1, earth=1, energy=1, ice=1, holy=1, death=1, physical=1, drown=1)
Firestarter.setExperience(80)
Firestarter.setSpeed(250)
Firestarter.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Firestarter.walkAround(energy=0, fire=0, poison=0)
Firestarter.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=0)
Firestarter.voices("FIRE!","BURN!", "DEATH to the FALSE GOD!!", "You shall burn in the thornfires!!","DOWN with the followers of the bog!!")
Firestarter.regMelee(7)
Firestarter.loot( (2148, 100, 35), ("elvish talisman", 6.0), ("flaming arrow", 100, 12), ("coal", 15.0), ("grapes", 20.5), ("longsword", 6.25), ("bow", 4.25), ("flintstone", 0.5), (5921, 1.0), ("elvish bow", 0.0025) )