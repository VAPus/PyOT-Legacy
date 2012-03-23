# Note: Don't do imports here

# Network:
loginInterface = '' # Leave blank to accept connections on any hostname
loginPort = 7171
gameInterface = '' # Leave blank to accept connections on any hostname
gamePort = 7172

# Server ips, for the loginserver
servers = {0 : ('127.0.0.1', "PyOT dev server")} # WORLD_ID -> (ip, name)

# IPs allowed to use the execute protocol (usually things like web servers). ONLY trusted hosts, they can remove system files from this!
executeProtocolIps = ('127.0.0.1',)
executeProtocolAuthKeys = ("myAuthKey",) # Add keys here if you will demand authorization
loginMaxConnections = 20
gameMaxConnections = 100

# SQL:
sqlModule = "MySQLdb" # Can be "MySQLdb" (Mysql), "oursql" (a more Modern implant of MySQLdb, tho, slower), "pymysql" (Mysql using ctypes, slower on CPython), mysql-ctypes, or "sqlite3"
sqlUsername = "root"
sqlPassword = ""
sqlDatabase = "ot" # Either a DB name, or file for sqlite3
sqlHost = "localhost"
sqlDebug = False # Send debug messages to the console

# Use socket from libmysqlclient, works ONLY if sqlHost == localhost
sqlSocket = None

# Alternative:
# Fedora/CentOS/RHEL
#sqlSocket = "/var/lib/mysql/mysql.sock"
# Ubuntu/Kubuntu/Debian
# sqlSocket = "/var/run/mysql/mysql.sock"
# Others:
#sqlSocket = "/var/run/mysqld/mysqld.sock"

# LoginServer, seperate or integrated? This allows you to let the game server handle the loginserver. Doesn't stack very well when using multi server.
letGameServerRunTheLoginServer = True

# Versions:
versionMin = 860
versionMax = 945
versionError = "You must use 8.6-9.45"
supportProtocols = (860, 861, 862, 870, 910, 920, 931, 940, 941, 942, 943, 944, 945) # We support these main branches + compatible protocols to them

# MOTD
motd = "PyOT, it's alive!"

# Walking
diagonalWalkCost = 3

# Soulgain timer
soulGain = 240 # 4 minutes

# Stamina
maxStamina = 42 * 60 # 42 hours, higher won't be displayed in client do to debug, but it will exist virtually
noStaminaNoExp = True

# Melee
meleeAttackSpeed = 2 # 2 seconds, this affect both monsters and players. TODO: Configurable per vocation
monsterMeleeFactor = 1 # 1x damage

# Spell and rune
runeCastDelay = 1 # Set to 0 to disable the delay.

# Monster behavior
monsterWalkBack = False # Walk or Teleport back to spawn point
monsterWalkPer = 2 # Amount of seconds between walks without target.
monsterNeverSkipWalks = True # This makes monsters always calculate a new rute if it runs into solid tiles etc. Walking will be smooth
monsterStairHops = False # Allow monsters to walk up and down stairs

# Outfits
playerCanChangeOutfit = True
playerCanChangeColor = True
playerCanWearAllOutfits = False
playerCanUseAllMounts = False

# Loot / Drop
lootDropRate = 1
lootMaxRate = 1
lootInAlphabeticalOrder = True # Order loot in alphabetical order just like real tibia
stockLootInBagsIfNeeded = True # If amount of items > corpseSize, then append a bag, note: bags does stack as the first items, not alphabetically. 
stockLootBagId = 1987 # Id of the bags to append

# Experince
experienceRate = 1
experienceMessageColor = 215 # Between 1 or 255, else debug

# Map cleaning & unloading
# Note: All dropped items on the map will be removed, all creatures will (hopefully) despawn etc
performSectorUnload = True
performSectorUnloadEvery = 900 # 15 minutes is good

# Save system
doSaveAll = True # Issue saves
saveEvery = 300 # in seconds. Even down to a few seconds won't really make server lag since it's async, but you will definitly risk binding up sql connections if your below 1second, this in turn can cause lag
saveOnShutdown = True # Issue saves on shutdowns

# Tibia day
tibiaTimeOffset = 1200 # This is used as a base time for when the server started. If day is 3600, this means the clock will be 8 when the server starts
tibiaDayLength = 3600 # One hour
tibiaDayFullLightStart = 14
tibiaDayFullLightEnds = 20
tibiaFullDayLight = 215 # Highest light level
tibiaNightLight = 40 # Lowest light level

# Mounts
allowMounts = True
applyMountSpeedChange = True

# Game modes
playerWalkthrough = False # can also be modified in scripts
creatureWalkthrough = False # can also be modified in scripts
playerIsPushable = True

# Spawn
tryToSpawnCreaturesNextToEachother = True # Try the sides of a spawn field if there is a creature on top of them
tryToSpawnCreatureRegardlessOfCreatures = False # Try to spawn creatures on top of eachother, this and previous option doesn't stack.

# Mailboxes
maxMails = 20
maxMailsWithin = 600 # 10min, default on tibia as of 9.aug

# Questlog
sendTutorialSignalUponQuestLogUpdate = True # This is a non-cipsoft feature originally thought up by Big Vamp.

# Psyco
# Psyco can give a speed up so long you have psyco installed, doesn't work on 64-bit python, nor anything other than CPython.
# It's not much, and it also increase memory usage
tryPsyco = False

# Auto Cython
# Cython makes c code and compile it out of the python code which still keeping most of the python code compatible. DO NOT STACK WELL WITH tryPsyco!
tryCython = False

# Item cache
# This reduce the time it takes to start the server (by about 0.1s), but in turn, it won't use items from the DB whenever a cache file exists.
# This also make item reloading impossible (will require restart and removal of the cache file)
itemCache = False

# Houses
chargeRentEvery = 30 * 86400 # Every 30 days

# Critical hits:
criticalHitRate = 5 # In %
criticalHitMultiplier = 2 # Multiplier for the damage

# Useful options for war system.
anyAccountWillDo = False
anyAccountPlayerMap = ("Random Test Character", 0),  # (name, world_id)...

# Hotkeys
enableHotkey = True

# Marketplace
enableMarket = True # It works for 9.44+ only. Lower versions might not access it.

# Pathfinder
# MIGHT BE BUGGY, NOT WELL TESTED!
findDiagonalPaths = False # Disable this will make the pathfinder somewhat 10-15%

########## Advance settings #########
suggestedLoginServerThreadPoolSize = 2 # sqlMinConnections + 1 is often good enough
suggestedGameServerThreadPoolSize = 6 # sqlMaxConnections + 1 is often good enough
sqlMinConnections = 3
sqlMaxConnections = 5

reactorStyle = "default" #"default" # Can be "select" (work on "all" platforms), "poll" (faster then select, does not work on Mac OSX), "epoll" (Linux 2.6+ only), "kqueue" (FreeBSD only), "iocp" (Fastest on Windows, may have bugs). Leave it to "default" to allow twisted to choose

RSAKeys = {"n":"109120132967399429278860960508995541528237502902798129123468757937266291492576446330739696001110603907230888610072655818825358503429057592827629436413108566029093628212635953836686562675849720620786279431090218017681061521755056710823876476444260558147179707119674283982419152118103759076030616683978566631413",
"e":"65537",
"d":"46730330223584118622160180015036832148732986808519344675210555262940258739805766860224610646919605860206328024326703361630109888417839241959507572247284807035235569619173792292786907845791904955103601652822519121908367187885509270025388641700821735345222087940578381210879116823013776808975766851829020659073",
"p":"14299623962416399520070177382898895550795403345466153217470516082934737582776038882967213386204600674145392845853859217990626450972452084065728686565928113",
"q":"7630979195970404721891201847792002125535401292779123937207447574596692788513647179235335529307251350570728407373705564708871762033017096809910315212884101"}

maxLengthOfSay = 255 # maximum length of what the client might say
debugItems = True # Print extra data about items

checkAdler32 = False # Disable this might speed things up a bit
loadEntierMap = False # Load all the sectors, useful for debug and benchmarking
useNumpy = False # Use numpy to deal with map array and item array, preallocating itself. This is most memory effective without causing problems, but numpy itself is HUGE. It use like 20MB of memory. The entier map (on my system) takes only 11MB in this mode. Also, it doesn't work with Pypy until pypy 1.8
# Disabled for now, breaks house support
stackTiles = False # Sacrefice loading time for the sake of memory usage
stackItems = True

whisperRange = (1, 1)
whisperNoise = "pspspsps"
sayRange = (9, 7)
yellRange = (18, 14)
itemMaxClientId = 12905
itemMaxServerId = 13983

# JSON Library
jsonLibrary = "cjson" # cjson, ujson, json or simplejson

# Drawing speed
# Drawing speed is the overall delay of all actions, minimum value PyOT is able to handle nicely (on Windows) is 15, while you can easily have it down to 1 on Linux,
# keep in mind tho that having a value below 10 might cause client out-of-syncs. Default on cipsoft/otserv is 50. We use 25 because we're abit cooler!
drawingSpeed = 25

# Formulas
levelFormula = lambda x: 50*(x**2)-150*x+200
totalExpFormula = lambda x: (50.0/3)*x*((x-3)*x+8)

# This formula is too complex to put into a lambda
from math import log,floor
def levelFromExpFormula(y): # y = experience
    l1 = ((3 ** 0.5)*(((243*(y**2))-(48600*y)+3680000) ** 0.5)+(27*y)-2700) ** (1.0/3)
    l2 = 30**(2.0/3)
    l3 = 5 * 10**(2.0/3)
    l4 = (3 ** (1.0/3)) * l1
    return floor(round((l1/l2)-(l3/l4)+2, 10)) # Use floor to get the level, and not the progress (eg 10.7 instead of 10), we only want 10 in that case.

magicLevelFormula = lambda a,b: 1600*(b**a)
totalMagicLevelFormula = lambda a,b:(1600*((b**a)-1))/(b-1) # a = level, b = vocation constant
magicLevelFromManaFormula = lambda n,b: floor(round((log((1.0+n+(1600.0/b)) / 1600.0) + log(b)) / (log(b)), 8)) # n = mana, b = vocation constant
skillFormula = lambda a,b: 50*(b**(a-10))
magicPower = lambda lvl,mlvl: max(1,(lvl + 4 * mlvl) / 100)
fishingFormula = lambda x: 20*(1.1)**(x-10)
meleeDamage = lambda attack,skill,level,factor: (0.085*factor*attack*skill)+(level/5)
