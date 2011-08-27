# Note: Don't do imports here

# Network:
loginInterface = 'localhost'
loginPort = 7171
gameInterface = 'localhost'
gamePort = 7172

# Server ips, for the loginserver
servers = {0 : '127.0.0.1'}

loginMaxConnections = 20
gameMaxConnections = 100

# SQL:
sqlModule = "MySQLdb" #"MySQLdb" # Can be "MySQLdb" (Mysql), "pymysql" (Mysql using ctypes, slower on CPython) or "sqlite3"
sqlUsername = "root"
sqlPassword = ""
sqlDatabase = "ot" # Either a DB name, or file for sqlite3
sqlHost = "localhost"
sqlSocket = "/var/run/mysqld/mysqld.sock"

# Versions:
versionMin = 900
versionMax = 910
versionError = "You must use 9.x"

# MOTD
motd = "PyOT, it's alive!"

# name
name = "PyOT dev server"

# Walking
diagonalWalkCost = 3

# Soulgain timer
soulGain = 240 # 4 minutes

# Stamina
maxStamina = 42 * 60 # 42 hours, higher won't be displayed in client do to debug, but it will exist virtually
noStaminaNoExp = True

# Melee
meleeAttackSpeed = 2 # 2 seconds, this affect both monsters and players. TODO: Configurable per vocation and per monster.
monsterMeleeFactor = 1 # 1x damage

# Monster behavior
monsterWalkBack = False # Walk or Teleport back to spawn point
monsterWalkPer = 3 # Amount of seconds between walks without target
monsterNeverSkipWalks = True # This makes monsters always calculate a new rute if it runs into solid tiles etc. Walking will be smooth

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
performSectorUnloadEvery = 300 # 5 minutes is good

########## Advance settings #########
suggestedLoginServerThreadPoolSize = 2 # sqlMinConnections + 1 is often good enough
suggestedGameServerThreadPoolSize = 6 # sqlMaxConnections + 1 is often good enough
suggestedGameServerScriptPoolSize = suggestedGameServerThreadPoolSize * 2# This is only for the scripts! 
sqlMinConnections = 3
sqlMaxConnections = 5

reactorStyle = "default" # Can be "select" (work on "all" platforms), "poll" (faster then select, does not work on Mac OSX), "epoll" (Linux 2.6+ only), "kqueue" (FreeBSD only), "iocp" (Fastest on Windows, may have bugs). Leave it to "default" to allow twisted to choose

RSAKeys = {"n":"109120132967399429278860960508995541528237502902798129123468757937266291492576446330739696001110603907230888610072655818825358503429057592827629436413108566029093628212635953836686562675849720620786279431090218017681061521755056710823876476444260558147179707119674283982419152118103759076030616683978566631413",
"e":"65537",
"d":"46730330223584118622160180015036832148732986808519344675210555262940258739805766860224610646919605860206328024326703361630109888417839241959507572247284807035235569619173792292786907845791904955103601652822519121908367187885509270025388641700821735345222087940578381210879116823013776808975766851829020659073",
"p":"14299623962416399520070177382898895550795403345466153217470516082934737582776038882967213386204600674145392845853859217990626450972452084065728686565928113",
"q":"7630979195970404721891201847792002125535401292779123937207447574596692788513647179235335529307251350570728407373705564708871762033017096809910315212884101"}

maxLengthOfSay = 255 # maximum length of what the client might say
debugItems = True # Print extra data about items

checkAdler32 = False # Disable this might speed things up a bit
loadEntierMap = False # Load all the sectors, useful for debug and benchmarking
useNumpy = False # Use numpy to deal with map array and item array, preallocating itself. This is most memory effective without causing problems, but numpy itself is HUGE. It use like 20MB of memory. The entier map (on my system) takes only 11MB in this mode. Also, it doesn't work with Pypy until pypy 1.6
stackTiles = True # Sacrefice loading time for the sake of memory usage

whisperRange = (1, 1)
sayRange = (9, 7)
yellRange = (18, 14)
itemMaxClientId = 12816
itemMaxServerId = 12844

# Drawing speed
# Drawing speed is the overall delay of all actions, minimum value PyOT is able to handle nicely (on Windows) is 15, while you can easily have it down to 1 on Linux,
# keep in mind tho that having a value below 10 might cause client out-of-syncs. Default on cipsoft/otserv is 50. We use 25 because we're abit cooler!
drawingSpeed = 25

# Formulas
levelFormula = lambda x: 50*(x**2)-150*x+200
totalExpFormula = lambda x: (50*(x**3)-150*(x**2) + 400*x)/3
magicLevelFormula = lambda a,b: 1600*(b**a)
totalMagicLevelFormula = lambda a,b:(1600*(b**a-1))/b-1
skillFormula = lambda a,b: 50*(b**(a-10))
magicPower = lambda lvl,mlvl: max(1,(lvl + 4 * mlvl) / 100)
fishingFormula = lambda x: 20*(1.1)**(x-10)
meleeDamage = lambda attack,skill,level,factor: (0.085*factor*attack*skill)+(level/5)
