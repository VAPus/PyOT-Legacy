import game.scriptsystem # We use the talkactions from here
import game.item
spells = []


def conjureRune(words, make, icon, mana=0, level=0, mlevel=0, soul=1, vocation=None, use=2260, useCount=1, makeCount=1, teached=0, group=3, cooldown=2):
    def conjure(creature, words):
        if not creature.canDoSpell(icon, group):
            creature.message("Sorry, cooling down")
            return
            
        # Checks
        if creature.data["level"] < level:
            creature.message("Your level is not high enough")
        elif creature.data["mana"] < mana:
            creature.message("Your mana is not high enough")
        elif creature.data["soul"] < soul:
            creature.message("You don't have enough soul points")
        elif creature.data["maglevel"] < mlevel:
            creature.message("Your magic level is not high enough")
        else:
            useItem = creature.findItemById(use, useCount)
            if not useItem:
                creature.message("Can't find enough reagent")
            else:
                item = game.item.Item(make,makeCount)

                creature.itemToContainer(creature.inventory[2], item)
                creature.cooldownSpell(icon, group, cooldown)
                creature.message("Made %dx%s" % (makeCount, item.name()))

    spells.append((words, conjure))
    return (words, conjure)