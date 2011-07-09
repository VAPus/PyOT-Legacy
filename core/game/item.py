from twisted.internet.defer import waitForDeferred, deferredGenerator
import core.sql, cjson
from twisted.python import log

items = {}
reverseItems = {}

class BaseThing:
     def cid(self):
         return items[self.itemId]['cid']


class Item:
    def __init__(self, itemid, count=None):
        self.itemId = itemid
        self.count = count if self.stackable else None

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
    d = waitForDeferred(core.sql.conn.runQuery("SELECT * FROM items"))
    yield d
    
    result = d.getResult()
    for item in result:
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