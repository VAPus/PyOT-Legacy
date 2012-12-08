quara_constrictor = genMonster("Quara Constrictor", (46, 6065), "a quara constrictor")
quara_constrictor.setHealth(450)
quara_constrictor.bloodType("undead")
quara_constrictor.setDefense(armor=15, fire=0, earth=1.1, energy=1.25, ice=0, holy=1, death=1, physical=1, drown=0)
quara_constrictor.setExperience(250)
quara_constrictor.setSpeed(520)
quara_constrictor.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=670, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
quara_constrictor.walkAround(energy=1, fire=0, poison=1)
quara_constrictor.setImmunity(paralyze=1, invisible=0, lifedrain=0, drunk=1)
quara_constrictor.voices("Boohaa!", "Tssss!", "Gluh! Gluh!", "Gaaahhh!")
quara_constrictor.loot( (2148, 100, 100), ("fish fin", 0.5, 3), ("brass armor", 2.25), ("small amethyst", 0.25), ("longsword", 5.0), ("shrimp", 5.5), ("quara tentacle", 9.75) )

qcpberk = spell.Spell() #poison berserk
qcpberk.area(AREA_SQUARE)
qcpberk.element(ICE)
qcpberk.targetCondition(CONDITION_FREEZING, 10, 8, damage=8) #every 4 turns = 8seconds 1turn = 2s
qcpberk.effects(area=EFFECT_POISONAREA)

qcldberk = spell.Spell() #lifedrain berserk
qcldberk.area(AREA_SQUARE)
qcldberk.element(LIFEDRAIN)
qcldberk.effects(area=EFFECT_MAGIC_RED)

cre = spell.Spell() #close range electrify
cre.targetCondition(CONDITION_ENERGY, 3, 4, damage=25) #every 2 turns

qciceball = spell.Spell() #iceball gfb
qciceball.area(AREA_CIRCLE3)
qciceball.element(ICE)
qciceball.effects(area=EFFECT_GIANTICE) # http://imageshack.us/photo/my-images/88/naamloosqk.png/

quara_constrictor.regMelee(150, condition=CountdownCondition(CONDITION_POISON, 1), conditionChance=100)
quara_constrictor.regTargetSpell(qcldberk, 1, 80, check=chance(25))
quara_constrictor.regTargetSpell(qciceball, 40, 70, check=chance(25)) 
quara_constrictor.regTargetSpell(qcpberk, 1, 80, check=chance(25))
quara_constrictor.regTargetSpell(cre, 1, 1, check=chance(10)) #not suppose to damage