Markets = {}

class Offer(object):
    def __init__(self, playerId, itemId, price, expire, amount, counter):
        self.playerId = playerId
        self.itemId = itemId
        self.price = price
        self.expire = expire
        self.amount = amount
        self.counter = counter

    def save(self):
        pass # SQL, TODO

    def player(self):
        return loadPlayerById(self.playerId)

class Market(object):
    def __init__(self, id):
        self.id = id
        self.items = {} # itemId -> Count.

        self._saleOffers = []
        self._buyOffers = []

    def addSaleOffer(self, offer):
        if offer.itemId in self.items:
            self.items[offer.itemId] += offer.amount or 1
        else:
            self.items[offer.itemId] = offer.amount or 1
        self._saleOffers.append(offer)

    def addBuyOffer(self, offer):
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

#@inlineCallbacks
def load():
    # SQL, TODO.
    newMarket()

def newMarket():
    global Markets
    market = Market(0)
    
    # SQL, todo. Insert and get insert id, thats the market.id.

    Markets[0] = market

    # XXX:
    offer = Offer(1, 7449, 1000, time.time(), 1, 1)
    market.addSaleOffer(offer)

    return market

def getMarket(id):
    return Markets[id]


