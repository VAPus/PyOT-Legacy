import game.monster

souleater = game.monster.genMonster("Souleater", (355, 12631), "a souleater")
souleater.setHealth(1100)
souleater.bloodType(color="undead")
souleater.setDefense(armor=25, fire=1.1, earth=1, energy=1.1, ice=0.5, holy=1.1, death=0, physical=0.7, drown=1)
souleater.setExperience(1300)
souleater.setSpeed(250)
souleater.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
souleater.walkAround(energy=1, fire=1, poison=1)
souleater.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=1)
souleater.voices("Life is such a fickle thing!", "I will devour your soul.", "Souuuls!", "I will feed on you.", "Aaaahh")