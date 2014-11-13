rift_scythe = genMonster("Rift Scythe", (300, 6070), "a rift scythe")#no corpse
rift_scythe.health(3600)
rift_scythe.type("undead")
rift_scythe.defense(armor=32, fire=1.1, earth=0.6, energy=1.1, ice=0.35, holy=1.1, death=0.2, physical=1.05, drown=1)
rift_scythe.experience(2000)
rift_scythe.speed(370)
rift_scythe.behavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
rift_scythe.walkAround(energy=1, fire=1, poison=1)
rift_scythe.immunity(paralyze=1, invisible=1, lifedrain=0, drunk=0)
rift_scythe.regMelee(200)#wrong