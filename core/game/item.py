from twisted.internet.defer import inlineCallbacks
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
        if not items:
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
        except:
            print "Len items: %d" % len(items)
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
        try:
            attrVal = 1 << self.attributes.index(name)
            return items[self.itemId]["a"] & attrVal
        except:
            try:
                return self.params[name]
            except:
                try:
                    return items[self.itemId][name]
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
    
    def description(self):
        return "You see %s. %s" % (self.name(), items[self.itemId]["description"] if "description" in items[self.itemId] else "")

    def rawName(self):
        if self.count > 1 and "plural" in items[self.itemId]:
            return items[self.itemId]["plural"].title()
        return items[self.itemId]["name"].title()
        
    def reduceCount(self, count):
        self.count -= count
            
    def slotId(self):
        if not self.slotType:
            return None
        else:
            if self.slotType == "head":
                return game.enum.SLOT_HEAD
            elif self.slotType == "necklace":
                return game.enum.SLOT_NECKLACE
            elif self.slotType == "backpack":
                return game.enum.SLOT_BACKPACK
            elif self.slotType == "body":
                return game.enum.SLOT_ARMOR
            elif self.slotType == "two-handed":
                return game.enum.SLOT_LEFT
            elif self.slotType == "legs":
                return game.enum.SLOT_LEGS
            elif self.slotType == "feet":
                return game.enum.SLOT_FEET
            elif self.slotType == "ring":
                return game.enum.SLOT_RING
            elif self.slotType == "ammo":
                return game.enum.SLOT_AMMO
            else:
                if self.weaponType:
                    return game.enum.SLOT_LEFT if self.weaponType in ('sword', 'rod', 'ward') else game.enum.SLOT_RIGHT
                else:
                    return None

    def decay(self, position, to=None, duration=None, callback=None, creature=None):
        import game.map
        
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
        if position[0] == 0xFFFF:
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
                    if position[1] < 64:
                        stream = self.decayCreature.packet()
                        stream.addInventoryItem(position[1], self)
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
                
        self.executeDecay = game.engine.safeCallLater(duration, executeDecay)

    def __getstate__(self):
        if self.executeDecay:
            delay = round(self.executeDecay.getTime() - time.time(), 1)
            if delay > 0:
                return (self.itemId, self.actions, self.params, delay)
            
        return (self.itemId, self.actions, self.params)
    
    def __setstate__(self, state):
        self.itemId = state[0]
        self.actions = state[1]
                
        self.params = state[2]

        if len(state) == 4:
            self.decay(self.decayPosition, duration=state[3])
        
        # Bugfix
        try:
            del self.params["opened"]
        except:
            pass
        
    def copy(self):
        newItem = copy.deepcopy(self)
        try:
            del newItem.params["tileStacked"]
        except:
            pass
        return newItem
        
    def transform(self, toId, position, stackPos=None):
        if position[0] != 0xFFFF:
            import game.map
            tile = game.map.getTile(position)
            if not stackPos:
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
                    stream.addTileItem(position, stackPos, item)
                    
                stream.send(spectator)
        else:
            if item.tileStacked:
                item = item.copy()
                
            item.itemId = toId
            self.inPlayer.replaceItem(position, None, self)
            
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
    d2 = sql.conn.runQuery("SELECT sid, `key`, `value` FROM item_attributes ORDER BY sid") # We'll be waiting, won't we?
    
    
    # Make two new values while we are loading
    loadItemNames = {}
    if config.useNumpy:
        from numpy import empty, uint16
        loadItems = empty((config.itemMaxServerId + 1), dict)
        reverseLoadItems = empty((config.itemMaxClientId + 1), uint16)
    else:
        loadItems = [None] * (config.itemMaxServerId + 1)
        reverseLoadItems = [None] * (config.itemMaxClientId + 1)


    for item in (yield d1):
        subs = item["subs"]
        del item["subs"]
        
        sid = item["sid"]
        del item["sid"]
        
        if item["plural"] == item["name"] or not item["plural"]:
            del item["plural"]
            
        if not item["article"]:
            del item["article"]

        if item['type'] != 1:
            loadItemNames[item['name']] = sid
            
        if not item["type"]:
            del item["type"]
        
        if not item["name"]:
            del item["name"]
        
        if not item["speed"]:
            del item["speed"]
        
        cid = item["cid"]
        reverseLoadItems[cid] = sid

        loadItems[sid] = item
        if subs:
            for x in xrange(1, subs+1):
                attributes = item.copy()
                attributes["cid"] = cid+x
                reverseLoadItems[cid+x] = sid+x
                
                loadItems[sid+x] = attributes
            
    sid = 0
    attributes = None
    for data in (yield d2):
        if sid != data["sid"]:
            attributes = loadItems[data["sid"]]
            sid = data["sid"]
            
        if data["key"] == "fluidSource":
            attributes["fluidSource"] = getattr(game.enum, 'FLUID_%s' % data["value"].upper())
        elif data["key"] == "weaponType":
            try:
                attributes["weaponType"] = getattr(game.enum, 'SKILL_%s' % data["value"].upper())
            except:
                attributes["weaponType"] = data["value"]
        elif data["value"]:
            try:
                attributes[data["key"]] = int(data["value"])
            except:
                attributes[data["key"]] = data["value"]

    log.msg("%d Items loaded" % len(loadItems))
    
    if config.itemCache:
        """# Build namedtuples
        for item in loadItems:
            if item:
                keys = tuple(item.keys())
                try:
                    item = itemAttributes[keys]._make(item.values())
                except:
                    itemAttributes[keys] = namedtuple("Attr", keys)
                    item = itemAttributes[keys]._make(item.values())"""
        cut = 0
        for i in loadItems[::-1]:
            if not i:
                cut += 1
        if cut:        
            loadItems = loadItems[:-cut]
            
    # Replace the existing items
    items = tuple(loadItems)
    reverseItems = tuple(reverseLoadItems)
    itemNames = loadItemNames
    
    # Cache
    if config.itemCache:
        with _open("data/cache/items.cache", "wb") as f:
            f.write(marshal.dumps((items, reverseItems, itemNames), 2))
            
    
    
    
