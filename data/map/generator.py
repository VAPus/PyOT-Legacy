# Format WILL change, I'm surtain
import json, zlib


# Make 128 tiles
x = 1
y = 1
for n in range(0, 16):
	for m in range(0, 16):
		map = {}
		for xx in range(x, x+64):
			map[xx] = {}
			for yy in range(y, y+64):
				map[xx][yy] = {}
			
				# We only make one level for now, 7
				map[xx][yy][7] = ([106], {}) # Format being ( [ground, items], {tile flags/options}, (Monster names) )
	
		open("map_%d_%d.sec" % (n,m), "w+b").write(zlib.compress( json.dumps(map, separators=(',', ':'), indent=0).replace("\n", ''), 1 ))
		y += 64
	x += 64
