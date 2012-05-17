Deepling_Spellsinger = genMonster("Deepling Spellsinger", (8, 5980), "a deepling spellsinger") #need outfit and corpse
Deepling_Spellsinger.setHealth(850)
Deepling_Spellsinger.bloodType(color="blood")
Deepling_Spellsinger.setDefense(armor=1, fire=0, earth=1.1, energy=1.1, ice=0, holy=1, death=0.5, physical=1, drown=0)
Deepling_Spellsinger.setExperience(1000)
Deepling_Spellsinger.setSpeed(250) ##?
Deepling_Spellsinger.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Deepling_Spellsinger.walkAround(energy=1, fire=0, poison=1)
Deepling_Spellsinger.setImmunity(paralyze=0, invisible=1, lifedrain=1, drunk=1)
Deepling_Spellsinger.voices("Jey Obu giotja!!", "Mmmmmoooaaaaaahaaa!!")
Deepling_Spellsinger.regMelee(150)