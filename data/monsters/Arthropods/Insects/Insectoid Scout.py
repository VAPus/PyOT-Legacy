#mostly unknown
insectoid_scout = game.monster.genMonster(_("Insectoid Scout"), (403, 5980), _("an insectoid scout"))
insectoid_scout.setHealth(230)
insectoid_scout.bloodType(color="slime")
insectoid_scout.setDefense(armor=18, fire=1, earth=1, energy=1, ice=1, holy=1, death=1, physical=1, drown=1)
insectoid_scout.setExperience(150)
insectoid_scout.setSpeed(250)
insectoid_scout.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
insectoid_scout.walkAround(energy=0, fire=0, poison=0)
insectoid_scout.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
insectoid_scout.voices("Klk! Klk!", "Chrrr! Chrrr!")#wrong?
insectoid_scout.regMelee(63)#poison 2/3 turn