import game.monster

wisp = game.monster.genMonster("Wisp", (294, 6324), "a wisp")
wisp.setHealth(115)
wisp.bloodType(color="undead")
wisp.setDefense(armor=15, fire=1, earth=0.1, energy=0.6, ice=1, holy=1, death=0, physical=0.4, drown=1)
wisp.setExperience(0)
wisp.setSpeed(200)
wisp.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=115)
wisp.walkAround(energy=1, fire=1, poison=1)
wisp.setImmunity(paralyze=1, invisible=0, lifedrain=0, drunk=1)
wisp.voices("Crackle!", "Tsshh")
#nomelle attack only life drain