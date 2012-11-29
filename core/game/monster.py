from creature import Creature, uniqueId, allCreatures
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
import game.errors

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
        self.brainEvent = None
        self.spawnTime = None
        self.radius = 5
        self.master = None
        self.respawn = True
        self.skull = base.skull # We make a copy of the int so we might set a skull in scripts later.
        self.canWalk = base.walkable
        self.intervals = {}
        self.defaultSpeakType = MSG_SPEAK_MONSTER_SAY
        self.defaultYellType = MSG_SPEAK_MONSTER_YELL
        self.lastRetarget = 0

    def actionIds(self):
        return ('creature', 'monster', self.data["name"]) # Static actionIDs

    def setMaster(self, creature):
        self.master = creature
        self.respawn = False

        # Reset target.
        self.target = None
        self.targetMode = 0

    def setRespawn(self, state):
        self.respawn = state
    
    def isSummon(self):
        if self.master:
            return True
        else:
            return False
            
    def isSummonFor(self, creature):
        return self.master == creature

    def __repr__(self):
        return "<Monster (%s, %d, %s) at %s>" % (self.data["name"], self.clientId(), self.position, hex(id(self)))
        
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

    def defaultSpeed(self):
        self.speed = float(self.base.speed)
    
    def turnOffBrain(self):
        try:
            self.brainEvent.cancel()
        except:
            pass
        
        self.brainEvent = None
        
    def onDeath(self):
        # Remove master summons
        if self.master:
            self.master.activeSummons.remove(self)

        self.turnOffBrain()
        
        # Remove summons
        if self.activeSummons:
            for summon in self.activeSummons:
                summon.magicEffect(EFFECT_POFF)
                summon.despawn()
                summon.turnOffBrain()
                
        # Transform
        tile = map.getTile(self.position)
        lootMsg = []
        if self.base.data["corpse"]:
            corpse = game.item.Item(self.base.data["corpse"], actions=self.base.corpseAction)
            
            # Set owner.
            if self.lastDamagers:
                if self.getLastDamager().isPlayer():
                    corpse.owners = [self.getLastDamager()]
            
                    def _clear_private_loot():
                        del corpse.owners
                
                    # Callback to remove owner after config.privateLootFor seconds
                    callLater(config.privateLootFor, _clear_private_loot)
            if not self.lastDamagers or self.getLastDamager() != self.master:
                try:
                    maxSize = game.item.items[self.base.data["corpse"]]["containerSize"]
                except:
                    print "[WARNING] Monster %s got a bad corpse" % self.name()
                    maxSize = 0
                drops = []
                for loot in self.base.lootTable:
                    if config.lootDropRate*loot[1]*100 > random.randint(0, 10000): # [7363, 28.5, 4]
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
                
                ret = scriptsystem.get("loot").runSync(self, self.getLastDamager() if self.lastDamagers else None, loot=drops, maxSize=maxSize)
                if type(ret) == list:
                    drops = ret

                for loot in drops:

                    lenLoot = len(loot)
                    ret = 0
                    if lenLoot == 2:
                        ritem = game.item.Item(random.choice(loot[0]) if isinstance(loot[0], list) else loot[0], 1)
                        lootMsg.append(ritem.name)
                        ret = corpse.placeItemRecursive(ritem)
                            
                    elif lenLoot == 3:
                        count = random.randint(1, loot[2]) * config.lootMaxRate
                        if count > 100:
                            while count:
                                depCount = min(count, 100)
                                ritem = game.item.Item(random.choice(loot[0]) if isinstance(loot[0], list) else loot[0], depCount)
                                lootMsg.append(ritem.name)
                                ret = corpse.placeItemRecursive(ritem)
                                count -= depCount
                        else:
                            ritem = game.item.Item(random.choice(loot[0]) if isinstance(loot[0], list) else loot[0], count)
                            lootMsg.append(ritem.name)
                            ret = corpse.placeItemRecursive(ritem)
                                
                    elif lenLoot == 4:
                        count = random.randint(loot[4], loot[2]) * config.lootMaxRate
                        if count > 100:
                            while count:
                                depCount = min(count, 100)
                                ritem = game.item.Item(random.choice(loot[0]) if isinstance(loot[0], list) else loot[0], depCount)
                                lootMsg.append(ritem.name)
                                ret = corpse.placeItemRecursive(ritem)
                                count -= depCount
                                    
                        else:
                            ritem = game.item.Item(random.choice(loot[0]) if isinstance(loot[0], list) else loot[0], count)
                            lootMsg.append(ritem.name)
                            ret = corpse.placeItemRecursive(ritem)
                                

                    if ret == None:
                        log.msg("Warning: Monster '%s' extends all possible loot space" % self.data['name'])
                        break

        else:
            corpse = None
            
        scriptsystem.get("death").runSync(self, self.getLastDamager() if self.lastDamagers else None, corpse=corpse)
        if self.alive or self.data["health"] > 0:
            print "[May bug] Death events brought us back to life?"
            return
        
        # Remove bpth small and full splashes on the tile.
        for item in tile.getItems():
            if item.itemId in enum.SMALLSPLASHES or item.itemId in enum.FULLSPLASHES:
                tile.removeItem(item)
        
        # Add full splash
        splash = game.item.Item(enum.FULLSPLASH)
        splash.fluidSource = self.base.blood
        
        if corpse:
            corpse.place(self.position)
        splash.place(self.position)
        
        # Start decay
        if corpse:
            corpse.decay()
        splash.decay()
        
        # Remove me. This also refresh the tile.
        self.remove()

        if self.lastDamagers and self.getLastDamager().isPlayer() and self.getLastDamager() != self.master:
            if lootMsg:
                self.getLastDamager().message(_l(self.getLastDamager(), "loot of %(who)s: %(loot)s") % {"who": self.data["name"].lower(), "loot": ', '.join(lootMsg)}, MSG_LOOT)
            else:
                self.getLastDamager().message(_l(self.getLastDamager(), "loot of %s: nothing") % (self.data["name"]), MSG_LOOT)
                
            # Experience split.
            attackerParty = self.getLastDamager().party()
            if attackerParty and attackerParty.shareExperience and attackerParty.checkShareExperience():
                for member in attackerParty.members:
                    if member.data["stamina"] or config.noStaminaNoExp == False:
                        exp = (self.base.experience / len(attackerParty.members)) * config.partyExperienceFactor
                        member.modifyExperience(exp * member.getExperienceRate())
                        
                        if exp >= member.data["level"]:
                            member.soulGain()
            else:
                if self.getLastDamager().data["stamina"] or config.noStaminaNoExp == False:
                    self.getLastDamager().modifyExperience(self.base.experience *self.getLastDamager().getExperienceRate())

                    if self.base.experience >= self.getLastDamager().data["level"]:
                        self.getLastDamager().soulGain()
       
        # Begin respawn
        if self.respawn:
            self.position = self.spawnPosition
            self.target = None
            self.targetMode = 0
            if self.spawnTime != 0:
                if self.spawnTime:
                    reactor.callLater(self.spawnTime, self.base.spawn, self.spawnPosition, spawnTime = self.spawnTime, spawnDelay=0, monster=self, check=True)
                else:
                    return
            else:
                reactor.callLater(self.base.spawnTime, self.base.spawn, self.spawnPosition, spawnDelay=0, monster=self, check=True)

    def description(self):
        return "You see %s" % self.base.data["description"]

    def isPushable(self, by):
        return self.base.pushable

    def isAttackable(self, by):
        return self.base.attackable

    def targetCheck(self, targets=None):
        _time = time.time()
        if self.lastRetarget > _time - 7:
            return
        self.lastRetarget = _time

        if not self.target:
            # Null walkpatterns.
            self.walkPattern = None
            
        _target = self.target
        if not targets:
            targets = engine.getPlayers(self.position) # Get all creaturse in range
            if not targets:
                self.target = None
                self.targetMode = 0
                return
                
        target = None
        
        bestDist = 127
        for player in targets:
            # Can we target him, same floor
            if player.isAttackable(self) and self.canTarget(player.position):
                path = calculateWalkPattern(self, self.position, player.position, -1, True)
                
                if not path and self.distanceStepsTo(player.position) > 0: continue
                # Calc x+y distance, diagonal is honored too.
                dist = len(path) 
                if dist < bestDist:
                    # If it's smaller then the previous value
                    bestDist = dist
                    target = player
        
        if _target == target:
            return # We already have this target
        elif target:
            ret = game.scriptsystem.get('target').runSync(self, target, attack=True)
            
            if ret == False:
                return
            elif ret != None:
                self.target = ret
            else:
                self.target = target
            self.targetMode = 1
        else:
            self.walkPattern = None
            self.stopAction()
            self.target = None
            self.targetMode = 0
            return
                    
        # When we reach our destination, can we target check
        def __walkComplete(x):
            if not x:
                # Walk not possible. Loose target
                self.target = None
                self.targetMode = 0
                return
            # Are we OK?
            if self.distanceStepsTo(self.target.position) <= self.base.targetDistance:
                self.turnAgainst(self.target.position)
            else:
                # Apperently not. Try walking again.
                if self.canTarget(self.target.position) and not self.walkPattern:
                    engine.autoWalkCreatureTo(self, self.target.position, -self.base.targetDistance, __walkComplete)
                            
        # Begin autowalking
        engine.autoWalkCreatureTo(self, self.target.position, -self.base.targetDistance, __walkComplete)
                    
        # If the target moves, we need to recalculate, if he moves out of sight it will be caught in next brainThink
        def __followCallback(who):
            if self.target == who:                       
                if self.canTarget(self.target.position):
                    engine.autoWalkCreatureTo(self, self.target.position, -self.base.targetDistance, __walkComplete)
                else:
                    self.target = None
                    self.targetMode = 0
                                    
                if self.target:
                    # We shall be called again later
                    self.target.scripts["onNextStep"].append(__followCallback)
                            
        self.target.scripts["onNextStep"].append(__followCallback)
        return True
        
        
    def verifyMove(self, tile):
        """ This function verify if the tile is walkable in a regular state (pathfinder etc)
            This function handle things like PZ.
        """
        
        # Protected zone?
        if tile.getFlags() & TILEFLAGS_PROTECTIONZONE:
            return False
            
        if not tile.things:
            return True

        for thing in tile.things:
            if isinstance(thing, Item):
                field = thing.field
                if self.base.ignoreFire and field == 'fire':
                    continue
                elif self.base.ignorePoison and field == 'poison':
                    continue
                elif self.base.ignoreEnergy and field == 'energy':
                    continue
                elif field:
                    return False
                elif thing.blockpath:
                    return False

            elif isinstance(thing, Creature):
                ok = not thing.solid
                if not ok and self.base.pushCreatures and isinstance(thing, Monster) and thing.base.pushable:
                    continue    
                if not ok:
                    return False
                       
        return True
        
class MonsterBase(object):
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
        self.setDefense()
        
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
        self.prepared = False
        self._loot = None
        
        
    def spawn(self, position, place=True, spawnTime=None, spawnDelay=0.1, radius=5, radiusTo=None, monster=None, check=False):
        if spawnDelay:
            return reactor.callLater(spawnDelay, self.spawn, position, place, spawnTime, 0, radius, radiusTo, monster, check)
        else:
            if place:
                tile = position.getTile()
                if not tile:
                    log.msg("Spawning of creature('%s') on %s failed. Tile does not exist!" % (self.data["name"], str(position)))
                    return

            if not monster:
                monster = Monster(self, position, None)
                if not self.prepared:
                    self.prepare()

            if not monster.alive:
                monster.data = monster.base.data.copy()
                monster.alive = True
            
            if not monster.clientId() in allCreatures:
                allCreatures[monster.clientId()] = monster
                
            monster.lastDamagers.clear()
            
            if place:
                # Vertify that there are no spectators if check = True
                if check and engine.hasSpectators(position): 
                    # If so, try again in 10s
                    reactor.callLater(10, self.spawn, position, place, spawnTime, 0, radius, radiusTo, monster, check)
                    return
                    
                elif tile.hasCreatures() and config.tryToSpawnCreaturesNextToEachother:
                    ok = False
                    for testx in (-1,0,1):
                        position[0] += testx
                        tile = map.getTile(position)
                        if tile.hasCreatures():
                            for testy in (-1,0,1):
                                position[0] += testy
                                tile = map.getTile(position)
                                if not tile:
                                    continue
                                
                                if not tile.hasCreatures():
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
                elif not tile.hasCreatures() or config.tryToSpawnCreatureRegardlessOfCreatures:
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

            if place and stackpos and stackpos < 10:
                for player in engine.getPlayers(position):
                    stream = player.packet()
                    stream.addTileCreature(position, stackpos, monster, player)
                            
                    stream.send(player.client) 
                        
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
        self.pushCreatures = pushCreatures
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

    def setSkull(self, skull):
        self.skull = skull
        
    def regMelee(self, maxDamage, check=lambda x: True, interval=config.meleeAttackSpeed, condition=None, conditionChance=0, conditionType=enum.CONDITION_ADD):
        self.meleeAttacks.append([interval, check, maxDamage, condition, conditionChance, conditionType])
        
    def regDistance(self, maxDamage, shooteffect, check=chance(10), interval=config.meleeAttackSpeed):
        self.distanceAttacks.append([interval, maxDamage, shooteffect, check]) 
        
    def regTargetSpell(self, spellName, min, max, interval=2, check=chance(10), range=7, length=None):
        if isinstance(spellName, spell.Spell) or isinstance(spellName, spell.Rune):
            obj = spellName
        elif isinstance(spellName, str):
            try:
                obj = spell.spells[spellName][0]
            except:
                raise game.errors.SpellDoesNotExist(spellName)
            
        elif isinstance(spellName, int):
            try:
                obj = spell.targetRunes[spellName]
            except:
                raise game.errors.RuneDoesNotExist(spellName)
            
        if length:
            self.spellAttacks.append([interval, obj, check, range, (min, max, length)])
        else:
            self.spellAttacks.append([interval, obj, check, range, (min, max)])
            
    def regSelfSpell(self, spellName, min, max, interval=2, check=chance(10), length=None):
        if isinstance(spellName, spell.Spell) or isinstance(spellName, spell.Rune):
            obj = spellName.func
        elif isinstance(spellName, str):
            obj = spell.spells[spellName][0]
        elif isinstance(spellName, int):
            obj = spell.targetRunes[spellName]
            
        if length:
            self.defenceSpells.append([interval, obj, check, (min, max, length)])
        else:
            self.defenceSpells.append([interval, obj, check, (min, max)])
        
    def loot(self, *argc):
        self._loot = argc
    def prepare(self):
        self.prepared = True
        if not self._loot:
            return
        
        argc = self._loot
        
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
                        sid = item.idByName(ritem)
                        if sid:
                            loot[0].append(sid)
                        else:
                            print "Monster loot, no item with the name '%s' exists (in %s)" % (ritem, self.data["name"])
                        
                else:
                    loot = list(loot)
                    sid = item.idByName(loot[0])
                    if sid:
                        loot[0] = sid
                    else:
                        print "Monster loot, no item with the name '%s' exists (in %s)" % (loot[0], self.data["name"])
                        
                self.lootTable.append(loot)  
            
        else:
            for loot in argc:
                if type(loot[0]) == tuple:
                    loot = list(loot)
                    loots = loot[0][:]
                    loot[0] = []
                    for ritem in loots:
                        loot[0].append(item.idByName(ritem))
                        
                elif type(loot[0]) == str:
                    loot = list(loot)
                    loot[0] = item.idByName(loot[0])
        
                self.lootTable.append(loot)
        del self._loot
class MonsterBrain(object):
    def beginThink(self, monster, check=False):
        if not monster.brainEvent:
            monster.brainEvent = reactor.callLater(0, self.handleThink, monster, check)
        else:
            raise Exception("Attempting to start a brain of a active monster!")
        
    def handleThink(self, monster, check=True):
        # Are we alive?
        if not monster.alive:
            monster.turnOffBrain()
            return False # Stop looper
        
        if monster.base.voiceslist and random.randint(0, 99) < 10: # 10%
            # Find a random text
            text = random.choice(monster.base.voiceslist)
                
            # If text is uppercase, then yell it.
            if text.isupper():
                monster.yell(text)
            else:
                monster.say(text)
                    
        feature = monster.base.brainFeatures[0]
        #for feature in monster.base.brainFeatures:
        ret = brainFeatures[0][feature](monster)
        if ret == False:
            monster.turnOffBrain()
            return False
        elif ret == True:
            monster.brainEvent = reactor.callLater(1, self.handleThink, monster)
            return True

        #for feature in monster.base.brainFeatures:
        ret = brainFeatures[1][feature](monster)

        if ret == False:
            monster.turnOffBrain()
            return False
        elif ret == True:
            monster.brainEvent = reactor.callLater(1, self.handleThink, monster)
            return True
                    
        # Are anyone watching?
        if not monster.target: # This have already been vertified!
            if check and not engine.hasSpectators(monster.position, (9, 7)):
                monster.turnOffBrain()
                return False
            if not monster.walkPattern and monster.canWalk and not monster.action and time.time() - monster.lastStep > monster.walkPer: # If no other action is available
                self.walkRandomStep(monster) # Walk a random step

        monster.brainEvent = reactor.callLater(1, self.handleThink, monster)
        
    def walkRandomStep(self, monster, badDir=None, steps=[0,1,2,3]):
        if not badDir:
            badDir = []

        random.shuffle(steps)
        
        for step in steps:
            # Prevent checks in "bad" directions
            if step in badDir:
                continue
            
            # Prevent us from autowalking futher then radius steps from our spawn point
            if step == 0 and monster.radiusTo[1]-(monster.position.y-1) > monster.radius:
                continue
                
            elif step == 1 and (monster.position.x+1)-monster.radiusTo[0] > monster.radius:
                continue
                
            elif step == 2 and (monster.position.y+1)-monster.radiusTo[1] > monster.radius:
                continue
                
            elif step == 3 and monster.radiusTo[0]-(monster.position.x-1) > monster.radius:
                continue
            
            badDir.append(step)
            if config.monsterNeverSkipWalks:
                def _():
                    if len(badDir) < 4:
                        self.walkRandomStep(monster, badDir)
                monster.move(step, failback=_, stopIfLock=True, push=False)
            else:
                monster.move(step, stopIfLock=True, push=False)
                
            return
        
brain = MonsterBrain()
def genMonster(name, look, description=""):
    # baseMonsters
    if isinstance(look, tuple):
        look, corpse = look
    else:
        corpse = idByName('dead %s' % name)
        if not corpse:
            corpse = idByName('slain %s' % name)
    baseMonster = MonsterBase({"lookhead":0, "lookfeet":0, "lookbody":0, "looklegs":0, "lookaddons":0, "looktype":look, "corpse":corpse, "name":name, "description":description or "a %s." % name}, brain)
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
