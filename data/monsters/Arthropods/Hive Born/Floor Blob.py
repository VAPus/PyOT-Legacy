floor_blob = genMonster("Floor Blob", (459, 5980), "a floor blob")
floor_blob.setHealth(1, healthmax=1)
floor_blob.bloodType("slime")
floor_blob.setDefense(armor=10, fire=0, earth=0, energy=0, ice=0, holy=0, death=0, physical=0, drown=0)
floor_blob.setExperience(0)
floor_blob.setSpeed(200) #incorrect
floor_blob.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
floor_blob.walkAround(energy=0, fire=0, poison=0)
floor_blob.setImmunity(paralyze=0, invisible=1, lifedrain=0, drunk=0)