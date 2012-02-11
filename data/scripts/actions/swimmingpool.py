import game.scriptsystem
import game.enum


def stepIn(creature, position, **k):
    if creature.isPlayer() and not creature.getVar("IN_WATER"): # setVar is the local lock, it's not saved and can only be read from this script file!
        creature.magicEffect(position, game.enum.EFFECT_WATERSPLASH)
        creature.setOutfit(267)
        creature.setVar("OUTFIT", (creature.outfit, creature.addon))
        creature.setVar("IN_WATER", True)

def stepOut(creature, position, **k):
    if creature.isPlayer():
        outfit = creature.getVar("OUTFIT")
        creature.setOutfit(outfit[0][0], outfit[0][1], outfit[0][2], outfit[0][3], outfit[0][4], outfit[1])
        creature.setVar("IN_WATER") # Without a value, the var is deleted
        creature.setVar("OUTFIT")

game.scriptsystem.get("walkOn").reg(range(4620, 4625+1), stepIn)
game.scriptsystem.get("walkOff").reg(range(4620, 4625+1), stepOut)