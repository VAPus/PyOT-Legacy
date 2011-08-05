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

    def regFirst(self, trigger, callback):
        if not trigger in self.scripts:
            self.reg(trigger, callback)
        else:
            self.scripts[trigger].insert(0, weakref.ref(callback, self.unregCallback))
            
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
        if not toid:
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
        else:
            func = weakref.ref(callback, self.unregCallback)
            for xid in xrange(id, toid+1):
                if not xid in self.scripts:
                    self.scripts[xid] = [func]
                else:
                    self.scripts[xid].append(func)
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
        scriptPool.callInThread(self._run, thing, creature, end, False, *args, **kwargs)
    
    def runSync(self, thing, creature, end=None, *args, **kwargs):
        return self._run(thing, creature, end, True, *args, **kwargs)
        
    def _run(self, thing, creature, end, returnVal, *args, **kwargs):
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
                if aid in self.scripts:
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
        if not returnVal and end and ok is not False:
            return end()
        elif returnVal:
            return ok if type(ok) != bool else None
            
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
globalScripts["addMapItem"] = ThingScripts()
globalScripts["lookAt"] = ThingScripts()

# Begin the scriptPool stuff, note: we got to add support for yield for the SQL stuff!
scriptPool = ThreadPool(5, config.suggestedGameServerScriptPoolSize)
scriptPool.start()
reactor.addSystemEventTrigger('before','shutdown',scriptPool.stop)

global modPool
modPool = []

def handleModule(name):
    global modPool
    try:
        modules = __import__('data.%s' % name, globals(), locals(), ["*"], -1)
    except:
        import traceback
        t = traceback.print_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        if t:
            print t
        return
    for module in modules.__all__:
        try:
            if not module == "__init__":
                sys.modules["data.%s.%s" % (name, module)].init()
        except AttributeError:
            pass
    
    try:
        modules.paths
    except:
        pass
    else:
        for subModule in modules.paths:
            handleModule("%s.%s" % (name, subModule))
    
    modPool.append((name, modules))
        
def importer():
    handleModule("spells")
    handleModule("monsters")
    handleModule("npcs")
    handleModule("scripts")

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
    
