import __builtin__
from twisted.internet import reactor, threads, defer
from twisted.internet.defer import inlineCallbacks, returnValue, Deferred
__builtin__.inlineCallbacks = inlineCallbacks
from collections import deque
from twisted.python import log
import time
import game.map
import config
import userconfig
import math
import sql
import otjson
import game.const
import sys
import random
import game.vocation
import game.resource
import game.scriptsystem
import game.errors
import glob
import game.protocol
import game.logger
import game.chat
import re
import subprocess
import platform
import os
import game.deathlist
import game.ban
import game.position
import config
import game.item
import game.house, game.guild
import language
import game.player, game.creature, game.npc, game.monster, game.spell, game.party
import game.conditions
import game.market

try:
    import cPickle as pickle
except:
    import pickle

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO
    
MERCURIAL_REV = 0
__builtin__.IS_IN_TEST = False

# COLORS
import platform
if platform.system() == "Windows":
    # No colorss? :(
    _txtColor = lambda x, c: x
else:
    def _txtColor(text, color):
        
        if color == "blue":
            color = 34
        elif color == "red":
            color = 31
        elif color == "green":
            color = 32
        elif color == "yellow":
            color = 33
        RESET_SEQ = "\033[0m"
        COLOR_SEQ = "\033[1;%dm"

        return "%s%s%s" % (COLOR_SEQ % color, text, RESET_SEQ)
    
    
def windowsLoading():
    if config.consoleColumns:
        os.system("mode con cols=%d" % config.consoleColumns)
    if config.consoleColor:
        os.system("color %s" % config.consoleColor)

# The loader rutines, async loading :)
@inlineCallbacks
def loader(timer):
    # XXX: Remember, game.XXX -> sys.modules["game.XXX"] because game is set later on. And somehow this causes weird behavior :/
    
    IS_IN_TEST = "trial_temp" in os.getcwd()
    if IS_IN_TEST:
        os.chdir("..")
        # Also ugly hack.
        sys.stdout = StringIO()
        
    # Attempt to get the Merucurial rev
    if os.path.exists(".hg"):
        try:
            # This will work independantly of the OS (no need to have mercurial installed!
            # Not sure if it's 100% accurate, be aware that this is not the active rev, but the latest fetched one.
            # Downloaded packages doesn't have this file, thats why we keep in in a try, it will raise.
            
            MERCURIAL_REV = (os.path.getsize(".hg/store/00changelog.i") // 64) - 1 # Since mercurial start on rev 0, we need to -1 to get the rev number.
            #MERCURIAL_REV = subprocess.check_output(["hg", "parents", "--template={rev}"])
            log.msg("Begin loading (PyOT r%s)" % MERCURIAL_REV)
            if platform.system() == "Windows":
                os.system("title PyOT r%s" % MERCURIAL_REV)
                windowsLoading()
            else:
                sys.stdout.write("\x1b]2;PyOT r%s\x07" % MERCURIAL_REV)

        except (OSError, subprocess.CalledProcessError):
            # hg not in space.
            log.msg("Begin loading...")
            if platform.system() == "Windows":
                os.system("title PyOT")
                windowsLoading()
            else:
                sys.stdout.write("\x1b]2;PyOT\x07")
    else:
        MERCURIAL_REV = "unknown"
        log.msg("Begin loading...")
        if platform.system() == "Windows":
            os.system("title PyOT")
            windowsLoading()
        else:
            sys.stdout.write("\x1b]2;PyOT\x07")      
            
    
    # Begin loading items
    sys.modules["game.item"].loadItems()
    
    # Reset online status
    print "> > Reseting players online status...",
    sql.conn.runOperation("UPDATE players SET online = 0")
    print "%40s\n" % _txtColor("\t[DONE]", "blue")
    
   
    globalData = sql.conn.runQuery("SELECT `key`, `data`, `type` FROM `globals` WHERE `world_id` = %s" % config.worldId)
    groupData = sql.conn.runQuery("SELECT `group_id`, `group_name`, `group_flags` FROM `groups`")
    houseData = sql.conn.runQuery("SELECT `id`,`owner`,`guild`,`paid`,`name`,`town`,`size`,`rent`,`data` FROM `houses` WHERE `world_id` = %s" % config.worldId)

    # Globalize certain things
    print "> > Globalize data...",
    const = sys.modules["game.const"]
    __builtin__.const = const

    for i in dir(const):
        if not "__" in i:
            setattr(__builtin__, i, getattr(const, i))

    for i in dir(sys.modules["game.errors"]):
        if not "__" in i:
            setattr(__builtin__, i, getattr(sys.modules["game.errors"], i))

    for i in sys.modules["game.engine"].globalize:
        setattr(__builtin__, i, getattr(sys.modules["game.engine"], i))

    print "%55s\n" % _txtColor("\t[DONE]", "blue")

    __builtin__.sql = sql.conn
    __builtin__.config = config
    __builtin__.userconfig = userconfig

    import game.pathfinder

    __builtin__.register = game.scriptsystem.register
    __builtin__.registerFirst = game.scriptsystem.registerFirst
    __builtin__.registerForAttr = game.scriptsystem.registerForAttr
    __builtin__.registerClass = game.scriptsystem.registerClass
    __builtin__.defer = defer
    __builtin__.reactor = reactor
    __builtin__.engine = game.engine
    __builtin__.sys = sys
    __builtin__.math = math
    __builtin__.returnValue = returnValue
    __builtin__.Deferred = Deferred
    __builtin__.deque = deque
    __builtin__.random = random
    __builtin__.time = time
    __builtin__.re = re
    __builtin__.spell = game.spell # Simplefy spell making
    __builtin__.callLater = reactor.callLater
    __builtin__.Item = game.item.Item
    __builtin__.itemAttribute = game.item.attribute
    __builtin__.cid = game.item.cid
    __builtin__.idByName = game.item.idByName
    __builtin__.getTile = game.map.getTile
    __builtin__.setTile = game.map.setTile
    __builtin__.getTileConst = game.map.getTileConst
    __builtin__.Boost = game.conditions.Boost
    __builtin__.MultiCondition = game.conditions.MultiCondition
    __builtin__.itemAttribute = game.item.attribute
    __builtin__.getHouseId = game.map.getHouseId
    __builtin__.Position = game.position.Position
    __builtin__.StackPosition = game.position.StackPosition
    __builtin__.getHouseById = game.house.getHouseById
    __builtin__.getGuildById = game.guild.getGuildById
    __builtin__.getGuildByName = game.guild.getGuildByName
    __builtin__.logger = sys.modules["game.logger"]

    # Resources
    __builtin__.genMonster = game.monster.genMonster
    __builtin__.genNPC = game.npc.genNPC
    __builtin__.genQuest = game.resource.genQuest
    __builtin__.genOutfit = game.resource.genOutfit
    __builtin__.genMount = game.resource.genMount
    __builtin__.regVocation = game.vocation.regVocation

    # Spells
    __builtin__.typeToEffect = game.spell.typeToEffect

    # Grab them
    __builtin__.getNPC = game.npc.getNPC
    __builtin__.getMonster = game.monster.getMonster

    # Used alot in monster and npcs
    __builtin__.chance = game.monster.chance

    # We use this in the import system
    __builtin__.scriptInitPaths = game.scriptsystem.scriptInitPaths

    # Access
    __builtin__.access = game.scriptsystem.access
    
    # Conditions
    __builtin__.Condition = game.conditions.Condition
    __builtin__.Boost = game.conditions.Boost
    __builtin__.CountdownCondition = game.conditions.CountdownCondition
    __builtin__.PercentCondition = game.conditions.PercentCondition
    __builtin__.MultiCondition = game.conditions.MultiCondition
    __builtin__.RepeatCondition = game.conditions.RepeatCondition

    # Pathfinder
    __builtin__.pathfinder = game.pathfinder

    # Deathlist
    __builtin__.deathlist = game.deathlist

    # Bans
    __builtin__.ipIsBanned = game.ban.ipIsBanned
    __builtin__.playerIsBanned = game.ban.playerIsBanned
    __builtin__.accountIsBanned = game.ban.accountIsBanned
    __builtin__.addBan = game.ban.addBan

    # Market
    __builtin__.getMarket = game.market.getMarket
    __builtin__.newMarket = game.market.newMarket

    # Creature and Player class. Mainly for test and savings.
    __builtin__.Creature = game.creature.Creature
    __builtin__.Player = game.player.Player
    __builtin__.Monster = game.monster.Monster

    # JSON
    __builtin__.json = otjson

    # Web
    if config.enableWebProtocol:
        import core.service.webserver
        __builtin__.WebPage = core.service.webserver.Page
        from twisted.web.server import NOT_DONE_YET
        __builtin__.NOT_DONE_YET = NOT_DONE_YET

    class Globalizer(object):
        __slots__ = ()
        monster = game.monster
        npc = game.npc
        creature = game.creature
        player = game.player
        map = game.map
        item = game.item
        scriptsystem = game.scriptsystem
        spell = game.spell
        resource = game.resource
        vocation = game.vocation
        const = game.const
        house = game.house
        guild = game.guild
        party = game.party
        errors = game.errors
        chat = game.chat
        deathlist = game.deathlist
        ban = game.ban
        engine = sys.modules["game.engine"] # For consistancy
        market = game.market

    __builtin__.game = Globalizer()

    print "> > Loading global data...",
    for x in (yield globalData):
        if x['type'] == 'json':
            game.engine.globalStorage[x['key']] = otjson.loads(x['data'])
        elif x['type'] == 'pickle':
            game.engine.globalStorage[x['key']] = pickle.loads(x['data'])
        else:
            game.engine.globalStorage[x['key']] = x['data']
    print "%50s\n" % _txtColor("\t[DONE]", "blue")

    print "> > Loading groups...",
    for x in (yield groupData):
        game.engine.groups[x['group_id']] = (x['group_name'], otjson.loads(x['group_flags']))
    print "%60s\n" % _txtColor("\t[DONE]", "blue")

    print "> > Loading guilds...",
    game.guild.load()
    print "%60s\n" % _txtColor("\t[DONE]", "blue")
        
    print "> > Loading bans...",
    game.ban.refresh()
    print "%60s\n" % _txtColor("\t[DONE]", "blue")

    print "> > Loading market...",
    game.market.load()
    print "%55s\n" % _txtColor("\t[DONE]", "blue")
        
    print "> > Loading house data...",
    for x in (yield houseData):
        game.house.houseData[int(x['id'])] = game.house.House(int(x['id']), int(x['owner']),x['guild'],x['paid'],x['name'],x['town'],x['size'],x['rent'],x['data'])
    print "%55s\n" % _txtColor("\t[DONE]", "blue")
        
    # Load scripts
    print "> > Loading scripts...",
    game.scriptsystem.importer()
    game.scriptsystem.get("startup").runSync()
    print "%55s\n" % _txtColor("\t[DONE]", "blue")
        
    # Load map (if configurated to do so)
    if config.loadEntierMap:
        print "> > Loading the entier map...",
        begin = time.time()
        files = glob.glob('%s/%s/*.sec' % (config.dataDirectory, config.mapDirectory))
        for fileSec in files:
            x, y, junk = fileSec.split(os.sep)[-1].split('.')
            x = int(x)
            y = int(y)
            iX = x // game.map.sectorX
            iY = y // game.map.sectorY
            sectorSum = (iX << 11) + iY
            game.map.load(x,y, 0, sectorSum)

        print "%50s\n" % _txtColor("\t[DONE, took: %f]" % (time.time() - begin), "blue")
        
    # Charge rent?
    def _charge(house):
            callLater(config.chargeRentEvery, game.engine.looper, lambda: game.scriptsystem.get("chargeRent").runSync(None, house=house))
            
    for house in game.house.houseData.values():
        if not house.rent or not house.owner: continue
            
        if house.paid < (timer - config.chargeRentEvery):
            game.scriptsystem.get("chargeRent").runSync(None, house=house)
            _charge(house)
        else:
            callLater((timer - house.paid) % config.chargeRentEvery, _charge, house)    
    
    # Loading languages
    if config.enableTranslations:
        print "> > Loading languages... ",
        if language.LANGUAGES:
            print "%s\n" % _txtColor(language.LANGUAGES.keys(), "yellow")
        else:
            print "%s\n" % _txtColor("No languages found, falling back to defaults!", "red")
                
    
    # Load protocols
    print "> > Loading game protocols...",
    for version in config.supportProtocols:
        game.protocol.loadProtocol(version)
    print "%50s\n" % _txtColor("\t[DONE]", "blue")
    
    # Do we issue saves?
    if config.doSaveAll and not IS_IN_TEST:
        print "> > Schedule global save...",
        reactor.callLater(config.saveEvery, game.engine.looper, game.engine.saveAll, config.saveEvery)
        print "%50s\n" % _txtColor("\t[DONE]", "blue")
        
    # Do we save on shutdowns?
    if config.saveOnShutdown:
        game.scriptsystem.get("shutdown").register(lambda **k: game.engine.saveAll(True), False)
        
    # Reset online status on shutdown
    game.scriptsystem.get("shutdown").register(lambda **k: sql.conn.runOperation("UPDATE players SET online = 0"), False)
    # Light stuff
    if not IS_IN_TEST:
        print "> > Turn world time and light on...",
        lightchecks = config.tibiaDayLength / float(config.tibiaFullDayLight - config.tibiaNightLight)

        reactor.callLater(lightchecks, game.engine.looper, game.engine.checkLightLevel, lightchecks)
        print "%45s" % _txtColor("\t[DONE]", "blue")
    
        reactor.callLater(60, game.engine.looper, pathfinder.clear, 60)

    # Now we're online :)
    print _txtColor("Message of the Day: %s" % config.motd, "red")
    log.msg("Loading complete in %fs, everything is ready to roll" % (time.time() - timer))

    game.engine.IS_ONLINE = True

    print "\n\t\t%s\n" % _txtColor("[SERVER IS NOW OPEN!]", "green")
