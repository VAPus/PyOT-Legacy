
Werewolf = game.monster.genMonster("Werewolf", (308, 6080), "a werewolf")
Werewolf.setTargetChance(10)
Werewolf.bloodType("blood")
Werewolf.setHealth(1955)
Werewolf.setExperience(1900)
Werewolf.setSpeed(200) #incorrect
Werewolf.walkAround(0,1,0) # energy, fire, poison
Werewolf.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=195)
Werewolf.voices("BLOOD!", "HRAAAAAAAARRRRRR!")
Werewolf.setImmunity(1,1,1) # paralyze, invisible, lifedrain
Werewolf.setDefense(40, fire=1.05, earth=0.75, energy=0.85, ice=1.1, holy=1.05, death=0.45, physical=1.0, drown=1.0)
Werewolf.loot( ('epee', 1.05), ('dreaded cleaver', 0.6), ('berserk potion', 1.35), ('platinum amulet', 1.25), ('time ring', 1), ('plate legs', 1.5), ('wolf paw', 4.75, 3), ('troll green', 5.5), ('strong health potion', 5.25), ('stone skin amulet', 1.35), (9809, 7.25), ('plate shield', 9.25), ('relic sword', 0.9), ('halberd', 3.25), ('ultimate health potion', 2.5), ('mace', 3), ('gold coin', 33.25, 226), ('brown mushroom', 5.25), ('werewolf fur', 8), ('bonebreaker', 0.6) )