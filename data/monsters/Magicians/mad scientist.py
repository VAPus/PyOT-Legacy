import game.monster

mad_scientist = game.monster.genMonster("Mad Scientist", (133, 6080), "a mad scientist")
mad_scientist.setOutfit(97, 0, 38, 97) #needs 1 addon
mad_scientist.setHealth(325)
mad_scientist.bloodType(color="blood")
mad_scientist.setDefense(armor=15, fire=0.9, earth=0.8, energy=0.8, ice=0.9, holy=0.8, death=1.05, physical=1, drown=0)
mad_scientist.setExperience(205)
mad_scientist.setSpeed(220)
mad_scientist.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
mad_scientist.walkAround(energy=1, fire=1, poison=1)
mad_scientist.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
mad_scientist.voices("Die in the name of Science!", "You will regret interrupting my studies!", "Let me test this!", "I will study your corpse!")