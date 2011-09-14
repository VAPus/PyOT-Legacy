import game.monster

Barbarian_Bloodwalker = game.monster.genMonster("Barbarian Bloodwalker", (255, 6080), "a Barbarian Bloodwalker")
Barbarian_Bloodwalker.setOutfit(114,132,132,132)
Barbarian_Bloodwalker.setTargetChance(10)
Barbarian_Bloodwalker.bloodType("blood")
Barbarian_Bloodwalker.setHealth(305)
Barbarian_Bloodwalker.setExperience(195)
Barbarian_Bloodwalker.setSpeed(236) # correct
Barbarian_Bloodwalker.walkAround(1,1,1) # energy, fire, poison
Barbarian_Bloodwalker.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=590, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Barbarian_Bloodwalker.voices("YAAAHEEE!", "SLAUGHTER!", "CARNAGE!", "You can run but you can't hide")
Barbarian_Bloodwalker.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Barbarian_Bloodwalker.setDefense(9, fire=1.0, earth=1.05, energy=0.9, ice=0.5, holy=0.8, death=1.1, physical=0.9, drown=1.0)