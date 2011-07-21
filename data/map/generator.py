# Format WILL change, I'm certain
import json, zlib, random


# Make 400 tiles
x = 1
y = 1
monsterCount = 0
for n in range(0, 20):
	for m in range(0, 20):
		map = {}
		for xx in range(x, x+32):
			map[xx] = {}
			for yy in range(y, y+32):
				map[xx][yy] = {}
			
				# We only make one level for now, 7
				map[xx][yy][7] = [[106], {}] # Format being ( [ground, items], {tile flags/options}, (Monster names) )
				
				# Item random spawner :p
				if n > 2 and m > 2:
					ok = random.randint(0,50) == 10 # Funny way to make 2% ey?
					if ok:
						map[xx][yy][7].append(["Kongra"])
						monsterCount += 1
		open("map_%d_%d.sec" % (n,m), "w+b").write(zlib.compress( json.dumps(map, separators=(',', ':'), indent=0).replace("\n", ''), 1 ))
		y += 32
	x += 32
	y = 1

print "640x640 map generated with %d monsters" % monsterCount
