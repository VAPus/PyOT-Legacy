byKiller = {}
byVictim = {}

loadedDeathIds = set()

lastId = 0

# This function set lastId to the lastId in the database, so our new deathEntries have the same id for proper indexing.
@inlineCallbacks
def prepare():
    global lastId
    for entry in (yield sql.runQuery("SELECT MAX(death_id) FROM pvp_deaths")):
        lastId = entry[0]
        
    if lastId == None: # No entries.
        lastId = 0
        
class DeathEntry(object):
    def __init__(self, killerId, victimId, unjustified, revenged=0, _time=None, war_id=0, deathId=0):
        if not _time:
            _time = time.time()
        self.id = deathId
        self.killerId = killerId
        self.victimId = victimId
        self.time = _time
        self.unjustified = unjustified
        self.revenged = revenged
        self.warId = war_id
        
    def saveQuery(self):
        return "(%s, %s, %s, %s, %s, %s, %s)" % (self.id, self.killerId, self.victimId, self.unjustified, self.time, self.revenged, self.warId)

@inlineCallbacks
def loadDeathList(playerId):
    global byVictim, byKiller, loadedDeathIds
    query = yield sql.runQuery("SELECT death_id, killer_id, victim_id, unjust, `time`, revenged, war_id FROM pvp_deaths WHERE killer_id = %s OR victim_id = %s AND `time` >= %s", (playerId, playerId, int(time.time() - (config.deathListCutoff * 3600 * 24))))
    
    for entry in query:
        if entry[0] in loadedDeathIds: continue
        
        deathEntry = DeathEntry(entry[1], entry[2], entry[3], entry[5], entry[4], entry[6], entry[0])
        
        try:
            byVictim[entry[2]].append(deathEntry)
        except:
            byVictim[entry[2]] = [deathEntry]
            
        try:
            byKiller[entry[1]].append(deathEntry)
        except:
            byKiller[entry[1]] = [deathEntry]
            
        loadedDeathIds.add(entry[0])
        
def getSkull(playerId):
    if not playerId in byKiller: return SKULL_NONE
    
    whiteSkull = False
    redEntries = {}
    blackEntries = {}
    
    for i in config.redSkullUnmarked.keys():
        redEntries[i] = 0
        
    for i in config.blackSkullUnmarked.keys():
        blackEntries[i] = 0
        
    # Try to check for white skull and sort entries in red and black.
    whiteTime = time.time() - config.whiteSkull 
    for deathEntry in byKiller[playerId]:
        if deathEntry.time > whiteTime:
            whiteSkull = True
            
        for t in redEntries:
            if deathEntry.time > time.time() - t:
                redEntries[t] += 1
                
        for t in blackEntries:
            if deathEntry.time > time.time() - t:
                blackEntries[t] += 1
                
    # Now, check what kid of skulls he qualified for, try black first.
    for t in blackEntries:
        if blackEntries[t] >= config.blackSkullUnmarked[t]:
            return SKULL_BLACK
        
    # Now redEntries
    for t in redEntries:
        if redEntries[t] >= config.redSkullUnmarked[t]:
            return SKULL_RED
        
    # Now white
    if whiteSkull:
        return SKULL_WHITE
   
    # None
    return SKULL_NONE

def addEntry(deathEntry):
    global lastId
    deathEntry.id = lastId + 1
    lastId += 1
    
    sql.runOperation("INSERT INTO pvp_deaths(`death_id`, `killer_id`, `victim_id`, `unjust`, `time`, `revenged`, `war_id`) VALUES %s;" % deathEntry.saveQuery())
    
    try:
        byKiller[deathEntry.killerId].append(deathEntry)
    except:
        byKiller[deathEntry.killerId] = [deathEntry]
    try:
        byVictim[deathEntry.victimId].append(deathEntry)
    except:
        byVictim[deathEntry.victimId] = [deathEntry]
    loadedDeathIds.add(deathEntry.id)