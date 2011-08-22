<-- Black Knight -->
Black_Knight = game.monster.genMonster("Black Knight", (131, 6080), "a Black Knight")
Black_knight.setOutfit(95, 95, 95, 95)
Black_knight.setAddons(3)
Black_Knight.setTargetChance(10)
Black_Knight.bloodType("blood")
Black_Knight.setHealth(1800)
Black_Knight.setExperience(1600)
Black_Knight.setSpeed(200) # Incorrect
Black_Knight.walkAround(0,0,0) # energy, fire, poison
Black_Knight.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Black_Knight.voices("No prisoners!", "By Bolg's blood", "You're no match for me!", "NO MERCY!", "MINE!")
Black_Knight.setImmunity(1,1,1) # paralyze, invisible, lifedrain
Black_Knight.setDefense(100, fire=0.05, earth=0, energy=0.2, ice=0, holy=1.1, death=0.8, physical=0.8, drown=1.0)