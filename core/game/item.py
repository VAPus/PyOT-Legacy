from twisted.internet.defer import waitForDeferred, deferredGenerator
import sql
from twisted.python import log
from collections import deque
import game.enum
import bindconstant
import config

items = None
reverseItems = None

### Container class ###
class Container(object):
    __slots__ = ('items', 'maxSize')
    def __init__(self, size):
        self.items = deque()
        self.maxSize = size
        
    def placeItem(self, item):
        length = len(self.items)
        if length < self.maxSize:
            self.items.appendleft(item)
            return 0
        else:
            return None

    def placeItemRecursive(self, item):
        length = len(self.items)
        if length < self.maxSize:
            self.items.appendleft(item)
            return 0
        else:
            for itemX in self.items:
                if itemX.containerSize:
                    if itemX.container.placeItemRecursive(item) == 0:
                        return itemX

    def removeItem(self, item):
        return self.items.remove(item)
        
    def getThing(self, pos):
        try:
            return self.items[pos]
        except:
            return None
            
    def findSlot(self, item):
        return self.items.index(item)

bindconstant.bind_all(Container)

### Item ###
class Item(object):
    attributes = ('solid','blockprojectile','blockpath','usable','pickable','movable','stackable','ontop','hangable','rotatable','animation')
    __slots__ = ('itemId', 'actions', 'teledest', 'description', 'count', 'container', 'text')
    def __init__(self, itemid, count=None, actions=[], **kwargs):
        self.itemId = itemid
        self.actions = map(str, actions)
        if self.stackable:
            self.count = count
        
        
        # Extend items such as containers, beds and doors
        elif "containerSize" in items[self.itemId]:
            self.container = Container(self.containerSize)
            
        if kwargs:
            for key in kwargs:
                setattr(self, key, kwargs[key])

    def thingId(self):
        return self.itemId # Used for scripts

    def actionIds(self):
        return self.actions
            
    def __getattr__(self, name):
        try:
            attrVal = 1 << self.attributes.index(name)
            return items[self.itemId]["a"] & attrVal == attrVal
        except:
            if name in items[self.itemId]:
                return items[self.itemId][name]
            elif not "__" in name:
                return None
        raise AttributeError, name
        
    def name(self):
        if self.count > 1 and "plural" in items[self.itemId]:
            return (items[self.itemId]["article"]+" " if items[self.itemId]["article"]+" " else "") + items[self.itemId]["plural"]
        else:
            return (items[self.itemId]["article"]+" " if items[self.itemId]["article"]+" " else "") + items[self.itemId]["name"]
            
        
    def reduceCount(self, count):
        self.count -= count
        if self.count <= 0:
            pass # TODO: remove
            
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
        
            
@deferredGenerator
def loadItems():
    log.msg("Loading items...")

    # Async SQL (it's funny isn't it?)
    d = waitForDeferred(sql.conn.runQuery("SELECT sid,cid,name,`type`,plural,article,subs,speed,cast(IF(`solid`, 1 << 0, 0) + IF(`blockprojectile`, 1 << 1, 0) + IF(`blockpath`, 1 << 2, 0) + IF(`usable`, 1 << 3, 0) + IF(`pickable`, 1 << 4, 0) + IF(`movable`, 1 << 5, 0) + IF(`stackable`, 1 << 6, 0) + IF(`ontop`, 1 << 7, 0) + IF(`hangable`, 1 << 8, 0) + IF(`rotatable`, 1 << 9, 0) + IF(`animation`, 1 << 10, 0) as unsigned integer) AS a FROM items"))
    d2 = waitForDeferred(sql.conn.runQuery("SELECT sid, `key`, `value` FROM item_attributes"))
    yield d
    
    
    # Make two new values while we are loading
    loadItems = [None] * (config.itemMaxServerId + 1)
    reverseLoadItems = [None] * (config.itemMaxClientId + 1)


    for item in d.getResult():
        subs = item["subs"]
        del item["subs"]
        if item["plural"] == item["name"] or not item["plural"]:
            del item["plural"]
            
                    
        reverseLoadItems[item["cid"]] = item["sid"]
        
        loadItems[item["sid"]] = item
        if subs:
            for x in xrange(1, subs+1):
                reverseLoadItems[item["cid"]+x] = item["sid"]+x
                loadItems[item["sid"]+x] = loadItems[item["sid"]]
            
    del d
    yield d2
    autoCastValue = game.engine.autoCastValue
    for data in d2.getResult():
        if data["key"] == "fluidSource":
            val = getattr(game.enum, 'FLUID_'+data["value"].upper())
        else:
            val = autoCastValue(data["value"])
        if val:
            loadItems[data["sid"]][data["key"]] = val
    del d2
    log.msg("%d Items loaded" % len(loadItems))
    
    # Replace the existing items
    global items
    global reverseItems
    items = tuple(loadItems)
    reverseItems = tuple(reverseLoadItems)
    
    
    
