import game.monster
#mostly unknown
energized_raging_mage = game.monster.genMonster("Raging Mage", (35, 5995), "the raging mage") #unknown looktype or corpse
#energized_raging_mage.setOutfit(69, 66, 69, 66)
energized_raging_mage.setHealth(4000)
energized_raging_mage.bloodType(color="blood")
energized_raging_mage.setDefense(armor=20, fire=1, earth=1, energy=0, ice=1, holy=1, death=1, physical=1, drown=1)
energized_raging_mage.setExperience(0)
energized_raging_mage.setSpeed(200)
energized_raging_mage.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=800)
energized_raging_mage.walkAround(energy=0, fire=0, poison=0)
energized_raging_mage.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
energized_raging_mage.voices("Behold the all permeating powers I draw from this gate!!", "ENERGY!!", "I FEEL, I FEEEEEL... OMNIPOTENCE!!", "MWAAAHAHAAA!! NO ONE!! NO ONE CAN DEFEAT MEEE!!!")