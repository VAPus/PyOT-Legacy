instant = spell.Spell("Whirlwind Throw", "exori hur", icon=107, group=ATTACK_GROUP)
instant.require(mana=40, level=28, maglevel=0, learned=0, vocations=(4, 8))
instant.cooldowns(6, 2)
instant.targetEffect(callback=spell.damage(1, 2, 1, 6, PHYSICAL)) # TODO unknown values (X, X, 1, 6)
#formula needs to be based off of skills not magic level.
#instant.effects(shoot=ANIMATION_WEAPONTYPE)
