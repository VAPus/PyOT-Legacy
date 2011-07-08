from twisted.internet.defer import waitForDeferred, deferredGenerator
import core.sql, cjson
from twisted.python import log

items = {}
reverseItems = {}

class BaseThing:
     def cid(self):
         return items[self.itemId]['cid']


class Item(BaseThing):
     pass

def cid(itemid):
    try:
        return items[itemid]["cid"]
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
        items[item["sid"]]["cid"] = item["cid"]
        reverseItems[item["cid"]] = item["sid"]
    log.msg("%d Items loaded" % len(items))