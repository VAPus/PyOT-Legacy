import game.monster

troll_champion = game.monster.genMonster("Troll Champion", (281, 7926), "a troll champion")
troll_champion.setHealth(75)
troll_champion.bloodType(color="blood")
troll_champion.setDefense(armor=10, fire=1, earth=1.1, energy=0.85, ice=1, holy=0.9, death=1.1, physical=1, drown=1)
troll_champion.setExperience(40)
troll_champion.setSpeed(120)
troll_champion.setBehavior(summonable=340, attackable=1, hostile=1, illusionable=1, convinceable=340, pushable=1, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=20)
troll_champion.walkAround(energy=1, fire=1, poison=1)
troll_champion.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)
troll_champion.voices("Meee maity!", "Grrrr", "Whaaaz up!?", "Gruntz!", "Groar")
troll_champion.regMelee(35)