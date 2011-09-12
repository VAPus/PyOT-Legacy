from game.scriptsystem import reg
from game.engine import transformItem, relocate

openHorizontal = 1214, 1222, 1226, 1230, 1236, 1240, 1244, 1248, 1254, 1258, 1262, 1542, 1637, 1641, 3537, 3539, 3541, 3543, 4918, 5085, 5100,\
                5102, 5104, 5106, 5118, 5120, 5122, 5124, 5136, 5139, 5280, 5287, 5291, 5295, 5518, 5734, 5746, 6197, 6201, 6205, 6209, 6254,\
                6258, 6262, 6266, 6796, 6800, 6893, 6895, 6897, 6899, 7035, 7037, 7039, 7041, 7057, 8546, 8550, 8554, 8558, 9170, 9174, 9178,\
                9182, 9272, 9276, 9280, 9284, 10273, 10277, 10281, 10285, 10479, 10481, 10483

openVertical = 1211, 1220, 1224, 1228, 1233, 1238, 1242, 1246, 1251, 1256, 1260, 1540, 1635, 1639, 3546, 3548, 3552, 4915, 5083, 5109, 5111, 5113, 5115,\
                5127, 5129, 5131, 5133, 5142, 5145, 5283, 5285, 5289, 5293, 5516, 5737, 5749, 6194, 6199, 6203, 6207, 6251, 6256, 6260, 6264,\
                6798, 6802, 6902, 6904, 6906, 6908, 7044, 7046, 7048, 7050, 7055, 8543, 8548, 8552, 8556, 8697, 9167, 9172, 9176, 9180, 9269,\
                9274, 9278, 9282, 10270, 10275, 10283, 10470, 10472, 10474, 10476, 10485

def openHorizontalDoor(creature, thing, position, **k):
    newPos = position[:]
    newPos[1] += 1
    
    transformItem(thing, item.itemId+1, position)
    relocate(position, newPos)

def openVerticalDoor(creature, thing, position, **k):
    newPos = position[:]
    newPos[1] += 1
    
    transformItem(thing, thing.itemId+1, position)
    relocate(position, newPos)

reg('use', openHorizontal, openHorizontalDoor)
reg('use', openVertical, openVerticalDoor)