import game.monster

cobra = game.monster.genMonster("Cobra", (81, 10603), "a cobra")
cobra.setHealth(65)
cobra.bloodType(color="blood")
cobra.setDefense(armor=10, fire=1.1, earth=0, energy=1, ice=1, holy=1, death=1, physical=1, drown=1)
cobra.setExperience(30)
cobra.setSpeed(170)
cobra.setBehavior(summonable=275, attackable=1, hostile=1, illusionable=1, convinceable=275, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
cobra.walkAround(energy=1, fire=1, poison=0)
cobra.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=1)
cobra.voices("Fsssss", "Zzzzzz")