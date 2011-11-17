
cobra = game.monster.genMonster("Cobra", (81, 10603), "a cobra")
cobra.setHealth(65)
cobra.bloodType(color="blood")
cobra.setDefense(armor=3, fire=1.1, earth=0, energy=1, ice=1, holy=1, death=1, physical=1, drown=1)
cobra.setExperience(30)
cobra.setSpeed(170)
cobra.setBehavior(summonable=275, hostile=1, illusionable=1, convinceable=0, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
cobra.walkAround(energy=1, fire=1, poison=0)
cobra.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=1)
cobra.voices("Fsssss", "Zzzzzz")
cobra.regMelee(5) #Poisons you up to 5 hp/turn only ##melee damage is wrong
cobra.loot( ("cobra tongue", 4.75) )