dwarf_henchman = genMonster("Dwarf Henchman", (160, 5980), "a dwarf henchman")
dwarf_henchman.setOutfit(66, 50, 20, 20)
dwarf_henchman.health(350)
dwarf_henchman.type("blood")
dwarf_henchman.defense(armor=17, fire=1, earth=1, energy=1, ice=1, holy=1, death=1, physical=1, drown=1)#
dwarf_henchman.experience(15)
dwarf_henchman.speed(220)#
dwarf_henchman.behavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
dwarf_henchman.walkAround(energy=1, fire=1, poison=1)
dwarf_henchman.immunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
dwarf_henchman.voices("This place is for our eyes only!", "We will live and let you die!", "I will die another day!", "We have license to kill!")
dwarf_henchman.regMelee(50)