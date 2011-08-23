import game.monster

orc_warrior = game.monster.genMonster("Orc Warrior", (7, 5979), "an orc warrior")
orc_warrior.setHealth(125)
orc_warrior.bloodType(color="blood")
orc_warrior.setDefense(armor=8, fire=1, earth=1.1, energy=0.7, ice=1, holy=0.9, death=1.1, physical=1, drown=1)
orc_warrior.setExperience(50)
orc_warrior.setSpeed(190)
orc_warrior.setBehavior(summonable=360, attackable=1, hostile=1, illusionable=1, convinceable=360, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=11)
orc_warrior.walkAround(energy=1, fire=1, poison=1)
orc_warrior.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)
orc_warrior.voices("Alk!", "Trak grrrr brik.", "Grow truk grrrr.")