import game.monster

medusa = game.monster.genMonster("Medusa", (330, 10524), "a medusa")
medusa.setHealth(4500)
medusa.bloodType(color="blood")
medusa.setDefense(armor=25, fire=1.1, earth=0, energy=1.1, ice=0.8, holy=1, death=1, physical=1, drown=0)
medusa.setExperience(4050)
medusa.setSpeed(240)
medusa.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=500)
medusa.walkAround(energy=0, fire=0, poison=0)
medusa.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
medusa.voices("You will make sssuch a fine ssstatue!", "There isss no chhhanccce of essscape", "Are you tired or why are you moving thhat ssslow <chuckle>", "Jussst look at me!")
medusa.regMelee(450)  #poisons you 42 hp at start per turn