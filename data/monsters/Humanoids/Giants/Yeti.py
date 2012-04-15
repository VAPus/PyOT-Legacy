Yeti = game.monster.genMonster(_("Yeti"), (8, 5980), _("a yeti")) ##looktype and corpse
Yeti.setHealth(950)
Yeti.bloodType(color="blood")
Yeti.setDefense(armor=1, fire=1, earth=1, energy=1, ice=1, holy=1, death=1, physical=1, drown=1)
Yeti.setExperience(460)
Yeti.setSpeed(300) #incorrect
Yeti.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Yeti.walkAround(energy=0, fire=0, poison=0)
Yeti.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
Yeti.voices("Yooodelaaahooohooo")
Yeti.regMelee(200)
Yeti.regDistance(80, ANIMATION_SNOWBALL, chance(21))