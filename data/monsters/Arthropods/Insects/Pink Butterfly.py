butterfly = game.monster.genMonster(_("Butterfly"), (213, 4993), _("a butterfly"))
butterfly.setHealth(2)
butterfly.bloodType(color="slime")
butterfly.setDefense(armor=2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1)
butterfly.setSpeed(300)
butterfly.setBehavior(summonable=0, hostile=0, illusionable=1, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
butterfly.walkAround(energy=1, fire=1, poison=1)
#note 4313 is an old used butterfly corpse sprite or second stage of decay?