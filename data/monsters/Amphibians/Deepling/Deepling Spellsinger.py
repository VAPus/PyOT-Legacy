Deepling_Spellsinger = genMonster("Deepling Spellsinger", (443, 15209), "a deepling spellsinger")
Deepling_Spellsinger.health(850)
Deepling_Spellsinger.type("blood")
Deepling_Spellsinger.defense(armor=1, fire=0, earth=1.1, energy=1.1, ice=0, holy=1, death=0.5, physical=1, drown=0)
Deepling_Spellsinger.experience(1000)
Deepling_Spellsinger.speed(250) ##?
Deepling_Spellsinger.behavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Deepling_Spellsinger.walkAround(energy=1, fire=0, poison=1)
Deepling_Spellsinger.immunity(paralyze=0, invisible=1, lifedrain=1, drunk=1)
Deepling_Spellsinger.voices("Jey Obu giotja!!", "Mmmmmoooaaaaaahaaa!!")

Deepling_Spellsinger.regMelee(150)