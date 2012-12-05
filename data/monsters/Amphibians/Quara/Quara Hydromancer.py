quara_hydromancer = genMonster("Quara Hydromancer", (47, 6066), "a quara hydromancer")
quara_hydromancer.setHealth(1100)
quara_hydromancer.bloodType("blood")
quara_hydromancer.setDefense(armor=33, fire=0, earth=1.1, energy=1.25, ice=0, holy=1, death=1, physical=1, drown=0)
quara_hydromancer.setExperience(800)
quara_hydromancer.setSpeed(520)
quara_hydromancer.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=30)
quara_hydromancer.walkAround(energy=1, fire=0, poison=1)
quara_hydromancer.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
quara_hydromancer.voices("Qua hah tsh!", "Teech tsha tshul!", "Quara tsha Fach!", "Tssssha Quara!", "Blubber.", "Blup.")
quara_hydromancer.loot( (2148, 100, 90), ("white pearl", 1.75), ("black pearl", 2.0), ("small emerald", 1.5, 2), ("quara eye", 10.25), ("shrimp", 5.0), ("knight armor", 0.25), ("fish fin", 1.0, 3), ("wand of cosmic energy", 1.0), ("ring of healing", 0.5), ("great mana potion", 1.0) )

#Missing - Paralyze (on target?)

qhld = spell.Spell() #lifedrain
qhld.element(PHYSICAL) #life drain
qhld.effects(area=EFFECT_MAGIC_GREEN) #effect?

qhldb = spell.Spell(target=TARGET_AREA) #lifedrain beam
qhldb.area(AREA_BEAM7) #7 or 4?
qhldb.element(PHYSICAL) #life drain
qhldb.effects(area=EFFECT_MAGIC_GREEN)

qhbberserk = spell.Spell() #bubble berserk
qhbberserk.area(AREA_SQUARE)
qhbberserk.element(ICE)
qhbberserk.effects(area=EFFECT_BUBBLES)

qhib = spell.Spell(target=TARGET_AREA) #ice beam
qhib.area(AREA_BEAM7) #7 or 4?
qhib.element(ICE) #life drain
qhib.effects(area=EFFECT_BUBBLES)

quara_hydromancer.regMelee(80) #poisons you for up to 5 hp/turn
quara_hydromancer.regSelfSpell("Light Healing", 25, 55, check=chance(20)) #strength?
quara_hydromancer.regTargetSpell(qhldb, 170, 240, check=chance(20))
quara_hydromancer.regTargetSpell(qhib, 100, 180, check=chance(20))
quara_hydromancer.regTargetSpell(qhld, 1, 170, check=chance(20))
quara_hydromancer.regTargetSpell(qhbberserk, 90, 150, check=chance(20))