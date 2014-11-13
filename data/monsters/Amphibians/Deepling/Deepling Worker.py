Deepling_Worker = genMonster("Deepling Worker", (470 , 15497), "a deepling worker")
Deepling_Worker.health(190)
Deepling_Worker.type("blood")
Deepling_Worker.defense(armor=15, fire=0, earth=1.1, energy=1.1, ice=0, holy=1, death=1, physical=1, drown=0)
Deepling_Worker.experience(130)
Deepling_Worker.speed(200) #?
Deepling_Worker.behavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Deepling_Worker.walkAround(energy=0, fire=0, poison=0) ##
Deepling_Worker.immunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
Deepling_Worker.voices("Qjell afar gou jey!")

Deepling_Worker.regMelee(80) #
#shots spears too