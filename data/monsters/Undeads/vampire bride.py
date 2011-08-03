import game.monster

vampire_bride = game.monster.genMonster("Vampire Bride", (312, 9660), "a vampire bride")
vampire_bride.setHealth(1200)
vampire_bride.bloodType(color="blood")
vampire_bride.setDefense(23, armor=60, fire=1.1, earth=0.8, energy=0.9, ice=0.8, holy=1.1, death=0, physical=1, drown=0.9)
vampire_bride.setExperience(1050)
vampire_bride.setSpeed(180)
vampire_bride.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
vampire_bride.walkAround(energy=1, fire=1, poison=1)
vampire_bride.setImmunity(paralyze=0, invisible=1, lifedrain=0, drunk=1)
vampire_bride.voices("Kneel before your Mistress!", "Dead is the new alive.", "Come, let me kiss you, darling. Oh wait, I meant kill.", "Enjoy the pain - I know you love it.", "Are you suffering nicely enough?")