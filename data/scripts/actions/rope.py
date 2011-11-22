ropeSpots = 384, 418, 8278, 8592
openHoles = 294, 383, 392, 469, 470, 482, 484, 485, 489, 7933, 7938, 8249, 8250, 8251, 8252, 8253, 8254, 8255, 8256, 8323, 8380, 8567, 8585, 8972
openTraps = 462, 9625
ladders = 369, 370, 408, 409, 427, 428, 430, 924, 3135, 3136, 5545, 5763, 8170, 8276, 8277, 8279, 8280, 8281, 8284, 8285, 8286, 8595, 8596, 9606
ropes = 2120, 7731

def onUse(creature, position, onThing, onPosition, **k):
    if onPosition[0] == 0xFFFF:
        creature.notPossible()
        return

    newPos = onPosition[:]
    if onThing in ropeSpots:
        newPos[1] += 1
        newPos[2] -= 1
        creature.teleport(newPos)
    elif onThing in openedHoles or onThing in openTraps or onThing in ladders:
        newPos[2] += 1
        newPos[1] += 1
        downThing = getTile(newPos).getThing(0)
        if downThing:
            creature.teleport(newPos)
        else:
            creature.notPossible()

reg("useWith", ropes, onUse)
    