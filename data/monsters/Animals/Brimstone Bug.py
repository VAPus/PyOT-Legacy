brimstone_bug = game.monster.genMonster("brimstone bug", (352, 12527), "a brimstone bug")
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
brimstone_bug.loot( ('brimstone fang', 6.5), ('brimstone shell', 8.75), ('lump of earth', 18.25), ('poisonous slime', 45), ('sulphurous stone', 13), ('strong health potion', 8.75), ('strong mana potion', 8.5), ('gold coin', 35, 197), ('magic sulphur', 2), ('stealth ring', 1.5), ('small emerald', 1.3, 4), ('platinum amulet', 0.75)  )