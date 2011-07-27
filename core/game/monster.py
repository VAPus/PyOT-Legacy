from game.creature import Creature, CreatureBase, uniqueId
import game.engine, game.map, game.scriptsystem
from packet import TibiaPacket
import copy, random, time
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
monsters = {}

monsters["default"] = {"lookhead":0, "lookfeet":0, "lookbody":0, "looklegs":0}
class Monster(Creature):
    def generateClientID(self):
        return 0x40000000 + uniqueId()
        
    def __init__(self, base, position, cid=None):
        Creature.__init__(self, base.data, position, cid)
        self.base = base
        self.creatureType = 1
        self.spawnPosition = position[:]
        self.lastStep = 0
        self.speed = self.base.data["speed"]
    


class MonsterBase(CreatureBase):
    def __init__(self, data, brain, monsterData):
        self.data = data
        self.monsterData = monsterData
        self.voiceslist = []
        self.brain = brain
        self.scripts = {"onFollow":[], "onTargetLost":[]}
        
        self.setBehavior()
        self.setImmunity()
        self.walkAround()
        self.setRace()
        self.setDefense()
        
    def spawn(self, position, place=True):
        monster = Monster(self, position, None)
        self.brain.beginThink(monster) # begin the heavy thought process!

        if place:
                stackpos = game.map.getTile(position).placeCreature(monster)
                list = game.engine.getSpectators(position)
                for client in list:
                    stream = TibiaPacket()
                    stream.magicEffect(position, 0x03)
                    stream.addTileCreature(position, stackpos, monster, client.player)
            
                    stream.send(client)
        return monster
    def setHealth(self, health, healthmax=None):
        if not healthmax:
            healthmax = health
        self.data["health"] = health
        self.data["healthmax"] = healthmax
        
        return self

    def setRace(self, race="blood"):
        self.race = race
        
    def setDefense(self, armor=0, fire=1, earth=1, energy=1, ice=1, holy=1, death=1):
        self.armor = armor
        self.fire = fire
        self.earth = earth
        self.energy = energy
        self.ice = ice
        self.holy = holy
        self.death = death

    def setExperience(self, experience):
        self.data["experience"] = experience
        
    def setSpeed(self, speed):
        self.data["speed"] = 200
        
    def setBehavior(self, summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0):
        self.summonable = summonable
        self.attackable = attackable
        self.hostile = hostile
        self.illusionable = illusionable
        self.convinceable = convinceable
        self.pushable = pushable
        self.pushItems = pushItems
        self.pushCreaturse = pushCreatures
        self.targetDistance = targetDistance
        self.runOnHealth = runOnHealth
        
    def walkAround(self, energy=0, fire=0, poison=0):
        self.ignoreEnergy = energy
        self.ignoreFire = fire
        self.ignorePoison = poison
        
    def setImmunity(self, paralyze=1, invisible=1, lifedrain=1):
        self.paralyze = paralyze
        self.invisible = invisible
        self.lifedrain = lifedrain
        
    def voices(self, *argc):
        self.voiceslist = tuple(argc)

class MonsterBrain:
    def beginThink(self, monster):
        monster.actionThink = LoopingCall(self.handleThink, monster)
        monster.actionThink.start(1, False)
        if monster.base.voiceslist:
            monster.actionTalk = LoopingCall(self.handleTalk, monster)
            monster.actionTalk.start(2, False)

    
    def handleThink(self, monster):
        # Walking
        if monster.target:
            if not monster.canSee(monster.target.position):
                monster.base.onTargetLost(monster.target)
                monster.target = None
                
            return
        elif not monster.target:
            spectators = game.engine.getSpectatorList(monster.position)
            if spectators:
                target = None
                if len(spectators) > 1:
                    bestDist = 0
                    for x in spectators:
                        dist = monster.distanceStepsTo(x.position)
                        if dist < bestDist:
                            bestDist = dist
                            target = x.player
                else:
                    target = spectators[0].player
                monster.target = target
                monster.base.onFollow(monster.target)
                game.engine.autoWalkCreatureTo(monster, monster.target.position, -1, False)
                def __followCallback(who):
                    if monster.target == who:
                        monster.stopAction()
                        game.engine.autoWalkCreatureTo(monster, monster.target.position, -1, False)
                        monster.target.scripts["onNextStep"].append(__followCallback)
                        
                monster.target.scripts["onNextStep"].append(__followCallback)
                return
        if time.time() - monster.lastStep > 3:
            self.walkRandomStep(monster)
            
    def handleTalk(self, monster):
        if 10 > random.randint(0, 100): # 10%. TODO: Support config
            text = random.choice(monster.base.voiceslist)
            if text.isupper():
                monster.yell(text)
            else:
                monster.say(text)
                
    def walkRandomStep(self, monster):
        spectators = game.engine.getSpectatorList(monster.position)
        if not spectators:
            return False
        
        steps = []
        xFrom = monster.position[0]-monster.spawnPosition[0]
        yFrom = monster.position[1]-monster.spawnPosition[1]
        
        steps = [0,1,2,3]
        random.shuffle(steps)
        for step in steps:
            if step is 0:
                if monster.spawnPosition[1]-(monster.position[1]-1) > 5:
                    print "Stop by north"
                    print monster.position, " vs ", monster.spawnPosition
                    continue
            elif step is 1:
                if (monster.position[0]+1)-monster.spawnPosition[0] > 5:
                    print "Stop by east"
                    print monster.position, " vs ", monster.spawnPosition
                    continue
            elif step is 2:
                if (monster.position[1]+1)-monster.spawnPosition[1] > 5:
                    print "Stop by south"
                    print monster.position, " vs ", monster.spawnPosition
                    continue
            elif step is 3:
                if monster.spawnPosition[0]-(monster.position[0]-1) > 5:
                    print monster.position, " vs ", monster.spawnPosition
                    print "Stop by west"
                    continue
                
            if monster.move(step, spectators):
                monster.lastStep = time.time()
                return True
        return False
        
brains = {}
brains["default"] = MonsterBrain()
def genMonster(name, look, description="", brain="default", template="default"):
    # First build the common creature data
    if template in monsters:
        data = copy.copy(monsters[template])

    data["looktype"] = look[0]
    data["name"] = name
    # Then monster only data
    monsters[name] = MonsterBase(data, brains[brain], None)

    return monsters[name]

def getMonster(name):
    if name in monsters:
        return monsters[name]
    else:
        return None