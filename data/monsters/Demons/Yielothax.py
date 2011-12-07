yielothax = game.monster.genMonster("Yielothax", (408, 5980), "a yielothax")#unknown corpse
yielothax.setHealth(1500)
yielothax.bloodType(color="blood")
yielothax.setDefense(armor=20, fire=0.75, earth=0, energy=1.05, ice=1.05, holy=1, death=0.5, physical=1.1, drown=1)#
yielothax.setExperience(1250)
yielothax.setSpeed(300)#
yielothax.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
yielothax.walkAround(energy=1, fire=0, poison=0)
yielothax.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
yielothax.voices("IIEEH!! Iiih iih ih iiih!!!", "Bsssssssm Bssssssm Bsssssssssssm!")
yielothax.regMelee(200)