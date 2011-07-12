from twisted.internet.defer import waitForDeferred, deferredGenerator
import sql, cjson
from twisted.python import log

items = {}
reverseItems = {}

class BaseThing:
     def cid(self):
         return items[self.itemId]['cid']

### Container class ###
class Container:
    def __init__(self, size):
        self.items = []
        self.maxSize = size
        self.openId = None
        
    def placeItem(self, item):
        length = len(self.items)
        if length < self.maxSize:
            self.items.append(item)
        return length-2
        
    def removeItem(self, item):
        return self.items.remove(item)
        
    def getThing(self, pos):
        try:
            return self.items[pos]
        except:
            return None
            
    def findSlot(self, item):
        return self.items.index(item)
        
### Item ###
class Item:
    def __init__(self, itemid, count=None):
        self.itemId = itemid
        self.count = count if self.stackable else None
        
        # Extend items such as containers, beds and doors
        if "containerSize" in self.attributes():
            self.container = Container(self.containerSize)
            
    def __getattr__(self, name):
        if name and name in items[self.itemId]:
            return items[self.itemId][name]
        elif not "__" in name:
            return None
        raise AttributeError, name
        
    def name(self):
        if self.count > 1 and "plural" in items[self.itemId]:
            return (items[self.itemId]["article"]+" " if items[self.itemId]["article"]+" " else "") + items[self.itemId]["plural"]
        else:
            return (items[self.itemId]["article"]+" " if items[self.itemId]["article"]+" " else "") + items[self.itemId]["name"]
            
    def attributes(self):
        return items[self.itemId]
        
    def reduceCount(self, count):
        self.count -= count
        if self.count <= 0:
            pass # TODO: remove
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
    d = waitForDeferred(sql.conn.runQuery("SELECT sid,cid,name,attributes,plural,article FROM items"))
    yield d
    
    result = d.getResult()
    for item in result:
        item["cid"] = int(item["cid"]) # no long
        item["sid"] = int(item["sid"]) # no long
        if item["attributes"]:
            items[item["sid"]] = cjson.decode(item["attributes"])
        else:
            items[item["sid"]] = {}
        items[item["sid"]]["name"] = item["name"]
        if item["plural"]:
            items[item["sid"]]["plural"] = item["plural"]
        items[item["sid"]]["article"] = item["article"] or None
        
        items[item["sid"]]["cid"] = item["cid"]
        reverseItems[item["cid"]] = item["sid"]
    log.msg("%d Items loaded" % len(items))