from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor
import sql
from twisted.python import log
from collections import deque, namedtuple
import game.enum
import config
import game.engine
import copy
import time
import marshal
import inflect
import gc

INFLECT = inflect.engine()

try:
    import io # Python 2.7+
    _open = io.open
except:
    _open = open # Less than 2.7
    
items = {}
reverseItems = {}

### Container class ###
class Container(object):
    # TODO: Kill this class.
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
    
    def weight(self):
        weight = 0
        for item in self.getRecursive():
            iweight = item.weight
            if iweight:
                weight += iweight * (item.count or 1)
                
        return weight
        
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

    def __repr__(self):
        return "<Container (%d/%d) at %s>" % (self.size(), self.items.maxlen, hex(id(self)))
        
            
### Item ###
class Item(object):
    attributes = ('solid','blockprojectile','blockpath','usable','pickable','movable','stackable','ontop','hangable','rotatable','animation')

    def __init__(self, itemId, count=1, actions=None, **kwargs):
        try:
            self._itemBase = items[itemId]
        except (KeyError, IndexError):
            print "ItemId %d doesn't exist!" % itemId
            itemId = 100
            self._itemBase = items[itemId]
            
        self.itemId = itemId
        self.actions = actions
        
        if kwargs:
            for k in kwargs:
                self.__setattr__(k, kwargs[k])

        if self._itemBase['a'] & 64:
            if not count or count < 0:
                count = 1
            self.count = count
            
        # Extend items such as containers
        try:
            self.container = Container(self._itemBase["containerSize"])
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

    def register(self, event, func, **kwargs):
        game.scriptsystem.get(event).register(self, func, **kwargs)
        
    def registerAll(self, event, func, **kwargs):
        game.scriptsystem.get(event).register(self.itemId, func, **kwargs)
        
    def getsub(self):
        try:
            return self.count
        except:
            try:
                return self.fluidSource
            except:
                return None

    def vertifyPosition(self, creature, pos):
        if pos.x == 0xFFFF:
            if not creature:
                raise Exception("Cannot vertify Position inside inventory when creature == None!")
            
            if pos.y < 64:
                if creature.inventory[pos.y-1] == self:
                    return pos
                elif creature.inventory[pos.y] == self:
                    return pos
                else:
                    return False # We cant assume that inventory items move
                    
            else:
                container = creature.getContainer(pos.y-64)
                if not container:
                    print creature.openContainers
                    print pos.y - 64
                    return False
                    
                if container.container.items[pos.z] == self:
                    return pos
                else:
                    for z in xrange(len(container.container.items)):
                        if container.container.items[z] == self:
                            pos.z = z
                            return pos
                    return False # Not found

        tile = pos.getTile()
        
        if isinstance(pos, StackPosition) and tile.things[pos.stackpos] == self:
            return pos
            
        elif not self in tile.things:
            return False # Not on this tile
            
        elif isinstance(pos, StackPosition):
            for z in xrange(len(tile.things)):
                if tile.things[z] == self:
                    pos.stackpos = z
                    return pos
        
        return pos            
        
    def actionIds(self):
        return self.actions or []
    
    def hasAction(self, name):
        if name == "item":
            return True
        elif self.actions is None:
            return False
        else:
            return name in self.actions
        
    def addAction(self, name):
        if self.actions is None:
            self.actions = [name]
        else:
            self.actions.append(name)
            
    def removeAction(self, name):
        self.actions.remove(name)
    
    @property
    def solid(self):
        return self._itemBase['a'] & 1
        
    @property
    def blockprojectile(self):
        return self._itemBase['a'] & 2
        
    @property
    def blockpath(self):
        return self._itemBase['a'] & 4
        
    @property
    def cid(self):
        return self._itemBase['cid']
    
    """
    # Changeable attributes. Ignore.
    @property
    def usable(self):
        return items[self.itemId][None] & 8
        
    @property
    def pickable(self):
        return items[self.itemId][None] & 16
        
    @property
    def movable(self):
        return items[self.itemId][None] & 32
    """    
    @property
    def stackable(self):
        return self._itemBase['a'] & 64
        
    @property
    def ontop(self):
        return self._itemBase['a'] & 128
        
    @property
    def hangable(self):
        return self._itemBase['a'] & 256
        
    @property
    def rotatable(self):
        return self._itemBase['a'] & 512
        
    @property
    def animation(self):
        return self._itemBase['a'] & 1024
        
    @property
    def type(self):
        try:
            return self._itemBase["type"]
        except KeyError:
            return False
            
    def __getattr__(self, name):
        try:
            return self._itemBase[name]
        except:
            try:
                return self._itemBase['a'] & (1 << self.attributes.index(name))
            except:
                if not "__" in name:
                    return None
                       
        raise AttributeError, name
    
    def formatName(self, player=None):
        if not player:
            raise Exception("We need to have a player when asking for a items name now apperently!")
            
        if self.count > 1:
            return _l(player, "%(count)d %(plural_name)s") % {"count": self.count, "plural_name": _l(player, INFLECT.plural(self.name))}
            
        return _l(player, INFLECT.a(self.name))
    
    def description(self, player=None, position=None):
        bonus = ['absorbPercentDeath', 'absorbPercentPhysical', 'absorbPercentFire', 'absorbPercentIce', 'absorbPercentEarth', 'absorbPercentEnergy', 'absorbPercentHoly', 'absorbPercentDrown', 'absorbPercentPoison', 'absorbPercentManaDrain', 'absorbPercentLifeDrain']
        elems = ['elementPhysical', 'elementFire', 'elementIce', 'elementEarth', 'elementDeath', 'elementEnergy', 'elementHoly', 'elementDrown']
        #TODO: charges, showcharges, showattributes
        description = _l(player, "You see %s") % self.formatName(player)
        if self.showDuration:
            description += _lp(player, "that will expire in %d second.", "that will expire in %d seconds.", self.duration) % self.duration # TODO: days? , minutes, hours
        if self.containerSize:
            description += _l(player, " (Vol:%d).") % self.containerSize
        if (self.armor or (self.speed and self.pickable) or self.attack or self.defence or self.showcharges) and (not self.ammoType): #need to include crossbows.
            description += " ("
            if self.armor:
                description += _l(player, "Arm:%d") % self.armor
            if self.attack:
                description += _l(player, "Atk:%d") % self.attack
            moreatk = ""
            for elem in elems:
                value = self.__getattr__(elem)
                if value:
                    pre = elem[len("element"):]
                    moreatk += " %+d %s" % (value, pre.lower())
            if moreatk:
                description += _l(player, " physical %s") % moreatk
            if self.extraatk:
                description += _l(player, " %+d") % self.extraatk
            if self.defence:
                if self.attack:
                    description += ", "
                description += _l(player, "Def:%d") % self.defence
            if self.extradef:
                description += _l(player, " %+d") % self.extradef
            morearm = ""
            if self.speed:
                morearm += _l(player, ", %+d speed") % self.speed
            if self.__getattr__('magiclevelpoints'):
                morearm += _l(player, ", %+d magic level") % self.__getattr__('magiclevelpoints')
            if self.__getattr__('absorbPercentAll'):
                morearm = _l(player, ', %(all)+d%% Physical, %(all)+d%% Death, %(all)+d%% Fire, %(all)+d%% Ice, %(all)+d%% Earth, %(all)+d%% Energy, %(all)+d%% Holy, %(all)+d%% Drown, %(all)+d%% Poison, %(all)+d%% ManaDrain, %(all)+d%% Lifedrain') % {"all":self.__getattr__('absorbPercentAll')}
            # Step one, names to dict with value
            bonuses = {}
            for bns in bonus:
                data = self.__getattr__(bns)
                if data:
                    bonuses[bns] = data
            
            # Step two, sorting the dict
            for w in sorted(bonuses, key=bonuses.get, reverse=True):
                pre = w[len("absorbPercent"):]
                morearm += ", %+d%% %s" % (bonuses[w], pre.lower())
            if morearm:
                if not self.armor and not self.defence:
                    morearm = morearm[2:]
                description += "%s" % morearm
            description += ")."

        extra = ""
        if player and (not position or position.x == 0xFFFF or player.inRange(position, 1, 1)): # If position ain't set/known, we're usually in a trade situation and we should show it.
            if self.containerSize:
                extra += _l(player, "\nIt weighs %.2f oz.") % (float(self.weight + self.container.weight()) / 100)
                
            elif self.weight:
                if self.count:
                    extra += _l(player, "\nIt weighs %.2f oz.") % (float(self.count) * float(self.weight) / 100)
                else:
                    extra += _l(player, "\nIt weighs %.2f oz.") % (float(self.weight) / 100)

            # Special description, hacky.
            if "description" in self.__dict__:
                extra = "\n%s" % self.__dict__["description"]
            elif "description" in items[self.itemId]:
                extra = "\n%s" % items[self.itemId]["description"]

        if self.text and (player and (not position or position.x == 0xFFFF or player.inRange(position, 4, 4))):
            extra += _l(player, "\nYou Read: %s") % self.text

        return "%s%s\n" % (description, extra)
        
    def rawName(self):
        if self.count:
            return INFLECT.plural(self.name.title())
        return self.name.title()
        
    def reduceCount(self, count):
        self.count -= count
            
    def slots(self):
        slot = self.slotType

        #if not slot:
        #    return ()
        if slot == "head":
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

        position = self.vertifyPosition(creature, position)
        if not position:
            raise Exception("BUG: Item position cannot be vertified!") 
        
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
                    if to:
                        self.itemid = to
                    
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
                        self.decayCreature.removeItem(position, self)
                        
                else:
                    self.transform(self.decayTo, self.decayPosition)
                
                # Hack for chained decay
                if self.itemId and self.decayTo != None:
                    self.decay(self.decayPosition, callback=callback, creature=creature)
                else:
                    del self.decayPosition
                    
                if self.itemId and callback:
                    callback(self)
            except:
                pass # I don't exist here anymore.
        
        if duration:
            self.executeDecay = reactor.callLater(duration, executeDecay)
        else:
            executeDelay()
            
    def stopDecay(self):
        if self.executeDecay:
            try:
                self.executeDecay.cancel()
            except:
                pass
            
    def __getstate__(self):
        params = self.__dict__.copy()
        del params["_itemBase"]
        try:
            del params["decayCreature"]
            del params["inContainer"] # This only exists if inPlayer exists.
        except:
            pass
            
        try:
            del params["openIndex"]
        except:
            pass

        try:
            del params["parent"]
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
            
        if self.executeDecay:
            delay = round(self.executeDecay.getTime() - time.time(), 1)
            if delay > 0:
                return (params, delay)
                
        return params
    
    def __setstate__(self, state):
        if isinstance(state, tuple):
            self.__dict__ = state[0]
            self.decay(self.decayPosition, duration=state[1])
        else:
            self.__dict__ = state
            
        self._itemBase = items[self.itemId]

    def copy(self):
        newItem = copy.deepcopy(self)
        try:
            del newItem.tileStacked
        except:
            pass
        return newItem
        
    def transform(self, toId, position):
        position = self.vertifyPosition(self.decayCreature, position)
        if not position:
            raise Exception("BUG: Item position cannot be vertified!")
        
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
            self.refresh(position)

    def refresh(self, position):
        position = self.vertifyPosition(self.decayCreature, position)
        creature = self.decayCreature

        if not position:
            raise Exception("BUG: Item position cannot be vertified!")

        if position.x != 0xFFFF:
            tile = position.getTile()
            stackPos = tile.findStackpos(self)
            
            for spectator in game.engine.getSpectators(position):
                stream = spectator.packet()
                
                if self.itemId:
                    stream.updateTileItem(position, stackPos, self)
                else:
                    stream.removeTileItem(position, stackPos)
                    
                stream.send(spectator)
        else:

            # Option 2, the inventory
            if position.y < 64:

                sendUpdate = False
                currItem = creature.inventory[position.y-1]
                if currItem:
                    # Update cached data
                    if creature.removeCache(currItem):
                        sendUpdate = True
                        
                ret = creature.addCache(self)
                if ret:
                    sendUpdate = True
                    creature.inventory[position.y-1] = self
                elif ret == False:
                    creature.inventory[position.y-1] = None
                    tile = game.map.getTile(creature.position)
                    tile.placeItem(self)
                    creature.tooHeavy()
                    
                if sendUpdate:
                    creature.refreshStatus()
                
                creature.updateInventory(position.y)
            
            # Option 3, the bags, if there is one ofcource
            else:
                update = False
                try:
                    bag = creature.openContainers[position.y - 64]
                except:
                    return
                
                try:
                    creature.inventoryCache[bag.itemId].index(bag)
                    currItem = bag.container.items[position.z]
                    if currItem:
                        if creature.removeCache(currItem):
                            update = True
                    
                    ret = creature.addCache(self, bag)
                    if ret == False:
                        del bag.container.items[position.z]
                    elif ret == True:    
                        update = True
                        bag.container.items[position.z] = self
                        
                    stream = creature.packet()
                    stream.updateContainerItem(position.y - 64, position.z, self)
                    if update:
                        creature.refreshStatus(stream)
                    stream.send(creature.client)
                except:  
                    bag.container.items[position.z] = self
                    stream = creature.packet()
                    stream.updateContainerItem(position.y - 64, position.z, self)
                    stream.send(creature.client)
                    
    def __repr__(self):
        # Remove actions:
        r = self.__dict__.copy()
        del r["actions"]
        return "<Item (%s) at %s>" % (r, hex(id(self)))
            
def cid(itemid):
    try:
        return items[itemid][1]
    except:
        return None

def sid(itemid):
    try:
        return reverseItems[itemid]
    except:
        return None

idByNameCache = {}
def idByName(name):
    # Slow, should only be used to build the items on load.
    # We use this so we can prevent having a full runtime list
    # Main reason for the one above is not to save memory, but to support case independant
    # Item names. That would require a loop anyway.
    # This is (sadly) much slower...
    global idByNameCache
    
    name = name.upper()
    try:
        return idByNameCache[name]
    except KeyError:
        for sid in xrange(1500, len(items)):
            try:
                if items[sid]["name"].upper() == name:
                    idByNameCache[name] = sid
                    return sid
            except:
                pass
        
def attribute(itemId, attr):
    check = ('solid','blockprojectile','blockpath','usable','pickable','movable','stackable','ontop','hangable','rotatable','animation')
    try:
        if attr in check:
            return items[itemId][None] & check.index(attr)
            
        return items[itemId][attr]
    except:
        return
        
@inlineCallbacks
def loadItems():
    global items
    global reverseItems
    #global itemAttributes
    
    print "> > Loading items...\n"
    
    if config.itemCache:
        try:
            with _open("data/cache/items.cache", "rb") as f:
                items, reverseItems = marshal.loads(f.read())
            log.msg("%d Items loaded (from cache)" % len(items))
            return
        except IOError:
            pass
        
    # Async SQL (it's funny isn't it?)
    d1 = sql.conn.runQuery("SELECT sid,cid,IF(`name` <> '', `name`, NULL) as `name`,IF(`type`, `type`, NULL) as `type`,IF(`subs`, `subs`, NULL) as `subs`,IF(`speed`, `speed`, NULL) as `speed`,cast(IF(`solid`, 1 << 0, 0) + IF(`blockprojectile`, 1 << 1, 0) + IF(`blockpath`, 1 << 2, 0) + IF(`usable`, 1 << 3, 0) + IF(`pickable`, 1 << 4, 0) + IF(`movable`, 1 << 5, 0) + IF(`stackable`, 1 << 6, 0) + IF(`ontop`, 1 << 7, 0) + IF(`hangable`, 1 << 8, 0) + IF(`rotatable`, 1 << 9, 0) + IF(`animation`, 1 << 10, 0) as unsigned integer) AS a FROM items")
    d2 = sql.conn.runQuery("SELECT sid, `key`, `value` FROM item_attributes") # We'll be waiting, won't we?
    
    
    # Make three new values while we are loading
    loadItems = [None] * (config.itemMaxServerId + 1)
    reverseLoadItems = [None] * (config.itemMaxClientId + 1)

    for item in (yield d1):
        sid = item['sid']
        cid = item['cid']

        if not item['type']:
            del item['type']

        if not item['name']:
            del item['name']
                
        if not item['speed']:
            del item['speed'] 

        reverseLoadItems[cid] = sid

        subs = item['subs']
        del item['subs']
        loadItems[sid] = item
        if subs:
            for x in xrange(1, subs+1):
                loadItems[sid+x] = item
                
        if sid in MONEY_MAP2:
            loadItems[sid]["currency"] = MONEY_MAP2[sid]
            

    for data in (yield d2):
        sid = data["sid"]
        key = data['key']
        value = data["value"]
        if key == "fluidSource":
            loadItems[sid]["fluidSource"] = getattr(game.enum, 'FLUID_%s' % value.upper())
        elif key== "weaponType":
            loadItems[sid]["weaponType"] = value
            if value not in ("ammunition", "wand"):
                loadItems[sid]["weaponSkillType"] = getattr(game.enum, 'SKILL_%s' % value.upper())
        elif value:
            try:
                loadItems[sid]['key'] = int(value)
            except:
                loadItems[sid]['key'] = value

    print "\n> > Items (%s) loaded..." % len(loadItems),
    print "%50s\n" % _txtColor("\t[DONE]", "blue")
            
    # Replace the existing items
    items = loadItems
    reverseItems = reverseLoadItems
    
    # Cache
    if config.itemCache:
        with _open("data/cache/items.cache", "wb") as f:
            f.write(marshal.dumps((tuple(items), tuple(reverseItems)), 2))
            
    gc.collect()
    
    
