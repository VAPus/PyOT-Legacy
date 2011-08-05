import game.monster

betrayed_wraith = game.monster.genMonster("Betrayed Wraith", (233, 6316), "a betrayed wraith")
betrayed_wraith.setHealth(4200)
betrayed_wraith.bloodType(color="blood")
betrayed_wraith.setDefense(armor=15, fire=0, earth=0, energy=0, ice=0.5, holy=1.2, death=0, physical=1, drown=1)
betrayed_wraith.setExperience(3500)
betrayed_wraith.setSpeed(310)
betrayed_wraith.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=250)
betrayed_wraith.walkAround(energy=0, fire=0, poison=0)
betrayed_wraith.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
betrayed_wraith.voices("Rrrah!", "Gnarr!", "Tcharrr!")