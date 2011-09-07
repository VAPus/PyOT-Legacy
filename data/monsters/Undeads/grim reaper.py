import game.monster

grim_reaper = game.monster.genMonster("Grim Reaper", (300, 8955), "a grim reaper")
grim_reaper.setHealth(3900)
grim_reaper.bloodType(color="undead")
grim_reaper.setDefense(armor=50, fire=1.1, earth=0.6, energy=1.1, ice=0.35, holy=1.1, death=0.2, physical=0.8, drown=1)
grim_reaper.setExperience(5500)
grim_reaper.setSpeed(400)
grim_reaper.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
grim_reaper.walkAround(energy=1, fire=1, poison=0)
grim_reaper.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=0)
grim_reaper.voices("Death!", "Come a little closer!", "The end is near!")
grim_reaper.regMelee(813)