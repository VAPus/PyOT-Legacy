import game.scriptsystem # We use the talkactions from here
import game.item
import game.enum

spells = {}


def conjureRune(name, words, make, icon, mana=0, level=0, mlevel=0, soul=1, vocation=None, use=2260, useCount=1, makeCount=1, teached=0, group=3, cooldown=2):
    def conjure(creature, words):
        if not creature.canDoSpell(icon, group):
            creature.exhausted()
            return False
            
        # Checks
        if creature.data["level"] < level:
            creature.notEnough("level")
        elif creature.data["mana"] < mana:
            creature.notEnough("mana")
        elif creature.data["soul"] < soul:
            creature.notEnough("soul")
        elif creature.data["maglevel"] < mlevel:
            creature.notEnough("magic level")
        else:
            useItem = creature.findItemById(use, useCount)
            if not useItem:
                creature.needMagicItem()
                creature.magicEffect(creature.position, game.enum.EFFECT_POFF)
                
            else:
                item = game.item.Item(make,makeCount)

                creature.itemToContainer(creature.inventory[2], item)
                creature.cooldownSpell(icon, group, cooldown)
                creature.message("Made %dx%s" % (makeCount, name))
                creature.magicEffect(creature.position, game.enum.EFFECT_MAGIC_RED)

    return (name, words, conjure)
    
    
def reg(name, words, function):
    # I'm special
    if name in spells:
        print "Warning: Duplicate spell with name %s" % name
        
    spells[name] = (words, function)
    game.scriptsystem.get("talkaction").reg(words, function)