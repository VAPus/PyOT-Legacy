Deepling_Worker = game.monster.genMonster(_("Deepling Worker"), (8, 5980), _("a deepling worker")) #need outfit and corpse
Deepling_Worker.setHealth(190)
Deepling_Worker.bloodType(color="blood")
Deepling_Worker.setDefense(armor=1, fire=0, earth=1.1, energy=1.1, ice=0, holy=1, death=1, physical=1, drown=0)
Deepling_Worker.setExperience(130)
Deepling_Worker.setSpeed(200) ##?
Deepling_Worker.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Deepling_Worker.walkAround(energy=0, fire=0, poison=0) ##
Deepling_Worker.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
Deepling_Worker.voices("Qjell afar gou jey!")
Deepling_Worker.regMelee(80) ##
##shots spears too