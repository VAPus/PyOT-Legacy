#mostly unknown
#always around not really a boss
energized_raging_mage = game.monster.genMonster(_("Energized Raging Mage"), (423, 5995), _("the energized raging mage")) #unknown corpse
energized_raging_mage.setHealth(4000)
energized_raging_mage.bloodType(color="blood")
energized_raging_mage.setDefense(armor=30, fire=1, earth=1, energy=0, ice=1, holy=1, death=1, physical=1, drown=1)
energized_raging_mage.setExperience(0)
energized_raging_mage.setSpeed(200)
energized_raging_mage.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=800)
energized_raging_mage.walkAround(energy=0, fire=0, poison=0)
energized_raging_mage.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
energized_raging_mage.voices("Behold the all permeating powers I draw from this gate!!", "ENERGY!!", "I FEEL, I FEEEEEL... OMNIPOTENCE!!", "MWAAAHAHAAA!! NO ONE!! NO ONE CAN DEFEAT MEEE!!!")
energized_raging_mage.summon("Golden Servant", 10)
energized_raging_mage.maxSummons(1)