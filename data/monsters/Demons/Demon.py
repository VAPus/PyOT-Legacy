demon = game.monster.genMonster("Demon", (35, 5995), "a demon")
demon.setHealth(8200)
demon.bloodType(color="blood")
demon.setDefense(armor=48, fire=0, earth=0.6, energy=0.5, ice=1.12, holy=1.12, death=0.8, physical=0.75, drown=1)
demon.setExperience(6000)
demon.setSpeed(280)
demon.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
demon.walkAround(energy=0, fire=0, poison=0)
demon.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
demon.summon("fire elemental", 10)
demon.maxSummons(2)
demon.voices("Your soul will be mine!", "CHAMEK ATH UTHUL ARAK!", "I SMELL FEEEEAAAAAR!", "Your resistance is futile!", "MUHAHAHA")
demon.regMelee(520)
demon.regSelfSpell("Haste", 360, 360, length=20) # SpellName, minimum, maximum. You also have optional parameters for interval (default 2s) and chance (default 10%)
demon.regSelfSpell("Light Healing", 120, 280)

# Spells below need to be coded/scripted first.
# Currently we also lake a function to register rune attacks to monsters
#demon.regTargetSpell("Manadrain", 0, 120, range=7)
#demon.regTargetSpell("Energy Strike", 210, 300)
#demon.regTargetSpell("Great Energy Beam", 300, 460)
#demon.regTargetSpell("Ultimate Explosion", 150, 250, range=7)

# Invert haste :p
demon.regTargetSpell("Haste", -220, -220, length=5)

# Drain without effect
#spell.creatureTargetSpell("Demon Drain", None, spell.drainManaTarget())
#demon.regTargetSpell("Demon Drain", 0, -120)

demon.loot( (2148, 100, 200), ("platinum coin", 70.25), ("fire axe", 4.0), ("fire mushroom", 69.75, 6), ("double axe", 19.5), ("gold ring", 1.25), ("great mana potion", 30.0, 3), ("platinum amulet", 0.75), ("small emerald", 10.25), ("orb", 3.0), ("assassin star", 15.25, 5), ("talon", 3.25), ("golden sickle", 1.5), ("stealth ring", 1.5), ("ultimate health potion", 40.0, 3), ("ice rapier", 0.5), ("giant sword", 1.75), ("demon shield", 0.75), ("devil helmet", 1.25), ("ring of healing", 0.5), ("demon horn", 0.5), ("mastermind shield", 0.5), ("purple tome", 1.25), ("golden legs", 0.5), ("might ring", 0.25), ("demonrage sword", 0.0025), ("magic plate armor", 0.0025), (7393, 0.0025) )
