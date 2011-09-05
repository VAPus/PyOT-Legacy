from twisted.internet.defer import inlineCallbacks
import sql
from twisted.python import log
from collections import deque
import game.enum
import bindconstant
import config
import game.engine

items = None
reverseItems = None
itemNames = {}

### Container class ###
class Container(object):
    __slots__ = ('items', 'maxSize')
    def __init__(self, size):
        self.items = []
        self.maxSize = size
    
    def __getstate__(self): # For pickle functions such as jsonpickle
        return (self.items, self.maxSize)
    
    def __setstate__(self, state):
        self.items = state[0]
        self.maxSize = state[1]
        
    def placeItem(self, item):
        length = len(self.items)
        if length < self.maxSize:
            self.items.insert(0, item)
            return 0
        else:
            return None

    def placeItemRecursive(self, item):
        length = len(self.items)
        if length < self.maxSize:
            self.items.insert(0, item)
            return 0
        else:
            for itemX in self.items:
                if itemX.containerSize and itemX.container.placeItemRecursive(item) == 0:
                    return itemX

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

# Mailbox
class Mailbox(object):
    def send(self, item):
        if not item.itemId in (game.enum.ITEM_LETTER or game.enum.ITEM_PARCEL):
            return False
        else:
            pass # TODO
            
### Item ###
class Item(object):
    attributes = ('solid','blockprojectile','blockpath','usable','pickable','movable','stackable','ontop','hangable','rotatable','animation')
    #__slots__ = ('itemId', 'actions', 'teledest', 'description', 'count', 'container', 'text')
    __slots__ = ('itemId', 'actions', 'count', 'cont', 'params')
    __conts__ = ('container', 'mailbox') # Just alias for cont
    
    def __init__(self, itemid, count=None, actions=[], **kwargs):
        if type(items[itemid]) != dict:
            log.msg("itemId %d doesn't exist" % itemid)
            itemid = 100
           
        self.itemId = itemid
        self.actions = map(str, actions)
        
        if kwargs:
            self.params = kwargs
        else:
            self.params = None

        if self.stackable:
            self.count = count
        
        else:     
            # Extend items such as containers, beds and doors
            if "containerSize" in items[self.itemId]:
                self.cont = Container(self.containerSize)
                    
            if self.type == "mailbox":
                self.cont = Mailbox()
                


            
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
        if name == 'params': return None # bugfix
        
        if self.params and name in self.params:
            return self.params[name]
        
        if name in self.__conts__:
            return self.cont
            
        try:
            attrVal = 1 << self.attributes.index(name)
            return items[self.itemId]["a"] & attrVal == attrVal
        except:
            if name in items[self.itemId]:
                return items[self.itemId][name]
            elif not "__" in name:
                return None
                
        raise AttributeError, name

    def __setattr__(self, name, value):
        if name in self.__slots__:
            return object.__setattr__(self, name, value)
            
        if self.params:
            self.params[name] = value
        else:
            self.params = {name: value}
            
    def name(self):
        if self.count > 1 and "plural" in items[self.itemId]:
            return str(self.count) + " " + items[self.itemId]["plural"]
        else:
            return (items[self.itemId]["article"]+" " if items[self.itemId]["article"]+" " else "") + items[self.itemId]["name"]
    
    def description(self):
        return "You see %s%s. %s" % (items[self.itemId]["article"]+" " if items[self.itemId]["article"] else "", items[self.itemId]["name"], items[self.itemId]["description"] if "description" in items[self.itemId] else "")

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

    def decay(self, position, to=None, duration=None, callback=None):
        import game.map
        
        if to == None:
            to = self.decayTo
            
        if duration == None:
            duration = self.duration
            if not duration:
                return # We can't decay

        try:
            self.executeDecay.cancel()
        except:
            pass
        
        def executeDecay():
            game.engine.transformItem(self, self.decayTo, position)
            
            # Hack for chained decay
            if self.itemId and self.decayTo != None:
                self.decay(position, callback=callback)
                
            if self.itemId and callback:
                callback(self)
                
        self.executeDecay = game.engine.safeCallLater(duration, executeDecay)

    def __getstate__(self):
        count = None
        try:
            count = self.count
        except:
            pass
        
        try:
            cont = self.cont
        except:
            cont = None
   
        return (self.itemId, self.actions, count, cont, self.params)
    
    def __setstate__(self, state):
        self.itemId = state[0]
        self.actions = state[1]
        if state[2]:
            self.count = state[2]
        if state[3]:
            self.cont = state[3]
                
        self.params = state[4]
        # Bugfix
        try:
            del self.params["opened"]
        except:
            pass
            
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
        
            
@inlineCallbacks
def loadItems():
    log.msg("Loading items...")

    # Async SQL (it's funny isn't it?)
    result = yield sql.conn.runQuery("SELECT sid,cid,name,`type`,plural,article,subs,speed,cast(IF(`solid`, 1 << 0, 0) + IF(`blockprojectile`, 1 << 1, 0) + IF(`blockpath`, 1 << 2, 0) + IF(`usable`, 1 << 3, 0) + IF(`pickable`, 1 << 4, 0) + IF(`movable`, 1 << 5, 0) + IF(`stackable`, 1 << 6, 0) + IF(`ontop`, 1 << 7, 0) + IF(`hangable`, 1 << 8, 0) + IF(`rotatable`, 1 << 9, 0) + IF(`animation`, 1 << 10, 0) as unsigned integer) AS a FROM items")
    d2 = sql.conn.runQuery("SELECT sid, `key`, `value` FROM item_attributes") # We'll be waiting, won't we?
    
    
    # Make two new values while we are loading
    loadItemNames = {}
    if config.useNumpy:
        from numpy import empty, uint16
        loadItems = empty((config.itemMaxServerId + 1), dict)
        reverseLoadItems = empty((config.itemMaxClientId + 1), uint16)
    else:
        loadItems = [None] * (config.itemMaxServerId + 1)
        reverseLoadItems = [None] * (config.itemMaxClientId + 1)


    for item in result:
        subs = item["subs"]
        del item["subs"]
        if item["plural"] == item["name"] or not item["plural"]:
            del item["plural"]
            
                    
        reverseLoadItems[item["cid"]] = item["sid"]
        
        if item['type'] != 1:
            loadItemNames[item['name']] = item['sid']
            
        loadItems[item["sid"]] = item
        if subs:
            for x in xrange(1, subs+1):
                reverseLoadItems[item["cid"]+x] = item["sid"]+x
                loadItems[item["sid"]+x] = loadItems[item["sid"]]
            
    del result

    for data in (yield d2):
        if data["key"] == "fluidSource":
            data["value"] = getattr(game.enum, 'FLUID_'+data["value"].upper())
        if data["value"]:
            try:
                loadItems[int(data["sid"])][data["key"]] = int(data["value"])
            except:
                loadItems[int(data["sid"])][data["key"]] = data["value"]
    del d2
    log.msg("%d Items loaded" % len(loadItems))
    
    # Replace the existing items
    global items
    global reverseItems
    global itemNames
    items = loadItems
    reverseItems = reverseLoadItems
    itemNames = loadItemNames
    
    
    
