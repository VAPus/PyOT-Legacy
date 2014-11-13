Deepling_Scout = genMonster("Deepling Scout", (413, 13839), "a deepling scout")
Deepling_Scout.health(240, healthmax=240)
Deepling_Scout.type("blood")
Deepling_Scout.defense(armor=1, fire=0, earth=1.2, energy=1.2, ice=0, holy=1, death=1.2, physical=1.2, drown=0)
Deepling_Scout.experience(160)
Deepling_Scout.speed(250) #unknown
Deepling_Scout.behavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Deepling_Scout.walkAround(energy=0, fire=0, poison=0) ##?
Deepling_Scout.immunity(paralyze=0, invisible=0, lifedrain=1, drunk=1)
Deepling_Scout.voices("Njaaarh!!", "Begjone, intrjuder!!", "Djon't djare stjare injo the eyes of the djeep!", "Ljeave this sjacred pljace while you cjan")

Deepling_Scout.regMelee(100)