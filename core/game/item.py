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
import xml.etree.cElementTree as ET
import otjson as json

INFLECT = inflect.engine()

try:
    import io # Python 2.7+
    _open = io.open
except:
    _open = open # Less than 2.7
    
items = None
            
### Item ###
class Item(object):
    attributes = {'solid':1, 'blockprojectile': 1 << 1, 'blockpath': 1 << 2, 'hasheight': 1 << 3, 'usable': 1 << 4, 'pickable': 1 << 5,
                  'movable': 1 << 6, 'stackable': 1 << 7, 'fcd': 1 << 8, 'fcn': 1 << 9, 'fce': 1 << 10, 'fcs': 1 << 11, 'fcw': 1 << 12,
                  'ontop': 1 << 13, 'readable': 1 << 14,'rotatable': 1 << 15, 'hangable': 1 << 16, 'vertical': 1 << 17, 'horizontal': 1 << 18,
                  'cannotdecay': 1 << 19, 'allowdistread': 1 << 20, '_unused': 1 << 21, 'clientcharges': 1 << 22, 'lookthrough': 1 << 23,
                  'animation': 1 << 24}

    def __init__(self, itemId, count=1, actions=None, **kwargs):
        #itemId = 106
        attr = items.get(itemId)
        if not attr:
            print "ItemId %d doesn't exist!" % itemId
            itemId = 100
            attr = items[100]
            
        self.itemId = itemId

        if actions:
            self.actions = actions

        if kwargs:
            for k in kwargs:
                self.__setattr__(k, kwargs[k])

        if attr.get('flags', 0) & 128:
            if not count or count < 0:
                count = 1
            elif not isinstance(count, int):
                raise Exception("Supplied count to Item() is not a number.")

            self.count = count
            
        # Extend items such as containers
        try:
            self.container = deque(maxlen=attr["containerSize"])
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

    def verifyPosition(self):
        pos = self.position
        creature = self.creature

        if not pos:
            return False

        if pos.x == 0xFFFF:
            if not creature and not self.inContainer:
                raise Exception("Cannot verify Position inside inventory when creature == None and inContainer == None!")
            
            if creature and pos.y < 64:
                ### One of these should go.
                if creature.inventory[pos.y-1] == self:
                    return pos
                elif creature.inventory[pos.y] == self:
                    return pos
                else:
                    return False # We cant assume that inventory items move
                    
            else:
                container = self.inContainer
                if not container:
                    return False
                elif creature:
                    for con in creature.openContainers:
                        if creature.openContainers[con] == container:
                            pos.y = con+64
                            break
                if len(container.container) > pos.z and container.container[pos.z] == self:
                    return pos
                else:
                    for z in xrange(len(container.container)):
                        if container.container[z] == self:
                            pos.z = z
                            return pos
                    return False # Not found

        tile = pos.getTile()

        # Might fail. Since we might move to position with creature, and the creature move. Not to worry.        
        try:
            if isinstance(pos, StackPosition) and tile.things[pos.stackpos] == self:
                return pos
        except:
            pass

        if not self in tile.things:
            return False # Not on this tile
            
        elif isinstance(pos, StackPosition):
            for z in xrange(len(tile.things)):
                if tile.things[z] == self:
                    pos.stackpos = z
                    return pos
        
        return pos            
        
    def actionIds(self):
        if not self.itemId: return []

        return self.actions or ['item']
    
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
    def type(self):
        return items[self.itemId].get("type", 0)
    
    @property
    def cid(self):
        return items[self.itemId].get('cid', self.itemId)
        
    def __getattr__(self, name):
        if not "__" in name:
            _items = items[self.itemId]
            try:
                return _items['flags'] & self.attributes[name]
            except:
                return _items.get(name)
            
                       
        raise AttributeError, name
    
    def formatName(self, player=None):
        if not player:
            raise Exception("We need to have a player when asking for a items name now apperently!")
            
        if self.count > 1:
            return _l(player, "%(count)d %(plural_name)s") % {"count": self.count, "plural_name": _l(player, INFLECT.plural(self.name))}
            
        return _l(player, INFLECT.a(self.name))
    
    def useCharge(self):
        self.charges -= 1

        if self.charges <= 0:
            self.remove()

    def description(self, player=None):
        position = self.position
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
                description += "protection %s" % morearm
            if self.showcharges:
                description += ") that has %d charges left." % self.charges
            else:
                description += ")."
        extra = ""
        if player and (not position or position.x == 0xFFFF or player.inRange(position, 1, 1)): # If position ain't set/known, we're usually in a trade situation and we should show it.
            if self.containerSize:
                extra += _l(player, "\nIt weighs %.2f oz.") % ((float(self.weight if self.weight else 0) + self.containerWeight()) / 100)
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
            
    def modify(self, mod):
        count = self.count
        if count == None and mod < 0:
            self.remove()
        
        
        if count <= 0:
            count = 1

        try:
            count += mod
        except:
            pass

        if count > 0:
            self.count = count
            self.refresh()
        else:
            self.remove()
            
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
        elif self.weaponType == 'shield':
            return game.enum.SLOT_LEFT,
        elif self.weaponType:
            return game.enum.SLOT_RIGHT,
        else:
            return ()
  
    def place(self, position, creature=None):
        assert isinstance(position, Position) or isinstance(position, StackPosition)

        if creature:
            creature.placeItem(position, self)
        else:
            tile = position.getTile()
            stackpos = tile.placeItem(self)
            position = position.setStackpos(stackpos)
            self.setPosition(position)
            updateTile(position, tile)
            self.decay()

    def setPosition(self, position, creature=None):
        self.position = position
        if creature:
            self.creature = creature
        if self.creature and (position.x != 0xFFFF or not creature):
            del self.creature

    def decayNow(self):
        return self.decay(self.decayTo, duration=0)

    def decay(self, to=None, duration=None, callback=None):
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


        position = self.verifyPosition()

        if not position:
            raise Exception("BUG: Item position cannot be verified!") 
        
        # Store position:
        def executeDecay():
            try:
                if self.creature:
                    # Remove cache
                    self.creature.removeCache(self)
                    
                    # Change itemId
                    if to:
                        self.itemid = to
                    
                        # Add cache
                        self.creature.addCache(self)
                    
                        # We can assume the bag is open. And the inventory is always visible.
                        if position.y < 64:
                            stream = self.decayCreature.packet()
                            stream.addInventoryItem(position.y, self)
                            stream.send(self.decayCreature.client)
                        else:
                            self.decayCreature.updateAllContainers()
                            
                    else:
                        self.remove()
                        
                else:
                    self.transform(self.decayTo)
                
                # Hack for chained decay
                if self.itemId and self.decayTo != None:
                    self.decay(self.decayTo, callback=callback)
                    
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
    
    def cleanParams(self):
        params = self.__dict__.copy()
        
        try:
            del params["creature"]
        except:
            pass

        try:
            del params["openCreatures"]
        except:
            pass

        try:
            del params["owners"]
        except:
            pass

        try:
            del params["position"]
            del params["inContainer"]
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
        
        return params
    def __getstate__(self):
        params = self.cleanParams()
            
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
            

    def copy(self):
        newItem = Item(self.itemId)
        newItem.__dict__ = self.cleanParams()
        
        try:
            del newItem.tileStacked
        except:
            pass
        return newItem
        
    def transform(self, toId, position=None):
        if not position:
            position = self.verifyPosition()

        if not position:
            raise Exception("BUG: Item position cannot be verified!")
        
        if position.x != 0xFFFF:
            tile = position.getTile()
            # Is this a stacked tile?
            if tile.getFlags() & TILEFLAGS_STACKED:
                tile = tile.copy()
                position.setTile(tile)

            stackPos = tile.findStackpos(self)

            tile.removeItem(self)
            item = self
            if item.tileStacked:
                item = item.copy()
                
            item.itemId = toId
            if toId:
                newStackpos = tile.placeItem(item)
                item.decay()

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
            self.decay()
            self.refresh(position)

    def refresh(self, position=None):
        if not position:
            position = self.verifyPosition()

        creature = self.creature


        if not position:
            raise Exception("BUG: Item position cannot be verified!")

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
                creature.updateInventory(position.y-1)
            
            # Option 3, the bags, if there is one ofcource
            else:
                update = False
                creatures = self.openCreatures
                if not creatures:
                    if creature:
                        creatures = [creature]
                    else:
                        creatures = self.inContainer.openCreatures or [self.inContainer.creature]
                try:
                    bag = creature.openContainers[position.y - 64]
                except:
                    bag = self.inContainer

                
                for creature in creatures:
                    try:
                        creature.inventoryCache[bag.itemId].index(bag)
                        if self.creature:
                            currItem = bag.container[position.z]
                            if currItem:
                                if creature.removeCache(currItem):
                                    update = True
                    
                            ret = creature.addCache(self, bag)
                            if ret == False:
                                del bag.container[position.z]
                            elif ret == True:    
                                update = True
                                bag.container[position.z] = self
                        for index in creature.openContainers:
                            if creature.openContainers[index] == bag: break
                        stream = creature.packet()
                        stream.updateContainerItem(index, position.z, self)
                        if update:
                            creature.refreshStatus(stream)
                        stream.send(creature.client)
                    except:
                        for index in creature.openContainers:
                            if creature.openContainers[index] == bag: break
                        bag.container[position.z] = self
                        stream = creature.packet()
                        stream.updateContainerItem(index, position.z, self)
                        stream.send(creature.client)
                    
    def __repr__(self):
        return "<Item (%s) at %s>" % (self.__dict__, hex(id(self)))
    
    ##### Container stuff ####
    def placeItem(self, item):
        if len(self.container) < self.container.maxlen:
            self.container.appendleft(item)
            item.inContainer = self
            return 0

    def placeItemRecursive(self, item):
        if len(self.container) < self.container.maxlen:
            self.container.appendleft(item)
            item.inContainer = self
            return 0
        else:
            for itemX in self.container:
                if itemX.containerSize and itemX.placeItemRecursive(item) == 0:
                    return itemX

    def size(self):
        return len(self.container)
    
    def containerWeight(self):
        weight = 0
        for item in self.getRecursive():
            iweight = item.weight
            if iweight:
                weight += iweight * (item.count or 1)
                
        return weight
        
    def removeItem(self, item):
        if item.inContainer == self:
           del item.inContainer

        return self.container.remove(item)
        
    def getThing(self, pos):
        try:
            return self.container[pos]
        except:
            return None
    
    def getRecursive(self, items = None):
        if items == None:
            items = self.container
            
        for item in items:
            yield item
            if item != self and item.containerSize:
                for i in self.getRecursive(item.container):
                    yield i

    def getRecursiveWithBag(self, items = None):
        if not items:
            items = self.container
            
        for pos, item in enumerate(items):
            yield (item, self, pos)
            if item.containerSize:
                for i in self.getRecursiveWithBag(item.container):
                    yield i
                    
    def findSlot(self, item):
        return self.container.index(item)
    
    def move(self, newPosition):
        if self.position.x != 0xFFFF and newPosition.x != 0xFFFF:
            # HACK. Find a player.
            player = None
            for p in game.player.allPlayersObject:
                player = p
                break

            moveItem(player, self.position, newPosition)
        elif not self.creature:
            raise Exception("Use moveItem(<Player>, item.position, newPosition) instead")
        else:
            moveItem(self.creature, self.position, newPosition)
        
    def remove(self, position=None):
        if not position:
            position = self.verifyPosition()
        print "Removing", position
        if not position:
            raise Exception("BUG: Item position cannot be verified! %s")

        # Option 1, from the map:
        if position.x != 0xFFFF:
            tile = position.getTile()
            # Is this a stacked tile?
            if tile.getFlags() & TILEFLAGS_STACKED:
                tile = tile.copy()
                position.setTile(tile)


            tile.removeItem(self)
            updateTile(position, tile)

        # Option 2, the inventory
        elif position.y < 64:
            print "Remove2"
            creature = self.creature
            if creature.removeCache(self):
                creature.refreshStatus()
            creature.inventory[position.y-1] = None
            creature.updateInventory(position.y-1)

        # Option 3, the bags, if there is one ofcource
        elif self.inContainer:
            update = False
            try:
                bag = self.creature.openContainers[position.y - 64]
            except:
                # Might bug.
                bag = self.inContainer
            assert bag == self.inContainer
            creature = self.creature
            try:
                creature.inventoryCache[bag.itemId].index(bag)
                if creature.removeCache(self):
                    update = True
            except:
                pass

            del bag.container[position.z]
            index = position.y-64
            if index == DYNAMIC_CONTAINER-64:
                index = bag.openIndex
            if index != None and index < DYNAMIC_CONTAINER:
                if not creature:
                    # Ground bag, possibly open by many.
                    for creature in bag.openCreatures[:]:
                        if creature.alive:
                            with creature.packet() as stream:
                                for containerId in creature.openContainers:
                                    if creature.openContainers[containerId] == bag:
                                        break
                                stream.removeContainerItem(containerId, position.z)
                                if update:
                                    creature.refreshStatus(stream)
                        else:
                            self.openCreatures.remove(creature)
                else:
                    with creature.packet() as stream:
                        stream.removeContainerItem(index, position.z)
                        if update:
                            creature.refreshStatus(stream)
        try:
            del thing.creature
        except:
            pass
        self.position = None

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
        pass

def sid(cid):
    return cidToSid.get(sid, sid)

def cid(sid):
    return items[sid].get('cid', sid)
        
def attribute(itemId, attr):
    try:
        if attr in Item.attributes:
            return items[itemId]['flags'] & Item.attribute[attr]
            
        return items[itemId][attr]
    except:
        return
        
def loadItems():
    global items
    global idByNameCache
    global cidToSid

    print "> > Loading items..."
    
    if config.itemCache:
        try:
            with _open("%s/cache/items.cache" % config.dataDirectory, "rb") as f:
                items, idByNameCache, cidToSid = marshal.loads(f.read())
            log.msg("%d Items loaded (from cache)" % len(items))
            return
        except IOError:
            pass    
    
    # Make three new values while we are loading
    loadItems = {}
    idNameCache = {}
    _cidToSid = {}

    """tree = ET.parse("%s/items.xml" % config.dataDirectory)
    flagTree = {'s':1, 'b':3, 't':8192, 'ts':8193, 'tb':8195, 'm':64, 'p':96}    
    for item in tree.getroot():
        _item = item.attrib

        # Stupid elementtree thinks everything are strings....
        # Would have used lxml, but what the heck, I can't benchmark the difference.
        if "flags" in _item:
            flags = _item["flags"]
            try:
                _item["flags"] = flagTree[flags]
            except KeyError:
                _item["flags"] = int(flags)
        if "speed" in _item:
            _item["speed"] = int(_item["speed"])
        if "type" in _item:
            _item["type"] = int(_item["type"])

        if len(item):
            for attr in item:
                key = attr.tag
                val = attr.get("value")
                if key == "fluidSource":
                    val = getattr(game.enum, 'FLUID_%s' % val.upper())
                elif key == "weaponType" and val not in ("ammunition", "wand"):
                    _item["weaponSkillType"] = getattr(game.enum, 'SKILL_%s' % val.upper())
                elif key == 'shootType':
                    val = getattr(game.enum, 'ANIMATION_%s' % val.upper())
                else:
                    try:
                        val = int(val)
                    except:
                        pass

                _item[key] = val
                attr.clear()

             
        id = _item["id"]
        if "-" in id:
            start, end = map(int, id.split('-'))
            for id in xrange(start, end+1):
                loadItems[id] = _item
        else:        
            id = int(id)    
            loadItems[id] = _item
            try:
                # XXX: Ranged items are usually ground stuff witch we never reference by name.
                idNameCache[_item["name"].upper()] = id
            except:
                pass
        del _item["id"]
        item.clear()        
    """

    # JSON format.
    jsonItems = json.loads(_open(config.itemFile, 'r').read())
    flagTree = {'s':1, 'b':3, 't':8192, 'ts':8193, 'tb':8195, 'm':64, 'p':96}
    for item in jsonItems:
        flags = item.get('flags')
        if flags and not isinstance(flags, int):
            item['flags'] = flagTree[flags]

        if 'shootType' in item:
            item['shootType'] = getattr(game.enum, 'ANIMATION_%s' % item['shootType'].upper())

        if 'fluidSource' in item:
            item['fluidSource'] = getattr(game.enum, 'FLUID_%s' % item['fluidSource'].upper())

        if 'weaponType' in item:
            type = item['weaponType']
            if type not in ("ammunition", "wand"):
                item["weaponSkillType"] = getattr(game.enum, 'SKILL_%s' % type.upper())

        id = item['id']
        cid = item.get('cid')

        del item['id']
        if not isinstance(id, int):
            start, end = map(int, id.split('-'))
            fixCid = isinstance(cid, basestring)
            if fixCid:
                bCid = int(cid.split('-')[0])
            elif cid != None:
                _cidToSid[cid] = item

            for id in xrange(start, end+1):
                if fixCid:
                    _newItem = item.copy()
                    _newItem['cid'] = bCid
                    loadItems[id] = _newItem
                    _cidToSid[bCid] = id
                    bCid += 1
                else:
                    loadItems[id] = item

                 
        else:
            loadItems[id] = item
            if cid != id:
                _cidToSid[cid] = id            
            try:
                name = item["name"].upper()
                if not name in idNameCache:
                    idNameCache[name] = id
            except:
                pass

    print "\n> > Items (%s) loaded..." % len(loadItems),
    print "%45s\n" % "\t[DONE]"

    # Replace the existing items
    items = loadItems
    idByNameCache = idNameCache
    cidToSid = _cidToSid

    # Cache
    if config.itemCache:
        with _open("%s/cache/items.cache" % config.dataDirectory, "wb") as f:
            f.write(marshal.dumps((items, idByNameCache, cidToSid), 2))
