import game.monster

undead_gladiator = game.monster.genMonster("Undead Gladiator", (306, 9823), "an undead gladiator")
undead_gladiator.setHealth(1000e)
undead_gladiator.bloodType(color="undead")
undead_gladiator.setDefense(45, armor=40, fire=1, earth=1, energy=1, ice=1, holy=1, death=1, physical=1, drown=1)
undead_gladiator.setExperience(800)
undead_gladiator.setSpeed(270)
undead_gladiator.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
undead_gladiator.walkAround(energy=1, fire=0, poison=1)
undead_gladiator.setImmunity(paralyze=0, invisible=1, lifedrain=1, drunk=0)
undead_gladiator.voices("Let's battle it out in a duel!",, "Bring it!", "I'll fight here in eternity and beyond.", "I will not give up!", "Another foolish adventurer who tries to beat me.")