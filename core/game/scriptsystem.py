# The script system
from twisted.internet import reactor
from twisted.python.threadpool import ThreadPool
import config
import weakref
import sys

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
        self.scripts[trigger].append(weakref.ref(callback, self.unregCallback))
        
    def unreg(self, trigger, callback):
        for ref in self.scripts[trigger]:
            if ref() == callback:
                self.scripts[trigger].remove(ref)
                print "Found"
            print "Lop"
        if not len(self.scripts[trigger]):
            del self.scripts[trigger]
        
    def run(self, trigger, creature, end=None, *args, **kwargs):
        scriptPool.callInThread(self._run, trigger, creature, end, *args, **kwargs)

    def unregCallback(self, callback):
        for s in self.scripts:
            for c in self.scripts[s]:
                if c == callback:
                    del c
            if not len(self.scripts[s]):
                del self.scripts[s]
                
    def _run(self, trigger, creature, end, *args, **kwargs):
        ok = True
        if not trigger in self.scripts:
            return end()
        for script in self.scripts[trigger][:]:
            func = script()
            if func:
                ok = func(creature, *args, **kwargs)
                if not (ok if ok is not None else True):
                    break
            else:
                try:
                    self.scripts[trigger].remove(script)
                except:
                    pass
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
            self.scripts[id].append(weakref.ref(callback, self.unregCallback ))
        else:
            if not id in self.scripts:
                self.scripts[id] = []
            self.scripts[id].append(weakref.ref(callback, self.unregCallback))

    def unreg(self, id, callback):
        try:
            for ref in self.scripts[id]:
                if ref() == callback:
                    self.scripts[id].remove(ref)

            if not self.scripts[id]:
                del self.scripts[id]
                
        except:
            pass # Nothing

    def unregAll(self, id):
        try:
            del self.scripts[id]
        except:
            pass
     
    def unregCallback(self, callback):
        for s in self.scripts:
            for c in self.scripts[s]:
                if c == callback:
                    del c
            if not len(self.scripts[s]):
                del self.scripts[s]
                
    def run(self, thing, creature, end=None, *args, **kwargs):
        scriptPool.callInThread(self._run, thing, creature, end, *args, **kwargs)
    
    def runSync(self, thing, creature, end=None, *args, **kwargs):
        self._run(thing, creature, end, *args, **kwargs)
        
    def _run(self, thing, creature, end, *args, **kwargs):
        ok = True
        
        if thing in self.scripts:
            for script in self.scripts[thing][:]:
                func = script()
                if func:
                    ok = func(creature, *args, **kwargs)
                    if not ok is not False:
                        break
                else:
                    try:
                        self.scripts[thing].remove(script) 
                    except:
                        pass
        if ok and thing.thingId() in self.scripts:
            for script in self.scripts[thing.thingId()][:]:
                func = script()
                if func:
                    ok = func(creature, *args, **kwargs)
                    if not ok is not False:
                        break
                else:
                    try:
                        self.scripts[thing.thingId()].remove(script) 
                    except:
                        pass   

        if ok:
            for aid in thing.actionIds():
                for script in self.scripts[aid][:]:
                    func = script()
                    if func:
                        ok = func(creature, *args, **kwargs)
                        if not ok is not False:
                            break
                    else:
                        try:
                            self.scripts[aid].remove(script) 
                        except:
                            pass   
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

global modPool
modPool = []
def importer():
    global modPool
    spells = __import__('data.spells', globals(), locals(), ["*"], -1)
    for spell in spells.__all__:
        try:
            if not spell == "__init__":
                sys.modules["data.spells.%s" % spell].init()
        except AttributeError:
            pass
    monsters = __import__('data.monsters', globals(), locals(), ["*"], -1)
    for monster in monsters.__all__:
        try:
            if not monster == "__init__":
                sys.modules["data.monsters.%s" % monster].init()
        except AttributeError:
            pass
    npcs = __import__('data.npcs', globals(), locals(), ["*"], -1)
    for npc in npcs.__all__:
        try:
            if not npc == "__init__":
                sys.modules["data.npcs.%s" % npc].init()
        except AttributeError:
            pass
    scripts = __import__('data.scripts', globals(), locals(), ["*"], -1)
    for script in scripts.__all__:
        try:
            if not script == "__init__":
                sys.modules["data.scripts.%s" % script].init()
        except AttributeError:
            pass
        
    modPool = [["spells", spells], ["monsters", monsters], ["npcs", npcs], ["scripts", scripts]]

def reimporter():
    global modPool
    for mod in modPool:
        # Step 1 reload self
        del mod[1]
        mod.append(__import__('data.%s' % mod[0], globals(), locals(), ["*"], -1))
        
        # Step 1, reload submodules
        for sub in mod[1].__all__:
            try:
                if sub != "__init__":
                    reload(sys.modules["data.%s.%s" % (mod[0], sub)])
            except:
                pass
            
        # Step 3: Rerun init
        for sub in mod[1].__all__:
            try:
                if sub != "__init__":
                    sys.modules["data.%s.%s" % (mod[0], sub)].init()
                    
            except AttributeError:
                pass
                
# This is the function to get events, it should also be a getAll, and get(..., creature)
def get(type, thing=None):
    if not thing:
        return globalScripts[type]
    
