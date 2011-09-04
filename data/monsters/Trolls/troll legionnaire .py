import game.monster

troll_legionnaire = game.monster.genMonster("Troll Legionnaire ", (53, 5998), "a troll legionnaire ")
troll_legionnaire.setHealth(210)
troll_legionnaire.bloodType(color="blood")
troll_legionnaire.setDefense(armor=10, fire=1, earth=1, energy=1, ice=1, holy=1, death=1, physical=1, drown=1)
troll_legionnaire.setExperience(140)
troll_legionnaire.setSpeed(190)
troll_legionnaire.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=4, runOnHealth=10)
troll_legionnaire.walkAround(energy=0, fire=0, poison=0)
troll_legionnaire.setImmunity(paralyze=0, invisible=1, lifedrain=0, drunk=0)
troll_legionnaire.voices("Attack!", "Graaaaar!")
troll_legionnaire.regMelee(40)