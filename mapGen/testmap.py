from generator import *

map = Map(640,640, ground=493) # Make a 640x640 map filled with water

area = Area(150,150, ground=RSItem(106,108,109)) # Make a 150x150 area, with Random Static item (from 106 or 108)

monster = Monster('Kongra') # Make a Kongra
for x in xrange(0, 10):
    for y in xrange(0,10):
        area.add(90+(x*5), 90+(y*5), monster) # Put Kongra on this part of the area

map.merge(area, 40, 40) # Put the area into the map
map.compile() # Compile the map

