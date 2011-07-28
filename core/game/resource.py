
# This is a shared resource maanger that we will use for quests, mounts and outfits

### Outfits ###
outfits = []
reverseOutfits = {}
class Outfit(object):
    def __init__(self, name="", premium=False):
        self.premium = premium
        self.name = name
        self.gender = None
        self.looks = {} # gender=>(looktype ---)

    def look(self, looktype, lookhead=0, lookbody=0, looklegs=0, lookfeet=0, gender=0):
        self.looks[gender] = [looktype, lookhead, lookbody, looklegs, lookfeet]
        
    def getLook(self, gender=0):
        return self.looks[gender]
        

def regOutfit(outfit):
    outfits.append(outfit)
    reverseOutfits[outfit.name] = len(outfits)-1

def getOutfit(name):
    return outfits[reverseOutfits[name]]
# Helper call
def genOutfit(name, premium=False):
    outfit = Outfit(name, premium)
    regOutfit(outfit)
    return outfit
    
    
    
### Mounts ###
mounts = []
reverseMounts = {} # id and name

class Mount(object):
    def __init__(self, name, cid, speed=0, premium=False):
        self.premium = premium
        self.name = name
        self.cid = cid
        self.speed = speed
        

def regMount(mount):
    mounts.append(mount)
    reverseMounts[mount.name] = len(mounts)-1
    reverseMounts[mount.cid] = len(mounts)-1 

def getMount(name):
    return mounts[reverseMounts[name]]
    
# Helper call
def genMount(name, cid, speed=0, premium=False):
    mount = Mount(name, cid, speed, premium)
    regMount(mount)
    return mount