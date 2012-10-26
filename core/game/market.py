Markets = {}

class Offer(object):
    def __init__(self, playerId, itemId, price, expire, amount, counter, type=0):
        self.id = 0
        self.playerId = playerId
        self.itemId = itemId
        self.price = price
        self.expire = expire
        self.amount = amount
        self.counter = counter
        self.playerName = ""
        self.type = type
        self.marketId = 0

    @inlineCallbacks
    def insert(self):
        self.id = yield sql.runOperationLastId("INSERT INTO `market_offers`(`world_id`, `market_id`, `player_id`, `item_id`, `amount`, `created`, `price`, `anonymous`, `type`) VALUES (%s,%s,%s,%s,%s,%s,%s,0,%s)", (config.worldId, self.marketId, self.playerId, self.itemId, self.amount, self.expire-config.marketOfferExpire, self.price, self.type))
    
    def save(self):
        if not self.id:
            self.insert()
        else:
            sql.runOperation("UPDATE market_offers SET `player_id` = %s, `item_id` = %s, `amount` = %s, `price` = %s, `type` = %s WHERE `id` = %s", (self.playerId, self.itemId, self.amount, self.price, self.type, self.id))

    def player(self):
        return loadPlayerById(self.playerId)

class Market(object):
    def __init__(self, id):
        self.id = id
        self.items = {} # itemId -> Count.

        self._saleOffers = []
        self._buyOffers = []

    def addSaleOffer(self, offer):
        offer.marketId = self.id

        if offer.itemId in self.items:
            self.items[offer.itemId] += offer.amount or 1
        else:
            self.items[offer.itemId] = offer.amount or 1
        self._saleOffers.append(offer)

    def addBuyOffer(self, offer):
        offer.marketId = self.id

        self._buyOffers.append(offer)

    def buyOffers(self, player):
        count = 0
        for entry in self._buyOffers:
            if entry.playerId == player.data["id"]:
                count += 1

        return count

    def saleOffers(self, player):
        count = 0
        for entry in self._saleOffers:
            if entry.playerId == player.data["id"]:
                count += 1

        return count

    def getSaleOffers(self, itemId):
        entries = []
        for entry in self._saleOffers:
            if entry.itemId == itemId:
                entries.append(entry)

        return entries

    def getBuyOffers(self, itemId):
        entries = []
        for entry in self._buyOffers:
            if entry.itemId == itemId:
                entries.append(entry)

        return entries
    def size(self):
        return len(self.items)

    def getItems(self):
        for itemId in self.items:
            yield (itemId, self.items[itemId])

    def save(self):
        pass # SQL, TODO

@inlineCallbacks
def load():
    global Markets
    for entry in (yield sql.runQuery("SELECT mo.`id`, mo.`market_id`, mo.`player_id`, mo.`item_id`, mo.`amount`, mo.`created`, mo.`price`, mo.`anonymous`, mo.`type`, (SELECT `name` FROM players p WHERE p.`id` = mo.`player_id`) as `player_name` FROM `market_offers` mo WHERE mo.`world_id` = %s AND mo.`type` != 0 AND mo.`created` > %s", (config.worldId, time.time() + config.marketOfferExpire))):
        if not entry["market_id"] in Markets:
            Markets[entry["market_id"]] = Market(0)

        offer = Offer(entry["player_id"], entry["item_id"], entry["price"], entry["created"]+config.marketOfferExpire,entry["amount"], entry["id"] & 0xFFFF, entry["type"])

        offer.id = entry["id"]

        if entry["anonymous"]:
            offer.playerName = "Anonymous"
        else:
            offer.playerName = entry["player_name"]

        if entry["type"] == MARKET_OFFER_SALE:
            Markets[entry["market_id"]].addSaleOffer(offer)
        else:
            Markets[entry["market_id"]].addBuyOffer(offer)

def newMarket(id):
    global Markets
    market = Market(id)
    
    Markets[id] = market

    return market

def getMarket(id):
    try:
        return Markets[id]
    except:
        return newMarket(id)


