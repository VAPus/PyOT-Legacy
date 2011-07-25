from generator import *

map = Map(640,640, ground=106)

area = Area(150,150, ground=106)

monster = Monster('Kongra')
area.add(75, 75, monster)

map.merge(area, 300, 300)
map.compile()

