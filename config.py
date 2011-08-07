# Note: Don't do imports here

# Network:
loginInterface = 'localhost'
loginPort = 7171
gameInterface = 'localhost'
gamePort = 7172

loginMaxConnections = 20
gameMaxConnections = 100

# SQL:
sqlModule = "MySQLdb" # Can be "MySQLdb" or "sqlite3"
sqlUsername = "root"
sqlPassword = ""
sqlDatabase = "ot" # Either a DB name, or file for sqlite3

# Versions:
versionMin = 900
versionMax = 910
versionError = "You must use 9.x"

# MOTD
motd = "PyOT, it's alive!"

# name
name = "PyOT dev server"

########## Advance settings #########
suggestedLoginServerThreadPoolSize = 2 # sqlMinConnections + 1 is often good enough
suggestedGameServerThreadPoolSize = 6 # sqlMaxConnections + 1 is often good enough
suggestedGameServerScriptPoolSize = suggestedGameServerThreadPoolSize * 2# This is only for the scripts! 
sqlMinConnections = 3
sqlMaxConnections = 5

reactorStyle = "default" # Can be "select" (Default, work on "all" platforms), "poll" (faster then select, does not work on Mac OSX), "epoll" (Linux 2.6+ only), "kqueue" (FreeBSD only), "iocp" (Fastest on Windows, may have bugs). Pypy ignore this one!

RSAKeys = {"n":"109120132967399429278860960508995541528237502902798129123468757937266291492576446330739696001110603907230888610072655818825358503429057592827629436413108566029093628212635953836686562675849720620786279431090218017681061521755056710823876476444260558147179707119674283982419152118103759076030616683978566631413",
"e":"65537",
"d":"46730330223584118622160180015036832148732986808519344675210555262940258739805766860224610646919605860206328024326703361630109888417839241959507572247284807035235569619173792292786907845791904955103601652822519121908367187885509270025388641700821735345222087940578381210879116823013776808975766851829020659073",
"p":"14299623962416399520070177382898895550795403345466153217470516082934737582776038882967213386204600674145392845853859217990626450972452084065728686565928113",
"q":"7630979195970404721891201847792002125535401292779123937207447574596692788513647179235335529307251350570728407373705564708871762033017096809910315212884101"}

maxLengthOfSay = 255 # maximum length of what the client might say
debugItems = True # Print extra data about items

checkAdler32 = False # Disable this might speed things up a bit
loadEntierMap = False # Load all the sectors, useful for debug and benchmarking
useNumpy = False # Use numpy to deal with map array, preallocating itself. This is most memory effective without causing problems, but numpy itself is HUGE. It use like 20MB of memory. The entier map (on my system) takes only 11MB in this mode.
stackTiles = True # Sacrefice loading time for the sake of memory usage

sayRange = (10,8)
yellRange = (18, 14)
itemMaxClientId = 12816
itemMaxServerId = 12844
