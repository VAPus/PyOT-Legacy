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
ATTACK_GROUP = 1
HEALING_GROUP = 2
SUPPORT_GROUP=3
SPECIAL_GROUP = 4

AREA_ONE = (0,0),

AREA_WAVE4 = game.enum.TARGET_DIRECTION, (0,), \
            (-1, 0, 1), \
            (-1, 0, 1), \
            (-2, -1, 0, 1, 2)
            
AREA_WAVE5 = game.enum.TARGET_DIRECTION, (0,), \
            (-1, 0, 1), \
            (-2, -1, 0, 1, 2), \
            (-2, -1, 0, 1, 2), \
            (-2, -1, 0, 1, 2), \
             
AREA_BEAM4 = game.enum.TARGET_DIRECTION,(0,), (0,), (0,), (0,)

AREA_BEAM7 = game.enum.TARGET_DIRECTION,(0,), (0,), (0,), (0,), (0,), (0,), (0,)

AREA_CIRCLE = game.enum.TARGET_CASTER_AREA, (-1, 1), (0, -1), (0, 1)

AREA_CIRCLE2 = game.enum.TARGET_CASTER_AREA, (-1, -2), (0, -2), (1, -2), \
               (-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1), \
               (-2, 0), (-1, 0), (1, 0), (2, 0), \
               (-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1), \
               (-1, 2), (0, 2), (1, 2)

AREA_SQUARE = game.enum.TARGET_CASTER_AREA, (-1, -1), (0, -1), (1, -1), \
              (-1, 0), (1, 0), \
              (-1, 1), (0, 1), (1, 1)

AREA_WALL = game.enum.TARGET_DIRECTION, (-2, -1, 1, 2)

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
        
def makeField(fieldId):
    def make(position, **k):
        item = game.item.Item(fieldId)
        
        def effectOverTime(creature, damage, perTime, effect, forTicks, ticks=0):
            if not creature.alive:
                return
                
            ticks += 1
            creature.modifyHealth(-1 * damage)
            creature.magicEffect(creature.position, effect)
            
            
            if ticks < forTicks:
                game.engine.safeCallLater(perTime, effectOverTime, creature, damage, perTime, effect, forTicks, ticks)
                
        def callback(creature, thing, **k):
            if thing.damage:
                creature.magicEffect(creature.position, typeToEffect(thing.field)[0])
                creature.modifyHealth(-1 * thing.damage)
                
            if thing.turns:
                effectOverTime(creature, thing.damage, thing.ticks / 1000, typeToEffect(thing.field)[1], thing.turns)
        
        stackpos = game.engine.placeItem(item, position)
        if item.damage:
            game.scriptsystem.reg('walkOn', item, callback)
            if item.duration:
                item.decay(position, callback=lambda i: game.scriptsystem.reg('walkOn', i, callback))
                
    return make

def damageTarget(mlvlMin, mlvlMax, constantMin, constantMax, type, lvlMin=5, lvlMax=5):
    def callback(creature, position, onCreature, onPosition, effect, strength):
        creature.shoot(position, onPosition, effect)
        if strength:
            minDmg, maxDmg = strength
            
        else:    
            maxDmg = -1 * (creature.data["level"]/lvlMax)+(creature.data["maglevel"]*mlvlMax)+constantMax
            minDmg = -1 * (creature.data["level"]/lvlMin)+(creature.data["maglevel"]*mlvlMin)+constantMin
        dmg = random.randint(round(minDmg), round(maxDmg))
        onCreature.modifyHealth(dmg)
        onCreature.onHit(creature, dmg, type)
        onCreature.lastDamager = creature
        
    return callback
    
def healTarget(mlvlMin, mlvlMax, constantMin, constantMax, lvlMin=5, lvlMax=5):
    def callback(creature, position, onCreature, onPosition, effect, strength):
        creature.shoot(position, onPosition, effect)
        if strength:
            minHP, maxHP = strength
            
        else:
            maxHP = (creature.data["level"]/lvlMax)+(creature.data["maglevel"]*mlvlMax)+constantMax
            minHP = (creature.data["level"]/lvlMin)+(creature.data["maglevel"]*mlvlMin)+constantMin

        onCreature.modifyHealth(random.randint(round(minHP), round(maxHP)))
    return callback

def damageArea(mlvlMin, mlvlMax, constantMin, constantMax, type, lvlMin=5, lvlMax=5):
    def callback(creature, position, effect, strength):       
        creature.magicEffect(position, effect)
        
        if strength:
            minDmg, maxDmg = strength
            
        else:
            maxDmg = round(-1 * (creature.data["level"]/lvlMax)+(creature.data["maglevel"]*mlvlMax)+constantMax)
            minDmg = round(-1 * (creature.data["level"]/lvlMin)+(creature.data["maglevel"]*mlvlMin)+constantMin)
            
        creatures = game.map.getTile(position).creatures()
        if creatures:
            for onCreature in creatures:
                dmg = round(random.randint(minDmg, maxDmg))
                onCreature.onHit(creature, -1 * dmg, type)
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
                    creature.modifyMana(-1 * mana)
                if soul:
                    creature.modifySoul(-1 * soul)
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
                creature.modifyItem(thing, position, stackpos, -1 * useCount)
                
                creature.cooldownSpell(icon, group, cooldown)
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
                creature.modifyItem(thing, position, stackpos, -1 * useCount)
                    
                creature.cooldownSpell(icon, group, cooldown)
                try:
                    onCreature = game.map.getTile(onPosition).getThing(onStackpos)
                    onCreature.isPlayer()
                except:
                    creature.onlyOnCreatures()
                else:
                    callback(creature, creature.position, onCreature, onPosition, effect)
                
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
                
            creature.modifyMana(-1 * mana)
            creature.cooldownSpell(icon, group, cooldown, groupCooldown)
        callback(creature, creature.position, target, target.position, effect, strength)
            
    spells[words] = (selftargetspell, name, level, mana)
    game.scriptsystem.reg("talkaction", words, selftargetspell)
        
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
            
            creature.modifyMana(-1 * mana)
            creature.cooldownSpell(icon, group, cooldown, groupCooldown)
            
        positions = calculateAreaDirection(creature.position, creature.direction, area)
        for pos in positions:
            callback(creature, pos, effect, strength)
            
    spells[words] = (areaspell, name, level, mana)
    game.scriptsystem.reg("talkaction", words, targetspell)

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
            
            creature.modifyMana(-1 * mana)
            creature.cooldownSpell(icon, group, cooldown, groupCooldown)
        if not target:
            target = creature.target
            if not target:
                return
                
        callback(creature, creature.position, target, target.position, effect, strength)
            
    spells[words] = (targetspell, name, level, mana)
    game.scriptsystem.reg("talkaction", words, targetspell)
    
def clear():
    fieldRunes.clear()
    targetRunes.clear()
    spells.clear()