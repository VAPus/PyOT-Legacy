Deepling_Scout = game.monster.genMonster(_("Deepling Scout"), (8, 5980), _("a deepling scout")) #need outfit and corpse
Deepling_Scout.setHealth(240, healthmax=240)
Deepling_Scout.bloodType(color="blood")
Deepling_Scout.setDefense(armor=1, fire=0, earth=1.2, energy=1.2, ice=0, holy=1, death=1.2, physical=1.2, drown=0)
Deepling_Scout.setExperience(160)
Deepling_Scout.setSpeed(250) #unknown
Deepling_Scout.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Deepling_Scout.walkAround(energy=0, fire=0, poison=0) ##?
Deepling_Scout.setImmunity(paralyze=0, invisible=0, lifedrain=1, drunk=1)
Deepling_Scout.voices("Njaaarh!!", "Begjone, intrjuder!!", "Djon't djare stjare injo the eyes of the djeep!", "Ljeave this sjacred pljace while you cjan")
Deepling_Scout.regMelee(100)