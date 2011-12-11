brimstone_bug = game.monster.genMonster("Brimstone Bug", (352, 12527), "a brimstone bug")
brimstone_bug.bloodType("slime")
brimstone_bug.setHealth(1300)
brimstone_bug.setExperience(900)
brimstone_bug.setTargetChance(10)
brimstone_bug.setSpeed(200) #incorrect
brimstone_bug.walkAround(0,1,0) # energy, fire, poison
brimstone_bug.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
brimstone_bug.voices("Chrrr!")
brimstone_bug.setImmunity(0,0,0) # paralyze, invisible, lifedrain
brimstone_bug.setDefense(38, fire=1.1, earth=0, energy=1.1, ice=1.1, holy=1.1, death=0, physical=1.05, drown=1.0)
brimstone_bug.loot( ("stealth ring", 1.0), ("strong health potion", 9.0), ("sulphurous stone", 14.75), (12658, 6.25), ("strong mana potion", 8.75), ("brimstone shell", 9.75), ("magic sulphur", 1.75), ("lump of earth", 19.75), ("small emerald", 6.0, 4), ("poisonous slime", 50.75), (2148, 100, 197), ("platinum amulet", 0.25) )
brimstone_bug.regMelee(150) # also poisons


#brimstone_bug.regTargetSpell("Wrath of Nature", 180, 270)