# The script system
from twisted.internet import reactor
from twisted.python.threadpool import ThreadPool
import config
import weakref

class Scripts(object):
    def __init__(self):
        self.scripts = []
        
    def reg(self, callback):
        self.scripts.append(callback)
        
    def unreg(self, callback):
        self.scripts.remove(callback)

    def run(self, creature, end=None, *args, **kwargs):
        scriptPool.callInThread(self._run, creature, end, *args, **kwargs)
        
    def _run(self, creature, end=None, *args, **kwargs):
        ok = True
        for script in self.scripts:
            ok = script(creature, *args, **kwargs)
            if not (ok if ok is not None else True):
               break
        if end and (ok if ok is not None else True):
            end()
            
class TriggerScripts(object):
    def __init__(self):
        self.scripts = {}
        
        
    def reg(self, trigger, callback):
        if not trigger in self.scripts:
            self.scripts[trigger] = []
        self.scripts[trigger].append(callback)
        
    def unreg(self, trigger, callback):
        self.scripts[trigger].remove(callback)
        if not len(self.scripts[trigger]):
            del self.scripts[trigger]
        
    def run(self, trigger, creature, end=None, *args, **kwargs):
        scriptPool.callInThread(self._run, trigger, creature, end, *args, **kwargs)
        
    def _run(self, trigger, creature, end, *args, **kwargs):
        ok = True
        if not trigger in self.scripts:
            return end()
        for script in self.scripts[trigger]:
            ok = script(creature, *args, **kwargs)
            if not (ok if ok is not None else True):
               break
        if end and (ok if ok is not None else True):
            end()

# Thing scripts is a bit like triggerscript except it might use id ranges etc
class ThingScripts(object):
    def __init__(self):
        self.scripts = {}
        
    def reg(self, id, callback, toid=None):
        if type(id) != int:
            # This ensures we remove the script object if the object disappear
            id = weakref.ref(id, self.unregAll) 
            
        if not id in self.scripts:
            self.scripts[id] = []
        self.scripts[id].append(callback)

    def unreg(self, id, callback):
        try:
            self.scripts[id].remove(callback)
            if not self.scripts[id]:
                del self.scripts[id]
                
        except:
            pass # Nothing

    def unregAll(self, id):
        try:
            del self.scripts[id]
        except:
            pass
    def run(self, thing, creature, end=None, *args, **kwargs):
        scriptPool.callInThread(self._run, thing, creature, end, *args, **kwargs)
    
    def runSync(self, thing, creature, end=None, *args, **kwargs):
        self._run(thing, creature, end, *args, **kwargs)
        
    def _run(self, thing, creature, end, *args, **kwargs):
        ok = True
        
        if thing in self.scripts:
            for script in self.scripts[thing]:
                ok = script(creature, *args, **kwargs)
                if not ok is not False:
                    break
                    
        if ok and thing.thingId() in self.scripts:
            for script in self.scripts[thing.thingId()]:
                ok = script(creature, *args, **kwargs)
                if not ok is not False:
                    break
                    
        if end and ok is not False:
            return end()
            
# All global events can be initialized here
globalScripts = {}
globalScripts["talkaction"] = TriggerScripts()
globalScripts["talkactionFirstWord"] = TriggerScripts()
globalScripts["login"] = Scripts()
globalScripts["logout"] = Scripts()
globalScripts["use"] = ThingScripts()
globalScripts["walkOn"] = ThingScripts()
globalScripts["walkOff"] = ThingScripts()
globalScripts["preWalkOn"] = ThingScripts()
globalScripts["lookAt"] = ThingScripts()

# Begin the scriptPool stuff, note: we got to add support for yield for the SQL stuff!
scriptPool = ThreadPool(5, config.suggestedGameServerScriptPoolSize)
scriptPool.start()
reactor.addSystemEventTrigger('before','shutdown',scriptPool.stop)

modPool = []
def importer():
    spells = __import__('data.spells', globals(), locals(), ["*"], -1)
    for spell in spells.__all__:
        try:
            sys.modules["data.spells.%s" % spell].init()
        except NameError:
            pass
    monsters = __import__('data.monsters', globals(), locals(), ["*"], -1)
    for monster in monsters.__all__:
        try:
            sys.modules["data.monsters.%s" % monster].init()
        except NameError:
            pass
    npcs = __import__('data.npcs', globals(), locals(), ["*"], -1)
    for npc in npcs.__all__:
        try:
            sys.modules["data.npc.%s" % npc].init()
        except NameError:
            pass
    scripts = __import__('data.scripts', globals(), locals(), ["*"], -1)
    for script in scripts.__all__:
        try:
            sys.modules["data.scripts.%s" % spell].init()
        except NameError:
            pass
        
    modPool = [spells, monsters, npcs, scripts]
    
# This is the function to get events, it should also be a getAll, and get(..., creature)
def get(type, thing=None):
    if not thing:
        return globalScripts[type]
    
