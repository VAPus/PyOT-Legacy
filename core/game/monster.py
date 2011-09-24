from creature import Creature, CreatureBase, uniqueId
import engine, map, scriptsystem
from packet import TibiaPacket
import copy, random, time
from twisted.internet import reactor, defer
from twisted.internet.task import LoopingCall
from twisted.python import log
import enum
import errors
import item
import config

monsters = {}
brainFeatures = ({},{})

def chance(procent):
    def gen(monster):
        if 10 > random.randint(0, 100):
            return True
        else:
            return False
    return gen
    
class Monster(Creature):
    def generateClientID(self):
        return 0x40000000 + uniqueId()

    def isMonster(self):
        return True
        
    def __init__(self, base, position, cid=None):
        Creature.__init__(self, base.data.copy(), position, cid)
        self.base = base
        self.creatureType = 1
        self.spawnPosition = position[:]
        self.lastStep = 0
        self.speed = float(self.base.speed)
        self.lastMelee = 0
        self.walkPer = base.walkPer
        self.noBrain = True
        self.spawnTime = None
        self.radius = 5
        self.activeSummons = []
        self.master = None
        self.respawn = True
        
    def actionIds(self):
        return ('creature', 'monster', self.data["name"]) # Static actionIDs

    def setMaster(self, creature):
        self.master = creature
        self.respawn = False

    def setRespawn(self, state):
        self.respawn = state
        
    def damageToBlock(self, dmg, type):
        if type == enum.MELEE:
            return dmg - self.base.armor
        elif type == enum.PHYSICAL:
            return dmg * self.base.physical
        elif type == enum.FIRE:
            return dmg * self.base.fire
        elif type == enum.EARTH:
            return dmg * self.base.earth
        elif type == enum.ENERGY:
            return dmg * self.base.energy
        elif type == enum.ICE:
            return dmg * self.base.ice
        elif type == enum.HOLY:
            return dmg * self.base.holy
        elif type == enum.DEATH:
            return dmg * self.base.death
        elif type == enum.DROWN:
            return dmg * self.base.drown
        
        # What, no match?
        return dmg
        
    def onDeath(self):            
        # Transform
        tile = map.getTile(self.position)
        lootMsg = []
        corpse = item.Item(self.base.data["corpse"])
        if "containerSize" in item.items[self.base.data["corpse"]]:
            maxSize = item.items[self.base.data["corpse"]]["containerSize"]
            drops = []
            for loot in self.base.lootTable:
                if config.lootDropRate*loot[1]*100 > random.randint(0, 10000):
                    if len(drops)+1 == maxSize:
                        if config.stockLootInBagsIfNeeded:
                            drops.insert(0, (config.stockLootBagId, None))
                            maxSize += item.items[config.stockLootBagId]["containerSize"]
                        else:
                            drops.append(loot)
                            break
                    else:        
                        drops.append(loot)
                        
                elif len(loot) == 4:
                    drops.append((loot[0], None, loot[4]))
                    
            ret = scriptsystem.get("loot").runSync(self, self.lastDamager, loot=drops, maxSize=maxSize)
            if type(ret) == list:
                drops = ret

            for loot in drops:
                lenLoot = len(loot)
                ret = 0
                if lenLoot == 2:
                    ritem = item.Item(random.choice(loot[0]) if isinstance(loot[0], list) else loot[0], 1)
                    lootMsg.append(ritem.name())
                    ret = corpse.container.placeItemRecursive(ritem)
                        
                elif lenLoot == 3:
                    count = random.randint(1, loot[2]) * config.lootMaxRate
                    if count > 100:
                        while count:
                            depCount = min(count, 100)
                            ritem = item.Item(random.choice(loot[0]) if isinstance(loot[0], list) else loot[0], depCount)
                            lootMsg.append(ritem.name())
                            ret = corpse.container.placeItemRecursive(ritem)
                            count -= depCount
                    else:
                        ritem = item.Item(random.choice(loot[0]) if isinstance(loot[0], list) else loot[0], count)
                        lootMsg.append(ritem.name())
                        ret = corpse.container.placeItemRecursive(ritem)
                            
                elif lenLoot == 4:
                    count = random.randint(loot[4], loot[2]) * config.lootMaxRate
                    if count > 100:
                        while count:
                            depCount = min(count, 100)
                            ritem = item.Item(random.choice(loot[0]) if isinstance(loot[0], list) else loot[0], depCount)
                            lootMsg.append(ritem.name())
                            ret = corpse.container.placeItemRecursive(ritem)
                            count -= depCount
                                
                    else:
                        ritem = item.Item(random.choice(loot[0]) if isinstance(loot[0], list) else loot[0], count)
                        lootMsg.append(ritem.name())
                        ret = corpse.container.placeItemRecursive(ritem)
                            

                if ret == None:
                    log.msg("Warning: Monster '%s' extends all possible loot space" % self.data['name'])
                    break

        scriptsystem.get("death").runSync(self, self.lastDamager, corpse=corpse)
        if self.alive or self.data["health"] > 0:
            return
        corpse.decay(self.position)
        splash = item.Item(enum.FULLSPLASH)
        splash.fluidSource = self.base.blood
        splash.decay(self.position)
        
        tile.placeItem(corpse)
        tile.placeItem(splash)
        try:
            tile.removeCreature(self)
        except:
            pass
        engine.updateTile(self.position, tile)

        if self.lastDamager and self.lastDamager.isPlayer():
            if lootMsg:
                self.lastDamager.message("Loot of %s: %s." % (self.data["name"], ','.join(lootMsg)), 'MSG_LOOT')
            else:
                self.lastDamager.message("Loot of %s: Nothing." % (self.data["name"]), 'MSG_LOOT')
                
            if self.lastDamager.data["stamina"] or config.noStaminaNoExp == False:
                self.lastDamager.modifyExperience(self.base.experience * config.experienceRate)

            if self.base.experience >= self.lastDamager.data["level"]:
                self.lastDamager.soulGain()
        
        # Begin respawn
        # TODO just respawn <this> class, can't possibly bind so many kb :p
        if self.respawn:
            if self.spawnTime:
                engine.safeCallLater(self.spawnTime, self.base.spawn, self.spawnPosition)
            else:
                engine.safeCallLater(self.base.spawnTime, self.base.spawn, self.spawnPosition)
            
    def say(self, message, messageType='MSG_SPEAK_MONSTER_SAY'):
        return Creature.say(self, message, messageType)
        
    def yell(self, message, messageType='MSG_SPEAK_MONSTER_YELL'):
        return Creature.yell(self, message, messageType)

    def description(self):
        return "You see %s" % self.base.data["description"]

    def isPushable(self, by):
        return self.base.pushable

    def isAttackable(self, by):
        return self.base.attackable
        
class MonsterBase(CreatureBase):
    def __init__(self, data, brain):
        self.data = data
        self.voiceslist = []
        self.brain = brain
        self.scripts = {"onFollow":[], "onTargetLost":[]}
        self.summons = []
        self.maxSummon = 1
        
        self.spawnTime = 60
        
        self.speed = 100
        self.experience = 0
        
        self.attackable = True
        
        self.setBehavior()
        self.setImmunity()
        self.walkAround()
        self.bloodType()
        self.setTargetChance()
        
        self.meleeAttacks = []
        self.spellAttacks = []
        self.defenceSpells = []
        
        self.intervals = {}
        self.lootTable = []
        
        self.walkable = True
        self.walkPer = config.monsterWalkPer
        
        self.brainFeatures = ["default"]
        
    def spawn(self, position, place=True, spawnTime=None, spawnDelay=0.10, radius=5, radiusTo=None):
        if spawnDelay:
            return engine.safeCallLater(spawnDelay, self.spawn, position, place, spawnTime, 0, radius, radiusTo)
        else:
            if place:
                tile = map.getTile(position)
                if tile.creatures() and config.tryToSpawnCreaturesNextToEachother:
                    ok = False
                    for testx in (-1,0,1):
                        position[0] += testx
                        tile = map.getTile(position)
                        if tile.creatures():
                            for testy in (-1,0,1):
                                position[0] += testy
                                tile = map.getTile(position)
                                if not tile.creatures():
                                    try:
                                        monster = Monster(self, position, None)
                                        stackpos = map.getTile(position).placeCreature(monster)
                                        if stackpos > 9:
                                            log.msg("Can't place creatures on a stackpos > 9")
                                            return
                                        ok = True
                                    except:
                                        pass
                                    break
                        else:
                            
                            try:
                                monster = Monster(self, position, None)
                                stackpos = map.getTile(position).placeCreature(monster)
                                if stackpos > 9:
                                    log.msg("Can't place creatures on a stackpos > 9")
                                    return
                                ok = True
                            except:
                                pass
                        if ok:
                            break
                    if not ok:
                        log.msg("Spawning of creature('%s') on %s failed" % (self.data["name"], str(position)))
                        return
                elif not tile.creatures() or config.tryToSpawnCreatureRegardlessOfCreatures:
                    try:
                        monster = Monster(self, position, None)
                        stackpos = tile.placeCreature(monster)
                    except:
                        log.msg("Spawning of creature('%s') on %s failed" % (self.data["name"], str(position)))
                        return
                else:
                    log.msg("Spawning of creature('%s') on %s failed" % (self.data["name"], str(position)))
                    return
                        
            else:
                monster = Monster(self, position, None)
                
            if spawnTime:
                monster.spawnTime = spawnTime
            monster.radius = radius
            
            if radius <= 1:
                self.walkable = False
            if radiusTo:
                monster.radiusTo = radiusTo
            else:
                monster.radiusTo = (position[0], position[1])
                
            
            if self.targetChance and not (self.meleeAttacks or self.spellAttacks):
                log.msg("Warning: '%s' have targetChance, but no attacks!" % self.data["name"])

            if place:
                for player in engine.getPlayers(position):
                    if player.client and player.canSee(monster.position):
                        stream = player.packet()
                        stream.addTileCreature(position, stackpos, monster, player)
                            
                        stream.send(player.client)
            if engine.getPlayers(position):        
                self.brain.beginThink(monster) # begin the heavy thought process!
            return monster
        
    def setHealth(self, health, healthmax=None):
        if not healthmax:
            healthmax = health
        self.data["health"] = health
        self.data["healthmax"] = healthmax
        
        return self

    def defaultSpawnTime(self, spawnTime):
        self.spawnTime = spawnTime
        
    def bloodType(self, color="blood"):
        self.blood = getattr(enum, 'FLUID_'+color.upper())

    def setOutfit(self, lookhead, lookbody, looklegs, lookfeet):
        self.data["lookhead"] = lookhead
        self.data["lookbody"] = lookbody
        self.data["looklegs"] = looklegs
        self.data["lookfeet"] = lookfeet

    def setAddons(self, addon):
        self.data["lookaddons"] = addon
        
    def setDefense(self, armor=0, fire=1, earth=1, energy=1, ice=1, holy=1, death=1, physical=1, drown=1):
        self.armor = armor
        self.fire = fire
        self.earth = earth
        self.energy = energy
        self.ice = ice
        self.holy = holy
        self.death = death
        self.drown = drown
        self.physical = physical
        if armor == -1:
            self.attackable = False
    def setTargetChance(self, chance=10):
        self.targetChance = chance
    
    def maxSummons(self, max):
        self.maxSummon = max
        
    def summon(self, monster=None, chance=10):
        self.summons.append((monster, chance)) 
        
    def setExperience(self, experience):
        self.experience = experience
        
    def setSpeed(self, speed):
        self.speed = speed
        
    def setBehavior(self, summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0, targetChange=1):
        self.summonable = summonable
        self.hostile = hostile
        self.illusionable = illusionable
        self.convinceable = convinceable
        self.pushable = pushable
        self.pushItems = pushItems
        self.pushCreaturse = pushCreatures
        self.targetDistance = targetDistance
        self.runOnHealth = runOnHealth
        self.targetChange = targetChange
        
    def walkAround(self, energy=0, fire=0, poison=0):
        self.ignoreEnergy = energy
        self.ignoreFire = fire
        self.ignorePoison = poison
        
    def setImmunity(self, paralyze=1, invisible=1, lifedrain=1, drunk=1):
        self.paralyze = paralyze
        self.invisible = invisible
        self.lifedrain = lifedrain
        self.drunk = drunk

    def setWalkable(self, state):
        self.walkable = state

    def setRandomWalkInterval(self, per):
        self.walkPer = per

    def setBrainFeatures(self, *argc):
        self.brainFeatures = argc
        
    def voices(self, *argc):
        self.voiceslist = tuple(argc)

    def regMelee(self, maxDamage, check=lambda x: True, interval=config.meleeAttackSpeed, condition=None, conditionChance=0, conditionType=enum.CONDITION_ADD):
        self.meleeAttacks.append([interval, check, maxDamage, condition, conditionChance, conditionType])
        
    def regTargetSpell(self, spellName, min, max, interval=1, check=chance(10), range=1):
        self.spellAttacks.append([interval, spellName, check, range, (min, max)])
        
    def regSelfSpell(self, spellName, min, max, interval=1, check=chance(10)):
        self.defenceSpells.append([interval, spellName, check, (min, max)])
        
    def regBoost(self, ability, chance, change, duration):
        pass # TODO
        
    def loot(self, *argc):
        # Convert name to Id here
        if config.lootInAlphabeticalOrder:
            cache = []
            for loot in argc:
                # Id to name
                if type(loot[0]) == int:
                    loot = list(loot)
                    loot[0] = item.items[loot[0]]["name"]
        
                cache.append(loot)  
                
            cache.sort(reverse=True)    
            
            for loot in cache:
                if type(loot[0]) == tuple:
                    loot = list(loot)
                    loots = loot[0][:]
                    loot[0] = []
                    for ritem in loots:
                        loot[0].append(item.itemNames[ritem])
                        
                else:
                    loot = list(loot)
                    loot[0] = item.itemNames[loot[0]]
        
                self.lootTable.append(loot)  
            
        else:
            for loot in argc:
                if type(loot[0]) == tuple:
                    loot = list(loot)
                    loots = loot[0][:]
                    loot[0] = []
                    for ritem in loots:
                        loot[0].append(item.itemNames[ritem])
                        
                elif type(loot[0]) == str:
                    loot = list(loot)
                    loot[0] = item.itemNames[loot[0]]
        
                self.lootTable.append(loot)
        
class MonsterBrain(object):
    def beginThink(self, monster, isOk=False):
        monster.noBrain = False
        self.handleThink(monster)
        if monster.base.voiceslist:
            self.handleTalk(monster)
                
    @engine.loopInThread(0.5)
    def handleThink(self, monster, check=True):
        monster.noBrain = False
        # Are we alive?
        if not monster.alive:
            monster.noBrain = True
            return False # Stop looper
            
        for feature in monster.base.brainFeatures:
            if feature in brainFeatures[0]:
                ret = brainFeatures[0][feature](self, monster)
                
                if ret in (True, False):
                    return ret

        for feature in monster.base.brainFeatures:
            if feature in brainFeatures[1]:
                ret = brainFeatures[1][feature](self, monster)

                if ret in (True, False):
                    return ret
                    
        # Are anyone watching?
        if check and not engine.getSpectators(monster.position, (9, 7)):
            monster.noBrain = True
            return False
        
        if monster.base.walkable and not monster.action and not monster.target and time.time() - monster.lastStep > monster.walkPer: # If no other action is available
            self.walkRandomStep(monster) # Walk a random step
            
    @engine.loopInThread(2)        
    def handleTalk(self, monster):
        # Are we alive?
        if not monster.alive:
            return False # Stop looper
            
        if 10 > random.randint(0, 100): # 10%
            # Find a random text
            text = random.choice(monster.base.voiceslist)
            
            # If text is uppercase, then yell it.
            if text.isupper():
                monster.yell(text)
            else:
                monster.say(text)
                
    def walkRandomStep(self, monster, badDir=None):
        # How far are we (x,y) from our spawn point?
        xFrom = monster.position[0]-monster.spawnPosition[0]
        yFrom = monster.position[1]-monster.spawnPosition[1]
        
        steps = [0,1,2,3]
        if badDir == None:
            badDir = []
        
        random.shuffle(steps)
        
        for step in steps:
            # Prevent checks in "bad" directions
            if step in badDir:
                continue
            
            # Prevent us from autowalking futher then 5 steps
            if step == 0 and monster.radiusTo[1]-(monster.position[1]-1) > monster.radius:
                continue
                
            elif step == 1 and (monster.position[0]+1)-monster.radiusTo[0] > monster.radius:
                continue
                
            elif step == 2 and (monster.position[1]+1)-monster.radiusTo[1] > monster.radius:
                continue
                
            elif step == 3 and monster.radiusTo[0]-(monster.position[0]-1) > monster.radius:
                continue
            
            elif monster.target and enine.positionInDirection(monster.position, step) == monster.target.position:
                continue
            
            badDir.append(step)
            def success(result):
                monster.lastStep = time.time()
            
            def errback(result):
                if config.monsterNeverSkipWalks:
                    self.walkRandomStep(monster, badDir)
            
            d = defer.Deferred()
            d.addCallback(success)
            
            d.addErrback(errback)
            monster._move(d, step)

            return True
        return False
        
brain = MonsterBrain()
def genMonster(name, look, description=""):
    # baseMonsters
    baseMonster = MonsterBase({"lookhead":0, "lookfeet":0, "lookbody":0, "looklegs":0, "lookaddons":0, "looktype":look[0], "corpse":look[1], "name":name, "description":description or "a %s." % name}, brain)
    monsters[name] = baseMonster

    return baseMonster

def getMonster(name):
    try:
        return monsters[name]
    except:
        pass
        
def regBrainFeature(name, function, priority=1):
    if not name in brainFeatures[priority]:
        brainFeatures[priority][name] = function
    else:
        print "Warning, brain feature %s exists!" % name