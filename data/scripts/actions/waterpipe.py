# Autoconverted script for PyOT
# Untested. Please remove this message when the script is working properly!

def onUse(creature, thing, position, stackpos, **k):
    
    magicEffect(creature.position, EFFECT_POFF)
    


reg("use", 2093, onUse)
