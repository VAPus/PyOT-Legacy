
mySpell = spell.regSpell2("Phoenix", "pho", icon=30, target=TARGET_AREA)
mySpell.area(AREA_CIRCLE2)
mySpell.effects(caster=EFFECT_YALAHARIGHOST, area=EFFECT_FIREAREA)
mySpell.requireGreater(level=10, mana=50)
mySpell.targetEffect(health=-1000) # Static effect :p

