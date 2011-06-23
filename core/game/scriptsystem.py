# The script system
from twisted.internet.defer import inlineCallbacks, deferredGenerator, waitForDeferred, Deferred
from twisted.internet import reactor, threads
from twisted.python.threadpool import ThreadPool
import config
class Scripts:
    def __init__(self):
        self.scripts = []
        
    def reg(self, callback):
        self.scripts.append(callback)
        
    def unreg(self, callback):
        self.scripts.remove(callback)
        
    def _run(self, creature, end, *args, **kwargs):
        ok = True
        for script in self.scripts:
            ok = script(creature, *args, **kwargs)
            if not (ok if ok is not None else True):
               break
        if (ok if ok is not None else True):
            end()
class TriggerScripts:
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
        
    def run(self, trigger, creature, end, *args, **kwargs):
        scriptPool.callInThread(self._run, trigger, creature, end, *args, **kwargs)
    def _run(self, trigger, creature, end, *args, **kwargs):
        ok = True
        if not trigger in self.scripts:
            return end()
        for script in self.scripts[trigger]:
            ok = script(creature, *args, **kwargs)
            if not (ok if ok is not None else True):
               break
        if (ok if ok is not None else True):
            end()
            
# All global events can be initialized here
globalScripts = {}
globalScripts["talkaction"] = TriggerScripts()
globalScripts["talkactionFirstWord"] = TriggerScripts()

# Begin the scriptPool stuff, note: we got to add support for yield for the SQL stuff!
scriptPool = ThreadPool(5, config.suggestedGameServerScriptPoolSize)
scriptPool.start()
reactor.addSystemEventTrigger('before','shutdown',scriptPool.stop)

# This is the function to get events, it should also be a getAll, and get(..., creature)
def get(type, creature=None):
    if not creature:
        return globalScripts[type]
    
