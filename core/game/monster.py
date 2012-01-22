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
    if procent == 100: return (lambda creature: True)
    elif procent == 0: return (lambda creature: False)
    
    def gen(creature):
        if random.randint(0, 99) < procent:
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
        self.spawnPosition = position.copy()
        self.lastStep = 0
        self.speed = float(base.speed)
        self.lastMelee = 0
        self.lastDistance = 0
        self.walkPer = base.walkPer
        self.noBrain = True
        self.spawnTime = None
        self.radius = 5
        self.master = None
        self.respawn = True
        self.skull = base.skull # We make a copy of the int so we might set a skull in scripts later.
        self.canWalk = base.walkable
        self.intervals = {}

    def actionIds(self):
        return ('creature', 'monster', self.data["name"]) # Static actionIDs

    def setMaster(self, creature):
        self.master = creature
        self.respawn = False

    def setRespawn(self, state):
        self.respawn = state
    
    def isSummon(self):
        if self.master:
            return True
        else:
            return False
            
    def isSummonFor(self, creature):
        return self.master == creature
        
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
        # Remove master summons
        if self.master:
            self.master.activeSummons.remove(self)
            
        self.noBrain = True
        
        # Remove summons
        if self.activeSummons:
            for summon in self.activeSummons:
                summon.magicEffect(EFFECT_POFF)
                summon.despawn()
                summon.noBrain = True
                
        # Transform
        tile = map.getTile(self.position)
        lootMsg = []
        corpse = game.item.Item(self.base.data["corpse"], actions=self.base.corpseAction)
        if self.lastDamager != self.master:
            try:
                maxSize = game.item.items[self.base.data["corpse"]]["containerSize"]
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
                        ritem = game.item.Item(random.choice(loot[0]) if isinstance(loot[0], list) else loot[0], 1)
                        lootMsg.append(ritem.name())
                        ret = corpse.container.placeItemRecursive(ritem)
                            
                    elif lenLoot == 3:
                        count = random.randint(1, loot[2]) * config.lootMaxRate
                        if count > 100:
                            while count:
                                depCount = min(count, 100)
                                ritem = game.item.Item(random.choice(loot[0]) if isinstance(loot[0], list) else loot[0], depCount)
                                lootMsg.append(ritem.name())
                                ret = corpse.container.placeItemRecursive(ritem)
                                count -= depCount
                        else:
                            ritem = game.item.Item(random.choice(loot[0]) if isinstance(loot[0], list) else loot[0], count)
                            lootMsg.append(ritem.name())
                            ret = corpse.container.placeItemRecursive(ritem)
                                
                    elif lenLoot == 4:
                        count = random.randint(loot[4], loot[2]) * config.lootMaxRate
                        if count > 100:
                            while count:
                                depCount = min(count, 100)
                                ritem = game.item.Item(random.choice(loot[0]) if isinstance(loot[0], list) else loot[0], depCount)
                                lootMsg.append(ritem.name())
                                ret = corpse.container.placeItemRecursive(ritem)
                                count -= depCount
                                    
                        else:
                            ritem = game.item.Item(random.choice(loot[0]) if isinstance(loot[0], list) else loot[0], count)
                            lootMsg.append(ritem.name())
                            ret = corpse.container.placeItemRecursive(ritem)
                                

                    if ret == None:
                        log.msg("Warning: Monster '%s' extends all possible loot space" % self.data['name'])
                        break
            except:
                pass
        
        scriptsystem.get("death").runSync(self, self.lastDamager, corpse=corpse)
        if self.alive or self.data["health"] > 0:
            return
        corpse.decay(self.position)
        # Remove bpth small and full splashes on the tile.
        for item in tile.getItems():
            if item.itemId in enum.SMALLSPLASHES or item.itemId in enum.FULLSPLASHES:
                tile.removeItem(item)
        
        # Add full splash
        splash = game.item.Item(enum.FULLSPLASH)
        splash.fluidSource = self.base.blood
        splash.decay(self.position)
        
        tile.placeItem(corpse)
        tile.placeItem(splash)
        
        
        # Remove me. This also refresh the tile.
        self.remove()

        if self.lastDamager and self.lastDamager.isPlayer() and self.lastDamager != self.master:
            if lootMsg:
                self.lastDamager.message("Loot of %s: %s." % (self.data["name"], ','.join(lootMsg)), 'MSG_LOOT')
            else:
                self.lastDamager.message("Loot of %s: Nothing." % (self.data["name"]), 'MSG_LOOT')
                
            if self.lastDamager.data["stamina"] or config.noStaminaNoExp == False:
                self.lastDamager.modifyExperience(self.base.experience *self.lastDamager.getExperienceRate())

            if self.base.experience >= self.lastDamager.data["level"]:
                self.lastDamager.soulGain()
        
        # Begin respawn
        if self.respawn:
            self.position = self.spawnPosition
            self.target = None
            self.targetMode = 0
            if self.spawnTime != 0:
                if self.spawnTime:
                    engine.safeCallLater(self.spawnTime, self.base.spawn, self.spawnPosition, spawnDelay=0, monster=self)
                else:
                    return
            else:
                engine.safeCallLater(self.base.spawnTime, self.base.spawn, self.spawnPosition, spawnDelay=0, monster=self)
            
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
        self.distanceAttacks = []
        self.spellAttacks = []
        self.defenceSpells = []
        
        self.intervals = {}
        self.lootTable = []
        
        self.walkable = True
        self.walkPer = config.monsterWalkPer
        
        self.brainFeatures = ["default"]
        self.skull = 0
        
        self.corpseAction = []
        
    def spawn(self, position, place=True, spawnTime=None, spawnDelay=0.1, radius=5, radiusTo=None, monster=None):
        if not monster:
            monster = Monster(self, position, None)
        if spawnDelay:
            return engine.safeCallLater(spawnDelay, self.spawn, position, place, spawnTime, 0, radius, radiusTo, monster)
        else:
            if not monster.alive:
                monster.data = monster.base.data.copy()
                monster.alive = True
                
            if place:
                tile = map.getTile(position)
                if not tile:
                    log.msg("Spawning of creature('%s') on %s failed. Tile does not exist!" % (self.data["name"], str(position)))
                    return
                elif tile.creatures() and config.tryToSpawnCreaturesNextToEachother:
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
                                        stackpos = map.getTile(position).placeCreature(monster)
                                        ok = True
                                    except:
                                        pass
                                    break
                        else:
                            
                            try:
                                stackpos = map.getTile(position).placeCreature(monster)
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
                        stackpos = tile.placeCreature(monster)
                    except:
                        log.msg("Spawning of creature('%s') on %s failed" % (self.data["name"], str(position)))
                        return
                else:
                    log.msg("Spawning of creature('%s') on %s failed" % (self.data["name"], str(position)))
                    return
                
            monster.spawnTime = spawnTime
            monster.radius = radius
            
            if radius <= 1:
                self.walkable = False
            if radiusTo:
                monster.radiusTo = radiusTo
            else:
                monster.radiusTo = (position[0], position[1])
                
            
            if self.targetChance and not (self.meleeAttacks or self.spellAttacks or self.distanceAttacks):
                log.msg("Warning: '%s' have targetChance, but no attacks!" % self.data["name"])

            if place and stackpos and stackpos < 10:
                for player in engine.getPlayers(position):
                    if player.client and player.canSee(monster.position):
                        stream = player.packet()
                        stream.addTileCreature(position, stackpos, monster, player)
                            
                        stream.send(player.client)
            if engine.hasSpectators(position):        
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

    def regCorpseAction(self, action):
        self.corpseAction.append(action)
        
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

    def setManaCost(self, mana):
        self.manacost = mana
        
    def voices(self, *argc):
        self.voiceslist = tuple(argc)

    def setSkull(self, skull):
        self.skull = skull
        
    def regMelee(self, maxDamage, check=lambda x: True, interval=config.meleeAttackSpeed, condition=None, conditionChance=0, conditionType=enum.CONDITION_ADD):
        self.meleeAttacks.append([interval, check, maxDamage, condition, conditionChance, conditionType])
		
    def regDistance(self, maxDamage, shooteffect, check=chance(10), interval=config.meleeAttackSpeed):
        self.distanceAttacks.append([interval, maxDamage, shooteffect, check]) 
        
    def regTargetSpell(self, spellName, min, max, interval=2, check=chance(10), range=7, length=None):
        if length:
            self.spellAttacks.append([interval, spellName, check, range, (min, max, length)])
        else:
            self.spellAttacks.append([interval, spellName, check, range, (min, max)])
            
    def regSelfSpell(self, spellName, min, max, interval=2, check=chance(10), length=None):
        if length:
            self.defenceSpells.append([interval, spellName, check, (min, max, length)])
        else:
            self.defenceSpells.append([interval, spellName, check, (min, max)])
        
    def loot(self, *argc):
        # Convert name to Id here
        if config.lootInAlphabeticalOrder:
            cache = []
            for loot in argc:
                # Id to name
                if type(loot[0]) == int:
                    loot = list(loot)
                    try:
                        loot[0] = item.items[loot[0]]["name"]
                    except:
                        print "ItemId %d not found in loot. Ignoring!" % loot[0]
                        continue
                cache.append(loot)  
                
            cache.sort(reverse=True)    
            
            for loot in cache[:]:
                if type(loot[0]) == tuple:
                    loot = list(loot)
                    loots = loot[0][:]
                    loot[0] = []
                    for ritem in loots:
                        try:
                            loot[0].append(item.itemNames[ritem])
                        except KeyError:
                            print "Monster loot, no item with the name '%s' exists (in %s)" % (ritem, self.data["name"])
                        
                else:
                    loot = list(loot)
                    try:
                        loot[0] = item.itemNames[loot[0]]
                    except KeyError:
                        print "Monster loot, no item with the name '%s' exists (in %s)" % (loot[0], self.data["name"])
                        
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
                
    @engine.loopInThread(2)
    #@engine.loopDecorator(2)
    def handleThink(self, monster, check=True):
        # Are we alive?
        if not monster.alive:
            monster.noBrain = True
            return False # Stop looper
        
        if monster.base.voiceslist:
            if 10 > random.randint(0, 100): # 10%
                # Find a random text
                text = random.choice(monster.base.voiceslist)
                
                # If text is uppercase, then yell it.
                if text.isupper():
                    monster.yell(text)
                else:
                    monster.say(text)
                    
        for feature in monster.base.brainFeatures:
            if feature in brainFeatures[0]:
                ret = brainFeatures[0][feature](self, monster)
                
                if ret in (True, False):
                    print ret
                    return ret

        for feature in monster.base.brainFeatures:
            if feature in brainFeatures[1]:
                ret = brainFeatures[1][feature](self, monster)

                if ret in (True, False):
                    print ret
                    return ret
                    
        # Are anyone watching?
        if not monster.target: # This have already been vertified!
            
            if check and not engine.hasSpectators(monster.position, (9, 7)):
                monster.noBrain = True
                return False
            
            if monster.canWalk and not monster.action and time.time() - monster.lastStep > monster.walkPer: # If no other action is available
                self.walkRandomStep(monster) # Walk a random step

    @defer.inlineCallbacks
    def walkRandomStep(self, monster, badDir=None):
        if not badDir:
            badDir = []
            
        # How far are we (x,y) from our spawn point?
        xFrom = monster.position.x-monster.spawnPosition.x
        yFrom = monster.position.y-monster.spawnPosition.y
        
        steps = [0,1,2,3]
        
        random.shuffle(steps)
        
        for step in steps:
            # Prevent checks in "bad" directions
            if step in badDir:
                continue
            
            # Prevent us from autowalking futher then 5 steps
            if step == 0 and monster.radiusTo[1]-(monster.position.y-1) > monster.radius:
                continue
                
            elif step == 1 and (monster.position.x+1)-monster.radiusTo[0] > monster.radius:
                continue
                
            elif step == 2 and (monster.position.x+1)-monster.radiusTo[1] > monster.radius:
                continue
                
            elif step == 3 and monster.radiusTo[0]-(monster.position.x-1) > monster.radius:
                continue
            
            badDir.append(step)
            d = yield monster.move(step)
            if d == False:
                if config.monsterNeverSkipWalks and len(badDir) < 4:
                    self.walkRandomStep(monster, badDir)
                
            return
        
brain = MonsterBrain()
def genMonster(name, look, description=""):
    # baseMonsters
    baseMonster = MonsterBase({"lookhead":0, "lookfeet":0, "lookbody":0, "looklegs":0, "lookaddons":0, "looktype":look[0], "corpse":look[1], "name":name, "description":description or "a %s." % name}, brain)
    """try:
        baseMonster.regCorpseAction(look[2])
    except:
        pass"""
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
