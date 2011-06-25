cidIndex = 1000

def cidGen(self):
    cidIndex += 1
    return cidIndex - 1
    
class Creature:
    def __init__(self, data, position, cid):
        self.data = data
        self.creatureType = 0
        self.direction = 0
        self.position = position
        self.modes = [0,0,0]
        self.stackpos = 1
        self.speed = 0x0032
        self.scripts = {}
        self.cid = cid
    def name(self):
        return self.data["name"]

    def clientId(self):
        return self.cid
        
    def stepDuration(self):
        return (1000 * 140 / self.speed) * 1 # TODO