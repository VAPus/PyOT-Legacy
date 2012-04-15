Deepling_Warrior = game.monster.genMonster(_("Deepling Warrior"), (8, 5980), _("a deepling warrior")) #need outfit and corpse
Deepling_Warrior.setHealth(1600, healthmax=1600)
Deepling_Warrior.bloodType(color="blood")
Deepling_Warrior.setDefense(armor=1, fire=0, earth=1.1, energy=1.1, ice=0, holy=1, death=0.9, physical=1, drown=0)
Deepling_Warrior.setExperience(1500)
Deepling_Warrior.setSpeed(250) ##?
Deepling_Warrior.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=30)
Deepling_Warrior.walkAround(energy=1, fire=0, poison=1)
Deepling_Warrior.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
Deepling_Warrior.voices("Jou wjil ajll djie!")
Deepling_Warrior.regMelee(300)
Deepling_Warrior.regSelfSpell("Light Healing", 50, 150, check=chance(20)) #strength?
Deepling_Warrior.regTargetSpell("Whirlwind Throw", 1, 290, check=chance(21)) #goes by weapon, will it work?