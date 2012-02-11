from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor
import sql
from twisted.python import log
from collections import deque, namedtuple
import game.enum
import bindconstant
import config
import game.engine
import copy
import time
import marshal

try:
    import io # Python 2.7+
    _open = io.open
except:
    _open = open # Less than 2.7
    
items = {}
reverseItems = {}
itemNames = {}

"""if config.itemCache:
    ### Attribute stragegy
    itemAttributes = {}"""

### Container class ###
class Container(object):
    __slots__ = ('items')
    def __init__(self, size):
        self.items = deque(maxlen=size)
    
    def __getstate__(self): # For pickle functions such as jsonpickle
        return self.items
    
    def __setstate__(self, state):
        self.items = state
        
    def placeItem(self, item):
        if len(self.items) < self.items.maxlen:
            self.items.appendleft(item)
            return 0

    def placeItemRecursive(self, item):
        if len(self.items) < self.items.maxlen:
            self.items.appendleft(item)
            return 0
        else:
            for itemX in self.items:
                if itemX.containerSize and itemX.container.placeItemRecursive(item) == 0:
                    return itemX

    def size(self):
        return len(self.items)
        
    def removeItem(self, item):
        return self.items.remove(item)
        
    def getThing(self, pos):
        try:
            return self.items[pos]
        except:
            return None
    
    def getRecursive(self, items = None):
        if items == None:
            items = self.items
            
        for item in items:
            yield item
            if item != self and item.containerSize:
                for i in self.getRecursive(item.container.items):
                    yield i

    def getRecursiveWithBag(self, items = None):
        if not items:
            items = self.items
            
        for pos, item in enumerate(items):
            yield (item, self, pos)
            if item.containerSize:
                for i in self.getRecursiveWithBag(item.container.items):
                    yield i
                    
    def findSlot(self, item):
        return self.items.index(item)

bindconstant.bind_all(Container)
            
### Item ###
class Item(object):
    attributes = ('solid','blockprojectile','blockpath','usable','pickable','movable','stackable','ontop','hangable','rotatable','animation')
    #__slots__ = ('itemId', 'actions', 'teledest', 'description', 'count', 'container', 'text')
    __slots__ = ('itemId', 'actions', 'params')
    
    def __init__(self, itemId, count=1, actions=[], **kwargs):
        try:
            if not items[itemId]:
                raise
        except (KeyError, IndexError):
            print "ItemId %d doesn't exist!" % itemId
            itemId = 100
            
        self.itemId = itemId
        self.actions = actions
        self.actions.append('item')
        
        if kwargs:
            self.params = kwargs
        else:
            self.params = None

        if items[itemId]["a"] & 64:
            self.count = count
            
        # Extend items such as containers
        try:
            self.container = Container(items[itemId]["containerSize"])
        except KeyError:
            pass


    def isPlayer(self):
        return False

    def isNPC(self):
        return False
        
    def isMonster(self):
        return False

    def isItem(self):
        return True
        
    def thingId(self):
        return self.itemId # Used for scripts

    def getsub(self):
        try:
            return self.count
        except:
            try:
                return self.fluidSource
            except:
                return None
                
    def actionIds(self):
        return self.actions
            
    def __getattr__(self, name):
        _loadItem = items[self.itemId]
        try:
            return self.params[name]
        except:
            try:
                return _loadItem["a"] & (1 << self.attributes.index(name))
            except:
                try:
                    return _loadItem[name]
                except:
                    if not "__" in name:
                        return None
                       
        raise AttributeError, name

    def __setattr__(self, name, value):
        if name in self.__slots__:
            return object.__setattr__(self, name, value)
            
        if self.params:
            self.params[name] = value
        else:
            self.params = {name: value}

    def __delattr__(self, name):
        del self.params[name]
        
    def name(self):
        if self.count > 1 and "plural" in items[self.itemId]:
            return str(self.count) + " " + items[self.itemId]["plural"]
        else:
            try:
                return items[self.itemId]["article"] + " " + items[self.itemId]["name"]
            except:
                return items[self.itemId]["name"]
    
    def description(self, player=None, position=None):
        elems = ['elementPhysical', 'elementFire', 'elementIce', 'elementEarth', 'elementDeath', 'elementEnergy', 'elementHoly', 'elementDrown']
        description = "You see %s" % self.name()
        if self.showDuration:
            description += "that will expire in %d seconds" % self.duration # TODO: days, minutes, hours
        if self.containerSize:
            description += " (Vol:%d)" % self.containerSize
        if self.armor: #magiclevelpoints absorbPercentDeath etc...
            description += " (Arm:%d)" % self.armor
        if self.attack or self.defence: ##melee? weapons and shields
            description += " ("
            if self.attack:
                description += "Atk:%d" % self.attack
            moreatk = ""
            for elem in elems:
                value = self.__getattr__(elem)
                if value:
                    pre = elem[len("element"):]
                    moreatk += " +%d %s" % (value, pre.lower())
            if moreatk:
                description += " physical %s" % moreatk
            if self.extraatk:
                description += " +%d" % self.extraatk
            if self.defence:
                if self.attack:
                    description += ", "
                description += "Def:%d" % self.defence
            if self.extradef:
                description += " +%d" % self.extradef
            description += ")" #shows up as a ? for some reason

        descriptio += "."

        ###########################only show weight and special description if distance <2. TODO: use extra below here
        extra = ""
        if player and (not position or player.inRange(position, 2, 2)): # If position ain't set/known, we're usually in a trade situation and we should show it.
            if self.weight:
                if self.count:
                    description	+= "It weighs %.2f oz." % (float(self.count) * float(self.weight) / 100)
                else:
                    description	+= "It weighs %.2f oz." % (float(self.weight) / 100)

            # Special description, not always defined
            if self.params:
                if "description" in self.params:
                    extra = self.params["description"]
                elif "description" in items[self.itemId]:
                    extra = items[self.itemId]["description"]

        ########################
        if self.text and (player and (not position or player.inRange(position, 4, 4))):
            extra += self.text
            
        return "%s\n%s" % (description, extra)

    def rawName(self):
        if self.count > 1 and "plural" in items[self.itemId]:
            return items[self.itemId]["plural"].title()
        return items[self.itemId]["name"].title()
        
    def reduceCount(self, count):
        self.count -= count
            
    def slots(self):
        slot = self.slotType
        if not slot:
            return ()
        elif slot == "head":
            return game.enum.SLOT_HEAD,
        elif slot == "necklace":
            return game.enum.SLOT_NECKLACE,
        elif slot == "backpack":
            return game.enum.SLOT_BACKPACK,
        elif slot == "body":
            return game.enum.SLOT_ARMOR,
        elif slot == "two-handed":
            return game.enum.SLOT_RIGHT,
        elif slot == "legs":
            return game.enum.SLOT_LEGS,
        elif slot == "feet":
            return game.enum.SLOT_FEET,
        elif slot == "ring":
            return game.enum.SLOT_RING,
        elif slot == "ammo":
            return game.enum.SLOT_AMMO,
        elif self.weaponType == SKILL_SHIELD:
            return game.enum.SLOT_LEFT,
        elif self.weaponType:
            return game.enum.SLOT_RIGHT,
        else:
            return ()

    def decay(self, position, to=None, duration=None, callback=None, creature=None):
        if to == None:
            to = self.decayTo
        
        if self.itemId == to:
            return # Not decay to self
            
        if duration == None:
            duration = self.duration
            if not duration:
                return # We can't decay

        try:
            self.executeDecay.cancel()
        except:
            pass
        
        # Store position:
        self.decayPosition = position
        if position.x == 0xFFFF:
            self.decayCreature = creature
        def executeDecay():
            try:
                if self.decayCreature:
                    # Remove cache
                    self.decayCreature.removeCache(self)
                    
                    # Change itemId
                    self.itemid = self.decayTo
                    
                    # Add cache
                    self.decayCreature.addCache(self)
                    
                    # We can assume the bag is open. And the inventory is always visible.
                    if position.y < 64:
                        stream = self.decayCreature.packet()
                        stream.addInventoryItem(position.y, self)
                        stream.send(self.decayCreature.client)
                    else:
                        self.decayCreature.updateAllContainers()
                        
                else:
                    self.transform(self.decayTo, self.decayPosition)
                
                # Hack for chained decay
                if self.itemId and self.decayTo != None:
                    self.decay(self.decayPosition, callback=callback, creature=creature)
                else:
                    del self.decayPosition
                    try:
                        del self.decayCreature
                    except:
                        pass
                    
                if self.itemId and callback:
                    callback(self)
            except:
                pass # I don't exist here anymore.
                
        self.executeDecay = reactor.callLater(duration, executeDecay)

    def stopDecay(self):
        if self.executeDecay:
            try:
                self.executeDecay.cancel()
            except:
                pass
            
    def __getstate__(self):
        
        if self.params:
            params = self.params.copy()
            try:
                del params["inPlayer"]
                del params["inContainer"] # This only exists if inPlayer exists.
            except:
                pass
            
            try:
                del params["openIndex"]
            except:
                pass

            try:
                del params["inTrade"]
            except:
                pass
            
            try:
                del params["executeDecay"]
            except:
                pass
            
        else:
            params = None
            
        if self.executeDecay:
            delay = round(self.executeDecay.getTime() - time.time(), 1)
            if delay > 0:
                return (self.itemId, self.actions, params, delay)
            
        return (self.itemId, self.actions, params)
    
    def __setstate__(self, state):
        self.itemId = state[0]
        self.actions = state[1]
                
        self.params = state[2]

        if len(state) == 4:
            self.decay(self.decayPosition, duration=state[3])
        

    def copy(self):
        newItem = copy.deepcopy(self)
        try:
            del newItem.params["tileStacked"]
        except:
            pass
        return newItem
        
    def transform(self, toId, position):
        if position.x != 0xFFFF:
            tile = position.getTile()
            stackPos = tile.findStackpos(self)

            tile.removeItem(self)
            item = self
            if item.tileStacked:
                item = item.copy()
                
            item.itemId = toId
            if toId:
                newStackpos = tile.placeItem(item)

            for spectator in game.engine.getSpectators(position):
                stream = spectator.packet()
                stream.removeTileItem(position, stackPos)
                if toId:
                    stream.addTileItem(position, newStackpos, item)
                    
                stream.send(spectator)
        else:
            if self.tileStacked:
                self = self.copy()
                
            self.itemId = toId
            self.inPlayer.replaceItem(position, self)
            
def cid(itemid):
    try:
        return items[itemid]["cid"]
    except:
        return None

def sid(itemid):
    try:
        return reverseItems[itemid]
    except:
        return None
        
def attribute(itemId, attr):
    check = ('solid','blockprojectile','blockpath','usable','pickable','movable','stackable','ontop','hangable','rotatable','animation')
    try:
        if attr in check:
            return items[itemId]["a"] & check.index(attr)
            
        return items[itemId][attr]
    except:
        return
        
@inlineCallbacks
def loadItems():
    global items
    global reverseItems
    global itemNames
    #global itemAttributes
    log.msg("Loading items...")
    if config.itemCache:
        try:
            with _open("data/cache/items.cache", "rb") as f:
                items, reverseItems, itemNames = marshal.loads(f.read())
            log.msg("%d Items loaded (from cache)" % len(items))
            return
        except IOError:
            pass
        
    # Async SQL (it's funny isn't it?)
    d1 = sql.conn.runQuery("SELECT sid,cid,IF(`name` <> '', `name`, NULL) as `name`,IF(`type`, `type`, NULL) as `type`,IF(`plural` <> '' AND `plural` != `name`, `plural`, NULL) as `plural`,IF(`article` <> '', `article`, NULL) as `article`,IF(`subs`, `subs`, NULL) as `subs`,IF(`speed`, `speed`, NULL) as `speed`,cast(IF(`solid`, 1 << 0, 0) + IF(`blockprojectile`, 1 << 1, 0) + IF(`blockpath`, 1 << 2, 0) + IF(`usable`, 1 << 3, 0) + IF(`pickable`, 1 << 4, 0) + IF(`movable`, 1 << 5, 0) + IF(`stackable`, 1 << 6, 0) + IF(`ontop`, 1 << 7, 0) + IF(`hangable`, 1 << 8, 0) + IF(`rotatable`, 1 << 9, 0) + IF(`animation`, 1 << 10, 0) as unsigned integer) AS a FROM items")
    d2 = sql.conn.runQuery("SELECT sid, `key`, `value` FROM item_attributes") # We'll be waiting, won't we?
    
    
    # Make two new values while we are loading
    loadItemNames = {}
    if config.useNumpy:
        from numpy import empty, uint16
        loadItems = empty((config.itemMaxServerId + 1), dict)
        reverseLoadItems = empty((config.itemMaxClientId + 1), uint16)
    else:
        loadItems = [0] * (config.itemMaxServerId + 1)
        reverseLoadItems = [0] * (config.itemMaxClientId + 1)


    for item in (yield d1):
        sid = item[0]
        cid = item[1]
        attr = {'cid':cid, 'a':item[8]}

        if item[4] and item[4] != item[2]:
            attr['plural'] = item[4]

        if item[5]:
            attr["article"] = item[5]

        if item[3] != 1:
            loadItemNames[item[2]] = sid

        if item[3]:
            attr['type'] = item[3]

        if item[2]:
            attr['name'] = item[2]

        if item[7]:
            attr['speed'] = item[7]

        
        reverseLoadItems[cid] = sid

        loadItems[sid] = attr
        if item[6]:
            for x in xrange(1, item[6]+1):
                loadItems[sid+x] = attr
                
        if sid in MONEY_MAP2:
            loadItems[sid]["currency"] = MONEY_MAP2[sid]

    for data in (yield d2):
        if data[1] == "fluidSource":
            loadItems[data[0]]["fluidSource"] = getattr(game.enum, 'FLUID_%s' % data[2].upper())
        elif data[1] == "weaponType":
            loadItems[data[0]]["weaponType"] = data[2]
            if data[2] not in ("ammunition", "wand"):
                loadItems[data[0]]["weaponSkillType"] = getattr(game.enum, 'SKILL_%s' % data[2].upper())
        elif data[2]:
            try:
                loadItems[data[0]][data[1]] = int(data[2])
            except:
                loadItems[data[0]][data[1]] = data[2]

    log.msg("%d Items loaded" % len(loadItems))

            
    # Replace the existing items
    items = loadItems
    reverseItems = reverseLoadItems
    itemNames = loadItemNames
    
    # Cache
    if config.itemCache:
        with _open("data/cache/items.cache", "wb") as f:
            f.write(marshal.dumps((tuple(items), tuple(reverseItems), itemNames), 2))
            
    
    
    
