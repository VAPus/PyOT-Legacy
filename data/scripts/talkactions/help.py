@register("talkactionRegex", r'teleport (?P<x>\d+),(?P<y>\d+),(?P<z>\d+)')
@access("TELEPORT")
def teleporter(creature, x, y, z, text):
    try:
        creature.teleport(Position(int(x),int(y),int(z)))
    except:
        creature.lmessage("Can't teleport to solid tiles!")
    else:
        creature.lmessage("Welcome to %s" % text)
        
    return False

@register("talkactionRegex", r'fteleport (?P<x>\d+),(?P<y>\d+),(?P<z>\d+)')
@access("TELEPORT")
def forcedTeleporter(creature, x,y,z, text):
    # Keep in mind that the extra parameters are always strings! You will need to cast them if you intend to use them in functions that require ints.
    try:
        creature.teleport(Position(int(x),int(y),int(z)), force=True)
    except:
        creature.lmessage("Can't teleport to void tiles!")
    else:
        creature.lmessage("Welcome to %s" % text)
        
    return False
        
@register("talkaction", '/up')
@access("TELEPORT")
def up(creature, text):
    up = creature.position.copy()
    up.z -= 1
    try:
            creature.teleport(up)
    except:
            creature.notPossible()
    return False

@register("talkaction", '/down')
@access("TELEPORT")
def down(creature, text):
    up = creature.position.copy()
    up.z += 1
    try:
            creature.teleport(up)
    except:
            creature.notPossible()
    return False

@register("talkactionFirstWord", 'set')
@access("SPAWN")
def tiler(creature, text):
        global last
        if len(text.split(" ")) < 2:
            pos = creature.position
            id = int(text.split(" ")[0])
        else:
            x,y,z = text.split(" ")[0].split(',')
            pos = Position(int(x),int(y),int(z))
            id = int(text.split(" ")[1])
            
        if not id in game.item.items:
            creature.lmessage("Item not found!")
            return False
        item = game.item.Item( id )
        last = id
        pos = Position(pos.x, pos.y-1, pos.z)
        getTile(pos).setThing(0, item)

        game.engine.updateTile(pos, getTile(pos))
        creature.magicEffect(0x03, pos)

        return False
        
global last
last = 0
@register("talkaction", 't')
@access("SPAWN")
def tilerE(creature, text):
    global last
    last += 1
    return tiler(creature, str(last))

@register("talkaction", 'mypos')
def mypos(creature, text):
    creature.lmessage("Your position is: "+str(creature.position))
    print creature.position.getTile()
    if isinstance(creature.position.getTile(), game.map.HouseTile):
        print creature.position.getTile().houseId
    print str(creature.position) # Print to console to be sure

@register("talkactionFirstWord", 'speed')
@access("SPEED")
def speedsetter(creature, text):
    try:
        creature.setSpeed(int(text))
    except:
        creature.lmessage("Invalid speed!")
    return False

@register("talkactionFirstWord", 'i')
@access("CREATEITEM")
def makeitem(creature, text):
    #try:
    if True:    
        count = 1
        if ' ' in text:
            count = int(text.split(" ")[1])
        text = int(text.split(" ")[0])
        if text >= 1000:
            while count:
                rcount = min(100, count)
                newitem = game.item.Item(text, rcount)
                if newitem.pickable:
                    creature.addItem(newitem)
                else:
                    tile = creature.position.getTile()
                    tile.placeItem(newitem)
                    updateTile(creature.position, tile)
                count -= rcount
        else:
            raise
    #except:
    #    creature.message("Invalid Item!")
         
    return False




# Reimport tester
@register("talkaction", 'reload')
@access("RELOAD")
def reimporter(creature, text):
    start = time.time()
    game.scriptsystem.reimporter()
    print "Full reload took: ", (time.time() - start)
    return False
    
# Tester of container functions
@register("talkactionFirstWord", 'pop')
@access("DEVELOPER")
def popItems(creature, text):
    i,c = map(int, text.split(" "))
    item = creature.findItemById(i,c)
    return False
    

# Experience tester
@register("talkactionFirstWord", 'exp')
@access("DEVELOPER")
def modexp(creature, text):
    exp = int(text)
    creature.modifyExperience(exp)
    return False
    

# Creature tester
@register("talkactionFirstWord", 's')
@access("SPAWN")
def creatureSpawn(creature, text):
    print "Spawner called"
    pos = creature.position.copy()
    pos.y += 2
    try:
        game.monster.getMonster(text.title()).spawn(pos)
    except:
        creature.lmessage("Monster named '%s' can't be spawned!" % text)
    return False
    

# NPC tester
@register("talkactionFirstWord", 'n')
@access("SPAWN")
def npcSpawn(creature, text):
    print "Spawner called"
    pos = creature.position.copy()
    pos.y += 2
    try:
        game.npc.getNPC(text.title()).spawn(pos)
    except:
        creature.lmessage("NPC named '%s' can't be spawned!" % text)
    return False
    

@register("talkaction", 'saveme')
@access("SAVEME")
def saveMe(creature, text):
    creature.save()
    return False
    

@register("talkaction", 'saveall')
@access("SAVEALL")
def saveAll(creature, text):
    engine.saveAll()
    return False

@register('talkactionFirstWord', 'depot')
@access("SPAWN")
def spawnDepot(creature, text):
    depotId = int(text)
    box = game.item.Item(2594, depotId=depotId)
    position = creature.positionInDirection(creature.direction)
    tile = game.map.getTile(position)
    tile.placeItem(box)
    game.engine.updateTile(position, tile)
    

@register('talkactionFirstWord', 'track')
@access("DEVELOPER")
def trackScripts(creature, text):
    import inspect
    try:
        text = int(text) # Support ids
    except:
        pass
    
    scripts = []
    for script in scriptsystem.globalScripts:
        if text in scriptsystem.globalScripts[script].scripts:
            for _script in scriptsystem.globalScripts[script].scripts[text]:
                scripts.append((script, inspect.getfile(_script())[2:]))
                
    t = ""
    for script in scripts:
        t += "'%s' event in: '%s'\n" % (script[0], script[1])
    if t:
        creature.windowMessage("===Scripts bound to '%s'===\n%s" % (text, t))
    else:
        creature.lmessage("No scripts what so ever on %s" % text)

@register('talkactionFirstWord', '!mount')
@register('talkaction', '!mount')
def mountPlayer(creature, text):
    if not config.allowMounts:
        return
        
    if text and text != "!mount":
        try:
            if creature.canUseMount(text):
                creature.mount = game.resource.getMount(text).cid
        except:
            creature.lmessage("Invalid mount.")
            
    elif not creature.mount:
        creature.lmessage("You have no mount.")
    else:
        status = not creature.mounted
        creature.changeMountStatus(status)
        
        if status:
            creature.lmessage("You're now mounted.")
        else:
            creature.lmessage("You're now unmouned.")
        
    return False


@register('talkactionFirstWord', 'mount')
@access("DEVELOPER")
def addMount(creature, text):
    try:
        creature.addMount(text.title())
        creature.lmessage("You can now use %s" % text)
    except:
        creature.lmessage("Invalid mount.")
    return False


@register('talkactionFirstWord', 'outfit')
@access("DEVELOPER")
def addOutfit(creature, text):
    try:
        creature.addOutfit(text.title())
        creature.lmessage("You can now use %s" % text)
    except:
        creature.lmessage("Invalid outfit.")
    return False

"""
@register("lookAt", "Wolf")
def testrename(creature, thing, **k):
    thing.privRename(creature, "[Seen] Wolf")
    return False
    


@register("lookAt", "Wolf")
def testhide(creature, thing, **k):
    thing.hideHealth(True)
    thing.refresh()
"""

@register("talkactionFirstWord", "res")
#@access("SPAWN") # Should this have access?
def summon(creature, text):
    try:
        mon = game.monster.getMonster(text)
    except:
        creature.lmessage("Invalid creature.")
    if mon.summonable:
        if creature.data["mana"] > mon.summonable:
            creature.modifyMana(-mon.summonable)
            creature.summon(text, creature.positionInDirection(creature.direction))
        else:
            creature.lmessage("You do not have enough mana.")
    return False

@register("talkactionFirstWord", "setowner")
def setowner(creature,text):
    id = int(text)
    game.house.houseData[id].owner = creature.data["id"]
    return False
    

@register("talkaction", "poisonme")
@access("DEVELOPER")
def poisonme(creature, **k):
    creature.condition(Condition(CONDITION_POISON, 0, 10, damage=10))
    print "Condition state (POISON): %d" % creature.hasCondition(CONDITION_POISON)
    

@register("talkaction", "conditionme")
@access("DEVELOPER")
def conditionme(creature, **k):
    creature.multiCondition(Condition(CONDITION_POISON, 0, 10, damage=10), Condition(CONDITION_FIRE, 0, 10, damage=10), Condition(CONDITION_POISON, 0, 20, damage=-10))
    

@register("talkaction", "restore")
@access("DEVELOPER")
def restoreme(creature, **k):
    creature.modifyHealth(10000)
    creature.modifyMana(10000)
    

@register("talkactionFirstWord", "info")
@access("DEVELOPER")
def readData(creature, text):
    msg = ""
    pos = Position(*map(int, text.split(',')))
    tile = pos.getTile()
    for i in tile.things:
        if isinstance(i, game.creature.Creature):
            msg += "Creature '%s'\n" % i.name()
        elif isinstance(i, game.item.Item):
            msg += "Item '%s'\n" % i.itemId
    creature.windowMessage(msg)        

@register("talkaction", "boostme")
@access("DEVELOPER")
def testBoost(creature, **k):
    # Give a +1000 for 20s
    creature.condition(Boost("speed", 1000, 20))
    
    # Give a +1000 to health and maxhealth too for 20s
    creature.condition(Boost(["health", "healthmax"], [1000, 1000], 20))
    

def walkRandomStep(creature, callback):
    wait = creature.lastAction - time.time()
    if wait > 0:
        callLater(wait*1.5, walkRandomStep, creature, callback) # Twisted have a slight rounding issue <15ms, it shouldn't affect the movement speed.
        return
    steps = [0,1,2,3]
    
    random.shuffle(steps)
    def _callback():
        try:
            creature.move(steps.pop(), stopIfLock=True, callback=callback, failback=_callback)
        except:
            callback()
    creature.move(steps.pop(), stopIfLock=True, callback=callback, failback=_callback)

@register("talkaction", "aime")
@access("DEVELOPER")
def playerAI(creature, **k):
    creature.setSpeed(1500)
    
    def _playerAI():
        if creature.data["health"] < 300:
            creature.modifyHealth(10000)
        
        if random.randint(0, 3) == 1:
            # Try targeting
            for pos in creature.position.roundPoint(1):
                tile = pos.getTile()
                if not tile:
                    continue
                
                for thing in tile.things:
                    if isinstance(thing, game.monster.Monster):
                        creature.target = thing
                        creature.targetMode = 1
                        creature.attackTarget()
                        break
                    elif isinstance(thing, Item) and thing.itemId in (1386, 3678, 5543, 8599):
                        creature.use(pos.setStackpos(tile.findStackpos(thing)), thing)
                        break
            
        walkRandomStep(creature, _playerAI)
        
    _playerAI()

@register("talkaction", "market")
@access("DEVELOPER")
def openMarket(creature, **k):
    creature.openMarket()




@register("talkaction", "forward!")
@access("DEVELOPER")
def moveForward(creature, **k):
    creature.move(creature.direction)
    
@register("talkaction", "immune")
@access("DEVELOPER")
def makeImmune(creature, **k):
    creature.attackable = False
    for monster in game.creature.allCreaturesObject:
        if isinstance(monster, game.monster.Monster) and monster.target == creature:
            monster.target = None
            monster.targetMode = 0
            
@register("talkaction", "kill me now")
@access("DEVELOPER")
def die(creature, **k):
    creature.modifyHealth(-9999999999)
    
@register("talkaction", "8.6 dialog")
@access("DEVELOPER")
def dialog(creature, **k):
    dialogId = creature.dialog("Test", "Hello world?", ["Great", "Not so great"])
    
    def response(button):
        if button == 0:
            creature.say("Yay!")
        else:
            creature.say("Message needs to be about 20% cooler!")
    creature.setWindowHandler(dialogId, response)
    
@register("talkaction", "freeze!")
def delayWalk(creature, **k):
    creature.delayWalk(50)
    creature.lmessage("Ow no, your stuck!")
    callLater(10, lambda: creature.lmessage("You may walk again!"))
    
@register("talkaction", "newinventory")
@access("DEVELOPER")
def newInventory(creature, **k):
    purse = Item(1987)
    purse.name = "Purse"
    purse.addAction('purse')
    creature.inventory = [Item(8820), Item(2125), Item(1987), Item(2463),
                      None, Item(7449), None, None, None,
                      Item(2546,20), purse]

    for item in creature.inventory:
        if not item:
            continue
        weight = item.weight
        if weight:
            creature.inventoryWeight += weight * (item.count or 1)
        try:
            creature.inventoryCache[item.itemId].append(item)
            creature.inventoryCache[item.itemId][0] += item.count or 1
        except:
            creature.inventoryCache[item.itemId] = [item.count or 1, item]
    
    creature.refreshInventory()
    return False