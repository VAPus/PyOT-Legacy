import game.monster

crypt_shambler = game.monster.genMonster("Crypt Shambler", (100, 6029), "a crypt shambler")
crypt_shambler.setHealth(330)
crypt_shambler.bloodType(color="undead")
crypt_shambler.setDefense(armor=15, fire=1, earth=0, energy=1, ice=1, holy=1.25, death=0, physical=1, drown=0)
crypt_shambler.setExperience(195)
crypt_shambler.setSpeed(180)
crypt_shambler.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=1, convinceable=580, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
crypt_shambler.walkAround(energy=1, fire=1, poison=0)
crypt_shambler.setImmunity(paralyze=1, invisible=0, lifedrain=1, drunk=0)
crypt_shambler.voices("Aaaaahhhh!", "Hoooohhh!", "Uhhhhhhh!", "Chhhhhhh!")
crypt_shambler.regMelee(140)