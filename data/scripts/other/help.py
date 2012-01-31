def callback(creature, text):
    creature.message("No you!!")
    
def repeater(creature, text):
    creature.message(text)
    
def teleporter(creature, text):
    x,y,z = text.split(',')
    try:
        creature.teleport(Position(int(x),int(y),int(z)))
    except:
        creature.message("Can't teleport to solid tiles!")
    else:
        creature.message("Welcome to %s" % text)
    
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
            creature.message("Item not found!")
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
def tilerE(creature, text):
    global last
    last += 1
    return tiler(creature, str(last))
    
def mypos(creature, text):
    creature.message("Your position is: "+str(creature.position))
    print creature.position.getTile()
    if isinstance(creature.position.getTile(), game.map.HouseTile):
        print creature.position.getTile().houseId
    print str(creature.position) # Print to console to be sure
reg("talkaction", "help", callback)
reg("talkactionFirstWord", 'rep', repeater)
reg("talkactionFirstWord", 'teleport', teleporter)
reg("talkactionFirstWord", 'set', tiler)
reg("talkaction", 't', tilerE)
reg("talkaction", 'mypos', mypos)
def speedsetter(creature, text):
    try:
        creature.setSpeed(int(text))
    except:
        creature.message("Invalid speed!")
reg("talkactionFirstWord", 'speed', speedsetter)



# First use of actions :p
def testContainer(creature, thing, position, index):
    if thing.owners and creature not in thing.owners: # Prevent people to open owned things
        return
    if thing.openIndex == None:
        # Open a bag inside a bag?
        open = True
        bagFound = creature.getContainer(index)    
            
        if bagFound:
            # Virtual close
            del creature.openContainers[index].openIndex
                
            # Virtual switch
            thing.openIndex = index
            thing.parent = creature.openContainers[index]
                
            # Update the container
            creature.updateContainer(thing, parent=1)
            open = False
            ok = True
            
        if open:
            # Open a new one
            parent = 0

            if position.x == 0xFFFF and position.y >= 64:
                parent = 1
                thing.parent = creature.openContainers[position.z-64]
            ok = creature.openContainer(thing, parent=parent)

        # Opened from ground, close it on next step :)
        if ok and position.x != 0xFFFF:
            def _vertifyClose(who):
                if thing.openIndex != None:
                    if not who.inRange(position, 1, 1):
                        who.closeContainer(thing)
                    else:
                        who.scripts["onNextStep"].append(_vertifyClose)
                    
            creature.scripts["onNextStep"].insert(0, _vertifyClose)
    else:
        creature.closeContainer(thing)
_script_ = game.scriptsystem.get("use")

for item in game.item.items:
    if item and "containerSize" in item:
        _script_.reg(game.item.reverseItems[item["cid"]], testContainer)

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
                creature.addItem(newitem)
                count -= rcount
        else:
            raise
    #except:
    #    creature.message("Invalid Item!")
         
    return False

reg("talkactionFirstWord", 'i', makeitem)


# Reimport tester
def reimporter(creature, text):
    game.scriptsystem.reimporter()
    return False

def saySomething(creature, text):
    creature.say("Test 1")
    return False
    
reg("talkaction", 'reload', reimporter)
reg("talkaction", 'reloadtest', saySomething)

# Tester of container functions
def popItems(creature, text):
    i,c = map(int, text.split(" "))
    item = creature.findItemById(i,c)
    return False
    
reg("talkactionFirstWord", 'pop', popItems)

# Experience tester
def modexp(creature, text):
    exp = int(text)
    creature.modifyExperience(exp)
    return False
    
reg("talkactionFirstWord", 'exp', modexp)

# Creature tester
def creatureSpawn(creature, text):
    print "Spawner called"
    pos = creature.position.copy()
    pos.y += 2
    try:
        game.monster.getMonster(text).spawn(pos)
    except:
        creature.message("Monster named '%s' can't be spawned!" % text)
    return False
    
reg("talkactionFirstWord", 's', creatureSpawn)

# NPC tester
def npcSpawn(creature, text):
    print "Spawner called"
    pos = creature.position.copy()
    pos.y += 2
    try:
        game.npc.getNPC(text).spawn(pos)
    except:
        creature.message("NPC named '%s' can't be spawned!" % text)
    return False
    
reg("talkactionFirstWord", 'n', npcSpawn)

def saveMe(creature, text):
    creature.save()
    return False
    
reg("talkaction", 'saveme', saveMe)

def saveAll(creature, text):
    engine.saveAll()
    return False
    
reg("talkaction", 'saveall', saveAll)

def spawnDepot(creature, text):
    depotId = int(text)
    box = game.item.Item(2594, depotId=depotId)
    position = creature.positionInDirection(creature.direction)
    tile = game.map.getTile(position)
    tile.placeItem(box)
    game.engine.updateTile(position, tile)
    
reg('talkactionFirstWord', 'depot', spawnDepot)

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
        creature.message("No scripts what so ever on %s" % text)

reg('talkactionFirstWord', 'track', trackScripts)

def mountPlayer(creature, text):
    if not config.allowMounts:
        return
        
    if text and text != "!mount":
        try:
            if creature.canUseMount(text):
                creature.mount = game.resource.getMount(text).cid
        except:
            creature.message("Invalid mount.")
            
    elif not creature.mount:
        creature.message("You have no mount.")
    else:
        status = not creature.mounted
        creature.changeMountStatus(status)
        
        if status:
            creature.message("You're now mounted.")
        else:
            creature.message("You're now unmouned.")
        
    return False
reg('talkactionFirstWord', '!mount', mountPlayer)
reg('talkaction', '!mount', mountPlayer)

def addMount(creature, text):
    try:
        creature.addMount(text)
        creature.message("You can now use %s" % text)
    except:
        creature.message("Invalid mount.")
    return False

reg('talkactionFirstWord', 'mount', addMount)

def addOutfit(creature, text):
    try:
        creature.addOutfit(text)
        creature.message("You can now use %s" % text)
    except:
        creature.message("Invalid outfit.")
    return False

reg('talkactionFirstWord', 'outfit', addOutfit)

def testrename(creature, thing, **k):
    thing.privRename(creature, "[Seen] Wolf")
    return False
    
reg("lookAt", "Wolf", testrename)

def testsummon(creature,**k):
    tiger = game.monster.getMonster("Tiger").spawn(creature.positionInDirection(creature.direction), spawnDelay=0)
    tiger.setMaster(creature)
    return False
    
reg("talkaction", "summon tiger", testsummon)

def setowner(creature,text):
    id = int(text)
    game.house.houseData[id].owner = creature.data["id"]
    return False
    
    
reg("talkactionFirstWord", "setowner", setowner)

def poisonme(creature, **k):
    creature.condition(Condition(CONDITION_POISON, 0, 10, damage=10))
    print "Condition state (POISON): %d" % creature.hasCondition(CONDITION_POISON)
    
reg("talkaction", "poisonme", poisonme)

def conditionme(creature, **k):
    creature.multiCondition(Condition(CONDITION_POISON, 0, 10, damage=10), Condition(CONDITION_FIRE, 0, 10, damage=10), Condition(CONDITION_POISON, 0, 20, damage=-10))
    
reg("talkaction", "conditionme", conditionme)

def restoreme(creature, **k):
    creature.modifyHealth(10000)
    creature.modifyMana(10000)
    
reg("talkaction", "restore", restoreme)

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
reg("talkactionFirstWord", "info", readData)

def testBoost(creature, **k):
    # Give a +1000 for 20s
    creature.condition(Boost("speed", 1000, 20))
    
    # Give a +1000 to health and maxhealth too for 20s
    creature.condition(Boost(["health", "healthmax"], [1000, 1000], 20))
    
reg("talkaction", "boostme", testBoost)

@inlineCallbacks
def walkRandomStep(creature, callback):
    steps = [0,1,2,3,4,5,6,7]
    
    random.shuffle(steps)
        
    for step in steps:
        d = yield creature.move(step, stopIfLock=True)
        if d == True:
            break
        if d == None:
            later = creature.lastAction - time.time()
            if later > 0:
                callLater(later + 0.1, callback)
                return
            else:
                callLater(0.1, callback)
                return
    callback()
    
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

reg("talkaction", "aime", playerAI)