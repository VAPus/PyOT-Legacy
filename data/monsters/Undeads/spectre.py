import game.monster

spectre = game.monster.genMonster("Spectre", (235, 6348), "a spectre")
spectre.setHealth(1350)
spectre.bloodType(color="undead")
spectre.setDefense(25, armor=20, fire=1.08, earth=0, energy=1.08, ice=0.99, holy=1, death=0, physical=0.1, drown=0)
spectre.setExperience(2100)
spectre.setSpeed(250)
spectre.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
spectre.walkAround(energy=0, fire=0, poison=0)
spectre.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
spectre.voices("Revenge ... is so ... sweet.", "Life...force! Feed me your... lifeforce", "Mor... tals!")