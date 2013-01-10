conjure = spell.Spell("Practise Magic Missile", "adori dis min vis", group=ATTACK_GROUP)
conjure.require(mana=5, level=1, maglevel=0, learned=0)
conjure.use()
conjure.cooldowns(0, 2)
conjure.targetEffect()

# Incomplete! Target rune.
rune = spell.Rune()#TODO
rune.cooldowns(0, 2)
rune.require(mana=0, level=27, maglevel=0)
rune.targetEffect() # TODO
rune.effects(area=EFFECT_HITBYFIRE, shoot=ANIMATION_FIRE)