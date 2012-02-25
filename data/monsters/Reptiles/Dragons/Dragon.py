dragon = game.monster.genMonster("Dragon", (34, 5973), "a dragon")
dragon.setHealth(1000)
dragon.bloodType(color="blood")
dragon.setDefense(armor=22, fire=0, earth=0.2, energy=0.8, ice=1.1, holy=1, death=1, physical=1, drown=1)
dragon.setExperience(700)
dragon.setSpeed(180)
dragon.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=300)
dragon.walkAround(energy=0, fire=0, poison=0)
dragon.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
dragon.voices("GROOAAARRR", "FCHHHHH")
dragon.loot( ("steel shield", 14.75), (12413, 9.75), ("dragon ham", 65.0, 3), ("plate legs", 2.0), (2148, 100, 105), ("strong health potion", 1.0), ("longsword", 4.25), ("steel helmet", 3.25), ("crossbow", 10.0), ("burst arrow", 42.75, 10), ("dragonbone staff", 0.0025), ("green dragon scale", 1.25), ("dragon hammer", 0.5), ("green dragon leather", 1.0), ("broadsword", 2.0), ("serpent sword", 0.5), ("wand of inferno", 1.0), ("double axe", 1.0), ("small diamond", 0.5), ("dragon shield", 0.25), ("life crystal", 0.0025) )
 
#declare spell before regestering them to the creature
dfwave = spell.Spell("drag fwave", target=TARGET_AREA)
dfwave.area(AREA_WAVE8)
dfwave.element(FIRE)
dfwave.effects(area=EFFECT_HITBYFIRE)
 
dragon.regMelee(120)
#arguements are (self, spellName, min, max, interval=2, check=chance(10), range=7, length=None)
#im not sure if we are ever going to need length
dragon.regTargetSpell("drag fwave", 100, 170, check=chance(100))
dragon.regSelfSpell("Light Healing", 25, 55, check=chance(100))
dragon.regTargetSpell(2304, 60, 110, check=chance(100)) #runes go by rune id and use regTargetSpell too. range isnt needed default is 7