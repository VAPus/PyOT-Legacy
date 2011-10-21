Amazon = game.monster.genMonster("Amazon", (137, 6081), "a Amazon")
Amazon.setOutfit(113, 120, 114, 132)
Amazon.setTargetChance(10)
Amazon.bloodType("blood")
Amazon.setHealth(110)
Amazon.setExperience(60)
Amazon.setSpeed(172) # correct
Amazon.walkAround(1,1,1) # energy, fire, poison
Amazon.setBehavior(summonable=390, hostile=1, illusionable=1, convinceable=390, pushable=1, pushItems=1, pushCreatures=0, targetDistance=4, runOnHealth=10)
Amazon.voices("Your head shall be mine!", "Your head will be mine!", "Yeee ha!")
Amazon.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Amazon.setDefense(11, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.05, physical=1.05, drown=1.0)
Amazon.regMelee(45)
Amazon.loot( ('sabre', 24.75), ('brown bread', 32.25), ('dagger', 81.25), ('protective charm', 5.25), ('skull', 100, 2), (2148, 100, 20), ('girlish hair decoration', 11.25), ('torch', 1.75), ('crystal necklace', 0.25) )