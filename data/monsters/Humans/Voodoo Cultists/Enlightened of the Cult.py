enlightened_of_the_cult = genMonster("Enlightened of the Cult", (193, 6080), "a enlightened of the cult")
enlightened_of_the_cult.setHealth(700)
enlightened_of_the_cult.bloodType(color="blood")
enlightened_of_the_cult.setDefense(armor=47, fire=1, earth=1.05, energy=1, ice=0.8, holy=0.8, death=1.06, physical=1.05, drown=1)
enlightened_of_the_cult.setExperience(500)
enlightened_of_the_cult.setSpeed(220)
enlightened_of_the_cult.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=4, runOnHealth=0)#target dis 5?
enlightened_of_the_cult.walkAround(energy=1, fire=1, poison=1)
enlightened_of_the_cult.setImmunity(paralyze=1, invisible=0, lifedrain=0, drunk=0)
enlightened_of_the_cult.summon("Crypt Shambler", 10)
enlightened_of_the_cult.summon("Ghost", 10)
enlightened_of_the_cult.maxSummons(2)
enlightened_of_the_cult.voices("Praise to my master Urgith!", "You will rise as my servant!", "Praise to my masters! Long live the triangle!", "You will die in the name of the triangle!")
enlightened_of_the_cult.regMelee(100) #Poisons you up to 4 Hitpoints/turn