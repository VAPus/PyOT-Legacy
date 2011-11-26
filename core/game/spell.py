import game.scriptsystem # We use the talkactions from here
import game.item
import game.enum
import game.engine
import game.map
import random
import game.creature

spells = {}
fieldRunes = {}
targetRunes = {}

def calculateAreaDirection(position, direction, area):
    positions = []
    if area[0] == game.enum.TARGET_DIRECTION:
        # We begin on row 1, right in front of us
        yp = 1
        blocking = [] # We keep the blocking tiles from this row because we are using them in the next
        prevBlocking = []
        count = 0 # Count of fields in previous row, so we can calculate fields required
        minEntry = maxEntry = 0
        prevMinEntry = prevMaxEntry = 0
        for yo in area[1:]: # As you might know, area[0] is used to determin the type. yo == y list
                
            for xp in yo: # xp == x position from y list
                # First agenda is to determin whatever a previous field blocked us
                if count and prevBlocking:
                    if prevBlocking[0] == prevMinEntry and prevBlocking[0] >= xp: # Are we extending the so called minEntry border?
                        blocking.append(prevBlocking[0])
                        minEntry = prevMinEntry
                        continue
                    elif prevBlocking[-1] == prevMaxEntry and prevBlocking[-1] <= xp: # Are we extending the so called maxEntry border?
                        blocking.append(prevBlocking[-1])
                        maxEntry = prevMaxEntry
                        continue
                    elif xp in prevBlocking:
                        continue

                if direction == 0: # North:
                    pos = [position[0] - xp, position[1] - yp, position[2]] # Our new position
                    
                elif direction == 1: # East
                    pos = [position[0] + yp, position[1] + xp, position[2]] # Our new position
                    
                elif direction == 2: # South
                    pos = [position[0] + xp, position[1] + yp, position[2]] # Our new position
                    
                elif direction == 3: # West
                    pos = [position[0] - yp, position[1] - xp, position[2]] # Our new position
                    
                if xp > maxEntry: # Determin this as our new min/max
                    maxEntry = xp
                elif xp < minEntry:
                    minEntry = xp
                    
                tile = game.map.getTile(pos)
                if not tile:
                    blocking.append(xp)
                    continue
                    
                ret = 0
                for item in tile.getItems():
                    if item.blockprojectile:
                        blocking.append(xp)
                        ret = 1
                        break
                    
                if not ret:
                    positions.append(pos)


            count = len(yo)
            
            if count and count == len(blocking): # 100% blocking, it basicly means we're done
                return positions
                
            prevBlocking = blocking[:]
            blocking = [] # New blocking, from this level
            prevMaxEntry = maxEntry
            prevMinEntry = minEntry
            yp += 1
                    
    elif area[0] == game.enum.TARGET_CASTER_AREA:
        for a in area[1:]:
            x = position[0] - a[0]
            y = position[1] - a[1]
           
            positions.append([x,y, position[2]])
                  

    return positions
    
def typeToEffect(type):
    if type == "fire":
        return (game.enum.EFFECT_HITBYFIRE, game.enum.ANIMATION_FIRE)
    elif type == "poison":
        return (game.enum.EFFECT_HITBYPOISON, game.enum.ANIMATION_POISON)
  
"""def makeField(fieldId, hiteffect=None):
    def make(position, **k):
        item = game.item.Item(fieldId)
        
        def effectOverTime(creature, damage, perTime, effect, forTicks, ticks=0):
            if not creature.alive:
                return
                
            ticks += 1
            creature.modifyHealth(-damage)
            creature.magicEffect(creature.position, effect)
            
            
            if ticks < forTicks:
                game.engine.safeCallLater(perTime, effectOverTime, creature, damage, perTime, effect, forTicks, ticks)
                
        def callback(creature, thing, **k):
            if thing.damage:
                creature.magicEffect(creature.position, typeToEffect(thing.field)[0])
                creature.modifyHealth(-thing.damage)
                
            if thing.turns:
                effectOverTime(creature, thing.damage, thing.ticks / 1000, typeToEffect(thing.field)[1], thing.turns)
        
        stackpos = game.engine.placeItem(item, position)
        
        if hiteffect:
            game.engine.magicEffect(hiteffect)
            
        if item.damage:
            game.scriptsystem.reg('walkOn', item, callback)
            if item.duration:
                item.decay(position, callback=lambda i: game.scriptsystem.reg('walkOn', i, callback))
                
    return make

def damageTarget(mlvlMin, mlvlMax, constantMin, constantMax, type, lvlMin=5, lvlMax=5, hiteffect=None):
    def callback(creature, position, onCreature, onPosition, effect, strength):
        creature.shoot(position, onPosition, effect)
        if strength:
            minDmg, maxDmg = strength
            
        else:    
            maxDmg = -(creature.data["level"]/lvlMax)+(creature.data["maglevel"]*mlvlMax)+constantMax
            minDmg = -(creature.data["level"]/lvlMin)+(creature.data["maglevel"]*mlvlMin)+constantMin
        dmg = random.randint(round(minDmg), round(maxDmg))
        
        if hiteffect:
            onCreature.magicEffect(hiteffect)
            
            
        onCreature.modifyHealth(dmg)
        
        onCreature.onHit(creature, dmg, type)
        onCreature.lastDamager = creature
        
    return callback
    
def healTarget(mlvlMin, mlvlMax, constantMin, constantMax, lvlMin=5, lvlMax=5, hiteffect=None):
    def callback(creature, position, onCreature, onPosition, effect, strength):
        creature.shoot(position, onPosition, effect)
        if strength:
            minHP, maxHP = strength
            
        else:
            maxHP = (creature.data["level"]/lvlMax)+(creature.data["maglevel"]*mlvlMax)+constantMax
            minHP = (creature.data["level"]/lvlMin)+(creature.data["maglevel"]*mlvlMin)+constantMin

        if hiteffect:
            onCreature.magicEffect(hiteffect)
            
        onCreature.modifyHealth(random.randint(round(minHP), round(maxHP)))
    return callback

def drainHealthTarget(effectivityLevel=1, hiteffect=None):
    def callback(creature, position, onCreature, onPosition, effect, strength):
        creature.shoot(position, onPosition, effect)
        if strength:
            minHP, maxHP = strength
        else:
            return
            
        health = random.randint(round(minHP), round(maxHP))
        if hiteffect:
            onCreature.magicEffect(hiteffect)
            
        onCreature.modifyHealth(health)
        creature.modifyHealth(health * effectivityLevel)
    return callback

def drainManaTarget(hiteffect=None):
    def callback(creature, position, onCreature, onPosition, effect, strength):
        creature.shoot(position, onPosition, effect)
        if strength:
            minMana, maxMana = strength
            
        else:
            return

        if hiteffect:
            onCreature.magicEffect(hiteffect)
            
        onCreature.modifyMana(random.randint(round(minMana), round(maxMana)))
    return callback
    
def boostTarget(type, length, formula, subtype="", hiteffect=None):
    def callback(creature, position, onCreature, onPosition, effect, strength):
        creature.shoot(position, onPosition, effect)
        if strength:
            mod = random.randint(strength[0], strength[1])
            try:
                length = strength[2]
            except:
                pass
        else:
            org = getattr(onCreature, type)
            mod = formula(org) - org
        
        if hiteffect:
            onCreature.magicEffect(hiteffect)
            
        onCreature.condition(game.creature.Boost(type, mod, length, subtype), game.enum.CONDITION_REPLACE)
        
    return callback
            
def conditionTarget(*argc, **kwargs):
    def callback(creature, position, onCreature, onPosition, effect, strength):
        creature.shoot(position, onPosition, effect)
        if strength:
            import copy
            condition = copy.deepcopy(strength)
        else:
            condition = game.creature.Condition(*argc, **kwargs)
        if "hiteffect" in kwargs:
            onCreature.magicEffect(kwargs["hiteffect"])
            del kwargs["hiteffect"]
            
        stack = CONDITION_ADD
        if "stack" in kwargs:
            stack = kwargs["stack"]
            del kwargs["stack"]
        onCreature.condition(condition, stack)
        
    return callback

def multi(*callbacks):
    def callback(creature, position, onCreature, onPosition, effect, strength):
        for call in callbacks:
            call(creature, position, onCreature, onPosition, effect, strength)
            
def damageArea(mlvlMin, mlvlMax, constantMin, constantMax, type, lvlMin=5, lvlMax=5, hiteffect=None):
    def callback(creature, position, effect, strength):       
        creature.magicEffect(position, effect)
        
        if strength:
            minDmg, maxDmg = strength
            
        else:
            maxDmg = round(-(creature.data["level"]/lvlMax)+(creature.data["maglevel"]*mlvlMax)+constantMax)
            minDmg = round(-(creature.data["level"]/lvlMin)+(creature.data["maglevel"]*mlvlMin)+constantMin)
            
        creatures = game.map.getTile(position).creatures()
        if creatures:
            for onCreature in creatures:
                dmg = round(random.randint(minDmg, maxDmg))
                
                if hiteffect:
                    onCreature.magicEffect(hiteffect)
                    
                onCreature.onHit(creature, -dmg, type)
                onCreature.lastDamager = creature
        
    return callback


def conjureRune(words, make, icon, mana=0, level=0, mlevel=0, soul=1, vocations=None, use=2260, useCount=1, makeCount=1, teached=0, group=3, cooldown=2):
    @game.creature.Creature.actionDecor
    def conjure(creature, text):
        if not creature.canDoSpell(icon, group):
            creature.exhausted()
            return False
            
        # Checks
        if creature.data["level"] < level:
            creature.notEnough("level")
        elif creature.data["mana"] < mana:
            creature.notEnough("mana")
        elif creature.data["soul"] < soul:
            creature.notEnough("soul")
        elif creature.data["maglevel"] < mlevel:
            creature.notEnough("magic level")
        elif vocation and not creature.data["vocation"] in vocation:
            creature.notPossible()
        else:
            useItem = creature.findItemById(use, useCount)
                
            if not useItem:
                creature.needMagicItem()
                creature.magicEffect(creature.position, game.enum.EFFECT_POFF)
                
            else:
                item = game.item.Item(make,makeCount)

                ret = creature.itemToUse(item)
                if not ret:
                    creature.notEnoughRoom()
                
                if mana:
                    creature.modifyMana(-mana)
                if soul:
                    creature.modifySoul(-soul)
                creature.cooldownSpell(icon, group, cooldown)
                creature.message("Made %dx%s" % (makeCount, item.rawName()))
                creature.magicEffect(creature.position, game.enum.EFFECT_MAGIC_RED)
    if game.item.items[make]["name"].title() in spells:
        print "Warning: Duplicate spell with name %s" % name
    spells[words] = (conjure, game.item.items[make]["name"].title(), level, mana)
    game.scriptsystem.get("talkaction").reg(words, conjure)
    
def fieldRune(rune, level, mlevel, icon, group, area, callback, cooldown=2, useCount=1):
    @game.creature.Creature.actionDecor
    def fieldrune(creature, position, thing, stackpos, onPosition, **k):
        if creature.isPlayer():
            if not creature.canDoSpell(icon, group):
                creature.exhausted()
                return False
                
            if creature.data["level"] < level:
                creature.notEnough("level")
            elif creature.data["maglevel"] < mlevel:
                creature.notEnough("magic level")
                
            else:
                if not thing.count:
                    creature.needMagicItem()
                    creature.magicEffect(creature.position, game.enum.EFFECT_POFF)
                    
                else:
                    creature.modifyItem(thing, position, stackpos, -useCount)
                    
                    creature.cooldownSpell(icon, group, cooldown)
                    for a in area:
                        pos = onPosition[:]
                        pos[0] += a[0]
                        pos[1] += a[1]
                        callback(pos)
        else:
            for a in area:
                pos = onPosition[:]
                pos[0] += a[0]
                pos[1] += a[1]
                callback(pos)
                
    fieldRunes[rune] = fieldrune # Just to prevent reset
    game.scriptsystem.get("useWith").reg(rune, fieldrune)

def targetRune(rune, level, mlevel, icon, group, effect, callback, cooldown=2, useCount=1):
    @game.creature.Creature.actionDecor
    def targetrune(creature, thing, position, onPosition, stackpos, onStackpos, **k):
        if creature.isPlayer():
            if not creature.canDoSpell(icon, group):
                creature.exhausted()
                return False
                
            if creature.data["level"] < level:
                creature.notEnough("level")
            elif creature.data["maglevel"] < mlevel:
                creature.notEnough("magic level")
                
            else:
                if not thing.count:
                    creature.needMagicItem()
                    creature.magicEffect(creature.position, game.enum.EFFECT_POFF)
                    
                else:
                    creature.modifyItem(thing, position, stackpos, -useCount)
                        
                    creature.cooldownSpell(icon, group, cooldown)
                    try:
                        onCreature = game.map.getTile(onPosition).getThing(onStackpos)
                        onCreature.isPlayer()
                    except:
                        creature.onlyOnCreatures()
                    else:
                        callback(creature, creature.position, onCreature, onPosition, effect, None)
        else:
            # Monster is doing it.
            callback(creature, creature.position, creature.target, onPosition, effect, k["strength"])
            
    targetRunes[rune] = targetrune # Just to prevent reset
    game.scriptsystem.get("useWith").reg(rune, targetrune)

def selfTargetSpell(words, name, icon, level, mana, group, effect, callback, cooldown=1, groupCooldown=None):
    @game.creature.Creature.actionDecor
    def selftargetspell(creature, strength=None, target=None, **k):
        if creature.isPlayer():
            if not creature.canDoSpell(icon, group):
                creature.exhausted()
                return False
                    
            if creature.data["level"] < level:
                creature.notEnough("level")
                return False
                
            elif creature.data["mana"] < mana:
                creature.notEnough("mana")
                return False
            if not target:
                target = creature
                
            creature.modifyMana(-mana)
            creature.cooldownSpell(icon, group, cooldown, groupCooldown)
        callback(creature, creature.position, target, target.position, effect, strength)
            
    spells[name] = (selftargetspell, words, level, mana)
    if words:
        game.scriptsystem.reg("talkaction", words, selftargetspell)

def creatureSelfTargetSpell(name, effect, callback):
    @game.creature.Creature.actionDecor
    def targetspell(creature, strength=None, target=None, **k):
        if not target:
            target = creature
                
        callback(creature, creature.position, target, target.position, effect, strength)
            
    spells[name] = (targetspell)
def areaSpell(words, name, icon, level, mana, group, effect, area, callback, cooldown=2, groupCooldown=None):
    @game.creature.Creature.actionDecor
    def areaspell(creature, strength=None, direction=None, **k):
        if creature.isPlayer():
            if not creature.canDoSpell(icon, group):
                creature.exhausted()
                return False
                    
            if creature.data["level"] < level:
                creature.notEnough("level")
                return False
                
            elif creature.data["mana"] < mana:
                creature.notEnough("mana")
                return False
            
            creature.modifyMana(-mana)
            creature.cooldownSpell(icon, group, cooldown, groupCooldown)
            
        positions = calculateAreaDirection(creature.position, creature.direction, area)
        for pos in positions:
            callback(creature, pos, effect, strength)
            
    spells[name] = (areaspell, words, level, mana)
    if words:
        game.scriptsystem.reg("talkaction", words, targetspell)

def creatureAreaSpell(name, effect, area, callback):
    @game.creature.Creature.actionDecor
    def areaspell(creature, strength=None, direction=None, **k):
        for pos in calculateAreaDirection(creature.position, creature.direction, area):
            callback(creature, pos, effect, strength)
            
    spells[name] = (areaspell)
  
def targetSpell(words, name, icon, level, mana, group, effect, callback, cooldown=2, groupCooldown=None):
    @game.creature.Creature.actionDecor
    def targetspell(creature, strength=None, target=None, **k):
        if creature.isPlayer():
            if not creature.canDoSpell(icon, group):
                creature.exhausted()
                return False
                    
            if creature.data["level"] < level:
                creature.notEnough("level")
                return False
                
            elif creature.data["mana"] < mana:
                creature.notEnough("mana")
                return False
            
            creature.modifyMana(-mana)
            creature.cooldownSpell(icon, group, cooldown, groupCooldown)
        if not target:
            target = creature.target
            if not target:
                return
                
        callback(creature, creature.position, target, target.position, effect, strength)
            
    spells[name] = (targetspell, words, level, mana)
    if words:
        game.scriptsystem.reg("talkaction", words, targetspell)

def creatureTargetSpell(name, effect, callback):
    @game.creature.Creature.actionDecor
    def targetspell(creature, strength=None, target=None, **k):
        if not target:
            target = creature.target
            if not target:
                return
                
        callback(creature, creature.position, target, target.position, effect, strength)
            
    spells[name] = (targetspell)"""

def clear():
    fieldRunes.clear()
    targetRunes.clear()
    spells.clear()
    
    
    
### The new way ###

def damage(mlvlMin, mlvlMax, constantMin, constantMax, type=game.enum.MELEE, lvlMin=5, lvlMax=5):
    def damageCallback(caster, target, strength=None):  
        if strength:
            dmg = random.randint(strength[0], strength[1])
        else:
            maxDmg = round(-(caster.data["level"]/lvlMax)+(caster.data["maglevel"]*mlvlMax)+constantMax)
            minDmg = round(-(caster.data["level"]/lvlMin)+(caster.data["maglevel"]*mlvlMin)+constantMin)
            dmg = random.randint(minDmg, maxDmg)
        

        target.modifyHealth(dmg)
        
        target.onHit(caster, dmg, type)
        target.lastDamager = caster
        
    return damageCallback
    
def heal(mlvlMin, mlvlMax, constantMin, constantMax, lvlMin=5, lvlMax=5):
    def healCallback(caster, target, strength=None):
        if strength:
            minDmg, maxDmg = strength
        else:
            maxDmg = round((caster.data["level"]/lvlMax)+(caster.data["maglevel"]*mlvlMax)+constantMax)
            minDmg = round((caster.data["level"]/lvlMin)+(caster.data["maglevel"]*mlvlMin)+constantMin)
        

        target.modifyHealth(random.randint(minDmg, maxDmg))
        
    return healCallback

def conjure(make, count=1, **kwargs):
    def conjureCallback(caster, target, strength=None):
        if target.isPlayer():
            item = game.item.Item(make, count, **kwargs)

            ret = target.itemToUse(item)
            if not ret:
                return target.notEnoughRoom()
                
            target.message("Made %dx%s" % (count, item.rawName()))
            
    return conjureCallback

def field(fieldId):
    def makeFieldCallback(position, **k):
        item = game.item.Item(fieldId)
        
        def effectOverTime(creature, damage, perTime, effect, forTicks, ticks=0):
            if not creature.alive:
                return
                
            ticks += 1
            creature.modifyHealth(-damage)
            creature.magicEffect(creature.position, effect)
            
            
            if ticks < forTicks:
                game.engine.safeCallLater(perTime, effectOverTime, creature, damage, perTime, effect, forTicks, ticks)
                
        def callback(creature, thing, **k):
            if thing.damage:
                creature.magicEffect(creature.position, typeToEffect(thing.field)[0])
                creature.modifyHealth(-thing.damage)
                
            if thing.turns:
                effectOverTime(creature, thing.damage, thing.ticks / 1000, typeToEffect(thing.field)[1], thing.turns)
        
        stackpos = game.engine.placeItem(item, position)
            
        if item.damage:
            game.scriptsystem.reg('walkOn', item, callback)
            if item.duration:
                item.decay(position, callback=lambda i: game.scriptsystem.reg('walkOn', i, callback))
                
    return makeFieldCallback
    
class Spell(object):
    def __init__(self, name, words=None, icon=0, target=game.enum.TARGET_TARGET, group=game.enum.ATTACK_GROUP):
        self.name = name
        self.words = words
        self.targetType = target
        
        self.vocations = None
        
        self.castEffect = None
        self._targetEffect = None
        self.shootEffect = None
        self.areaEffect = None
        
        self.targetRange = 1
        
        self.targetArea = None
        
        self.effectOnCaster = []
        self.effectOnTarget = []
        self.conditionOnCaster = []
        self.conditionOnTarget = []
        
        self.icon = icon
        self.group = group
        
        self.learned = False
        
        self._requireGreater = []
        self._requireLess = []
        self._requireCallback = []
        
        self.cooldown = 2
        self.groupCooldown = 2

        func = self.doEffect()
        def l():
            try:
                mana = self._requireGreater["mana"]
            except:
                mana = 0
                
            try:
                level = self._requireGreater["level"]
            except:
                level = 0
                
            spells[name] = (func, words, level, mana)
        
        # Delay the input a little.
        game.engine.safeCallLater(0.1, l)
        
        if words:
            game.scriptsystem.reg("talkaction", words, func)
            
    def effects(self, caster=None, shoot=None, target=None, area=None):
        self.castEffect = caster
        self.shootEffect = shoot
        self._targetEffect = target
        self.areaEffect = area
        
    def area(self, area):
        self.targetArea = area
        
    def casterEffect(self, mana=0, health=0, soul=0, callback=None):
        if mana or health:
            def _effect(caster, target, **k):
                # Target = caster
                if health:
                    target.modifyHealth(health)
                if mana:
                    target.modifyMana(mana)
                if soul:
                    target.modifySoul(soul)
                    
            self.effectOnCaster.append(_effect)
            
        if callback:
            self.effectOnCaster.append(callback)
            
    def targetEffect(self, mana=0, health=0, soul=0, callback=None):
        if mana or health:
            def _effect(target, caster, **k):
                # Target = actual target
                if health:
                    if health < 0:
                        target.lastDamager = caster
                    target.modifyHealth(health)
                if mana:
                    target.modifyMana(mana)
                    
                if soul:
                    target.modifySoul(soul)
                    
            self.effectOnTarget.append(_effect)
            
        if callback:
            self.effectOnTarget.append(callback)
            
    def casterCondition(self, *argc, **kwargs):
        try:
            stack = kwargs['stackbehavior']
        except:
            stack = CONDITION_LATER
            
        for con in argc:
            self.conditionOnCaster.append((con, stack))

    def targetCondition(self, *argc, **kwargs):
        try:
            stack = kwargs['stackbehavior']
        except:
            stack = CONDITION_LATER
            
        for con in argc:
            self.conditionOnTarget.append((con, stack))
   
    def require(self, learned=False, vocations=None, **kwargs):
        self._requireGreater = kwargs
        self.vocations = vocations
        self.learned = learned
   
    def requireLess(self, **kwargs):
        self._requireLess = kwargs

    def requireCallback(self, *args):
        self._requireCallback.extend(args)

    def use(self, itemId=2260, count=1):
        def check(caster):
            useItem = caster.findItemById(itemId, count)
                
            if not useItem:
                caster.needMagicItem()
                caster.magicEffect(game.enum.EFFECT_POFF)
                return False
                
            return True
            
        self._requireCallback.append(check)
    
    def cooldowns(self, cooldown=0, groupCooldown=None):
        if cooldown and groupCooldown == None:
            groupCooldown = cooldown
           
        self.cooldown = cooldown
        self.groupCooldown = groupCooldown
       
    def doEffect(self, ):
        # Stupid weakrefs can't deal with me directly since i can't be a strong ref. Yeye, I'll just cheat and wrap myself!
        def spellCallback(creature, strength=None, **k):
            if creature.isPlayer():
                if not creature.canDoSpell(self.icon, self.group):
                    creature.exhausted()
                    return False
                
                if self.learned and not creature.canUseSpell(self.name):
                    return creature.cancelMessage("You need to learn this spell first.")
                    
                if self.vocations and creature.getVocationId() not in self.vocations:
                    return creature.cancelMessage("Your vocation cannot use this spell.")
                    
                if self._requireGreater:
                    for var in self._requireGreater:
                        if creature.data[var] < self._requireGreater[var]:
                            creature.notEnough(var)
                            return False
                            
                if self._requireLess:
                    for var in self._requireLess:
                        if creature.data[var] > self._requireLess[var]:
                            creature.message("Your %s is too high!" % var)
                            return False
                
                if self._requireCallback:
                    for call in self._requireCallback:
                        if not call(caster=creature): return
                        
                # Integrate mana seeker
                try:
                    creature.modifyMana(-self._requireGreater["mana"])
                except:
                    pass

                # Integrate soul seeker
                try:
                    creature.modifyMana(-self._requireGreater["soul"])
                except:
                    pass
                
                creature.cooldownSpell(self.icon, self.group, self.cooldown, self.groupCooldown)
                
            target = creature
            if self.targetType == TARGET_TARGET:
                target = creature.target
                if not target:
                    return
                    
            if self.castEffect:
                creature.magicEffect(self.castEffect)
            
            for call in self.effectOnCaster:
                call(caster=creature, target=creature, strength=strength)
            
            for array in self.conditionOnCaster:
                creature.condition(array[0].copy(), array[1])
                
            if self.targetType == TARGET_TARGET and target and self.shootEffect:
                creature.shoot(creature.position, target.position, self.shootEffect)
                
            if not self.targetType == TARGET_AREA:
                for call in self.effectOnTarget:
                    call(target=target, caster=creature, strength=strength)
                
                if self._targetEffect:
                    target.magicEffect(self._targetEffect)
                    
                for array in self.conditionOnTarget:
                    target.condition(array[0].copy(), array[1])

            if self.targetType == TARGET_AREA:
                positions = calculateAreaDirection(creature.position, creature.direction, self.targetArea)
                targets = []
                for pos in positions:
                    if self.areaEffect:
                        creature.magicEffect(self.areaEffect, pos)
                        
                    creatures = game.map.getTile(pos).creatures()
                    if creatures:
                        targets.extend(creatures)
                        
                
                for targ in targets:
                    if self._targetEffect:
                        targ.magicEffect(self._targetEffect)
                        
                    for call in self.effectOnTarget:
                        call(target=targ, caster=creature, strength=strength)
                        
        return spellCallback
        
        
class Rune(Spell):
    def __init__(self, rune, icon=0, count=1, target=game.enum.TARGET_TARGET, group=game.enum.ATTACK_GROUP):
        self.rune = rune
        self.targetType = target
        self.count = count
        
        self.vocations = None
        
        self.castEffect = None
        self._targetEffect = None
        self.shootEffect = None
        self.areaEffect = None
        
        self.targetRange = 1
        
        self.targetArea = None
        
        self.effectOnCaster = []
        self.effectOnTarget = []
        self.conditionOnCaster = []
        self.conditionOnTarget = []
        
        self.icon = icon
        self.group = group
        
        self.learned = False
        
        self._requireGreater = []
        self._requireLess = []
        self._requireCallback = []
        
        self.cooldown = 2
        self.groupCooldown = 2

        func = self.doEffect()
        targetRunes[rune] = func # Just to prevent reset
        game.scriptsystem.get("useWith").reg(rune, func)
        
    def doEffect(self):
        # Stupid weakrefs can't deal with me directly since i can't be a strong ref. Yeye, I'll just cheat and wrap myself!
        def runeCallback(thing, creature, position, stackpos, onPosition, onStackpos, onThing, strength=None, **k):
            print "called!"
            if creature.isPlayer():
                if not creature.canDoSpell(self.icon, self.group):
                    creature.exhausted()
                    return False

                if self.learned and not creature.canUseSpell(self.name):
                    return creature.cancelMessage("You need to learn this spell first.")
                    
                if self.vocations and creature.getVocationId() not in self.vocations:
                    return creature.cancelMessage("Your vocation cannot use this spell.")
                    
                if self._requireGreater:
                    for var in self._requireGreater:
                        if creature.data[var] < self._requireGreater[var]:
                            creature.notEnough(var)
                            return False
                            
                if self._requireLess:
                    for var in self._requireLess:
                        if creature.data[var] > self._requireLess[var]:
                            creature.message("Your %s is too high!" % var)
                            return False
                
                if self._requireCallback:
                    for call in self._requireCallback:
                        if not call(caster=creature): return

                if not thing.count:
                    creature.needMagicItem()
                    creature.magicEffect(creature.position, game.enum.EFFECT_POFF)
                        
                else:
                    
                    if self.targetType == game.enum.TARGET_TARGET:
                        try:
                            #onCreature = game.map.getTile(onPosition).getThing(onStackpos)
                            onCreature = onThing
                            onCreature.isPlayer()
                        except:
                            return creature.onlyOnCreatures()
                        
                    creature.modifyItem(thing, position, stackpos, -self.count)  
                    
                    # Integrate mana seeker
                    try:
                        creature.modifyMana(-self._requireGreater["mana"])
                    except:
                        pass

                    # Integrate soul seeker
                    try:
                        creature.modifyMana(-self._requireGreater["soul"])
                    except:
                        pass
                    
                    creature.cooldownSpell(self.icon, self.group, self.cooldown, self.groupCooldown)
                
            target = creature
            if self.targetType == TARGET_TARGET:
                target = onCreature
                if not target:
                    return
                    
            if self.castEffect:
                creature.magicEffect(self.castEffect)
            
            for call in self.effectOnCaster:
                call(caster=creature, target=creature, strength=strength)
            
            for array in self.conditionOnCaster:
                creature.condition(array[0].copy(), array[1])
                
            if self.targetType == TARGET_TARGET and self.shootEffect:
                creature.shoot(creature.position, target.position, self.shootEffect)
                
            if not self.targetType == TARGET_AREA:
                for call in self.effectOnTarget:
                    call(target=target, caster=creature, strength=strength)
                
                if self._targetEffect:
                    target.magicEffect(self._targetEffect)
                    
                for array in self.conditionOnTarget:
                    target.condition(array[0].copy(), array[1])
        
            else:
                for call in self.effectOnTarget:
                    call(target=None, caster=creature, strength=strength, position=onPosition)
                if self._targetEffect:
                    caster.magicEffect(self._targetEffect, onPosition)
                    
        if config.runeCastDelay:
            def castDelay(**k):
                game.engine.safeCallLater(config.runeCastDelay, runeCallback, **k)
                
            return castDelay
            
        return runeCallback