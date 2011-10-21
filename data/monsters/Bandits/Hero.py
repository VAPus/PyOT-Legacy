Hero = game.monster.genMonster("Hero", (73, 6080), "a Hero")
Hero.setTargetChance(10)
Hero.bloodType("blood")
Hero.setHealth(1400)
Hero.setExperience(1200)
Hero.setSpeed(280) # Correct
Hero.walkAround(0,1,0) # energy, fire, poison
Hero.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Hero.voices("Let's have a fight!", "I will sing a tune at your grave.", "Have you seen princess Lumelia?", "Welcome to my battleground!")
Hero.setImmunity(1,1,1) # paralyze, invisible, lifedrain
Hero.setDefense(39, fire=0.7, earth=0.5, energy=0.6, ice=0.9, holy=0.5, death=1.2, physical=0.9, drown=1.0)
Hero.regMelee(240)
Hero.loot( ('green tunic', 8.0), ('scroll of heroic deeds', 5.5), ('meat', 9.75), ('scroll', 45.25), (2148, 100, 100), ('arrow', 100, 13), ('red rose', 19.5), ('sniper arrow', 29.5, 4), ('grapes', 20.0), ('bow', 13.5), ('lyre', 1.5), ('red piece of cloth', 2.25, 3), ('wedding ring', 5.0), ('rope', 2.5), ('crown armor', 0.75), ('great health potion', 0.5), ('two handed sword', 1.5), ('scarf', 0.75), ('war hammer', 1.25), ('small notebook', 1.0), ('might ring', 1.0), ('piggy bank', 0.25), ('crown helmet', 0.5), ('crown legs', 0.5), ('crown shield', 0.25), ('fire sword', 0.5) )