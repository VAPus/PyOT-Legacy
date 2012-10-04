Werewolf = genMonster("Werewolf", (308, 6080), "a werewolf")
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
Werewolf.loot( (2148, 100, 224), ("halberd", 3.0), ("brown mushroom", 7.0), ("troll green", 5.25), ("rusty armor", 7.75), ("plate shield", 11.0), ("berserk potion", 1.0), ("werewolf fur", 10.5), ("strong health potion", 5.5), ("stone skin amulet", 0.75), ("ultimate health potion", 2.25), ("platinum amulet", 1.0), ("epee", 0.75), ("time ring", 0.5), ("wolf paw", 4.5, 3), ("dreaded cleaver", 0.0025), ("relic sword", 0.5), ("bonebreaker", 0.25) )
Werewolf.regMelee(350)