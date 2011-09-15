
Parrot = game.monster.genMonster("Parrot", (217, 6056), "a parrot")
Parrot.setTargetChance(0)
Parrot.bloodType("blood")
Parrot.setHealth(25)
Parrot.setExperience(0)
Parrot.setSpeed(320) #corect
Parrot.walkAround(1,1,1) # energy, fire, poison
Parrot.setBehavior(summonable=250, hostile=0, illusionable=1, convinceable=250, pushable=0, pushItems=0, pushCreatures=0, targetDistance=0, runOnHealth=25)
Parrot.voices("You advanshed, you advanshed!", "Neeewbiiieee!", "Screeech!", "Hunterrr ish PK!", "BR? PL? SWE?", "Hope you die and loooosh it!", "You powerrrrrrabuserrrrr!", "You are corrrrupt! Corrrrupt!", "Tarrrrp?", "Blesshhh my stake! Screeech!", "Leeave orrr hunted!!", "Shhtop whining! Rraaah!", "I'm heeerrre! Screeeech!")
Parrot.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Parrot.setDefense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
