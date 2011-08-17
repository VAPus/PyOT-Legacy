# The script system
from twisted.internet import reactor, threads
from twisted.python.threadpool import ThreadPool
import config
import weakref
import sys

modPool = []
globalScripts = {}

class Scripts(object):
    __slots__ = ('scripts')
    def __init__(self):
        self.scripts = []
        
    def reg(self, callback):
        self.scripts.append(callback)
        
    def unreg(self, callback):
        self.scripts.remove(callback)

    def run(self, creature, end=None, **kwargs):
        scriptPool.callInThread(self._run, creature, end, **kwargs)
        
    def _run(self, creature, end=None, **kwargs):
        ok = True
        for script in self.scripts:
            ok = script(creature=creature, **kwargs)
            if not (ok if ok is not None else True):
               break
        if end and (ok if ok is not None else True):
            end()
            
class TriggerScripts(object):
    __slots__ = ('scripts')
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
        
    def run(self, trigger, creature, end=None, **kwargs):
        scriptPool.callInThread(self._run, trigger, creature, end, **kwargs)

    def unregCallback(self, callback):
        for s in self.scripts:
            for c in self.scripts[s]:
                if c == callback:
                    del c
            if not len(self.scripts[s]):
                del self.scripts[s]
                
    def _run(self, trigger, creature, end, **kwargs):
        ok = True
        if not trigger in self.scripts:
            return end()
        for script in self.scripts[trigger][:]:
            func = script()
            if func:
                ok = func(creature=creature, **kwargs)
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
    __slots__ = ('scripts', 'thingScripts')
    def __init__(self):
        self.scripts = {}
        self.thingScripts = {}
        
    def reg(self, id, callback, toid=None):
        if not toid:
            if type(id) in (tuple, list):
                func = weakref.ref(callback, self.unregCallback)
                for xid in id:
                    if not xid in self.scripts:
                        self.scripts[xid] = [func]
                    else:
                        self.scripts[xid].append(func)                
            elif type(id) != int:
                # This ensures we remove the script object if the object disappear
                id = weakref.ref(id, self.unregAll) 
                
                if not id in self.thingScripts:
                    self.thingScripts[id] = []
                self.thingScripts[id].append(weakref.ref(callback, self.unregCallback ))
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
                
    def run(self, thing, creature, end=None, **kwargs):
        scriptPool.callInThread(self._run, thing, creature, end, False, **kwargs)
    
    def runDefer(self, thing, creature, end=None, **kwargs):
        return threads.deferToThreadPool(reactor, scriptPool, self._run, thing, creature, end, True, **kwargs)

    def runSync(self, thing, creature, end=None, **kwargs):
        return self._run(thing, creature, end, True, **kwargs)
        
    def _run(self, thing, creature, end, returnVal, **kwargs):
        ok = True
        
        
        for weakthing in self.thingScripts:
            if weakthing() == thing:
                for script in self.thingScripts[weakthing][:]:
                    func = script()
                    if func:
                        ok = func(creature=creature, thing=thing, **kwargs)
                        if not ok is not False:
                            break
                    else:
                        try:
                            self.thingScripts[weakthing].remove(script) 
                        except:
                            pass
            elif weakthing() == None:
                del self.thingScripts[weakthing]
        if ok and thing.thingId() in self.scripts:
            print "_run thingId"
            for script in self.scripts[thing.thingId()][:]:
                func = script()
                print "func: ", func
                if func:
                    ok = func(creature=creature, thing=thing, **kwargs)
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
                            ok = func(creature=creature, thing=thing, **kwargs)
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
globalScripts["talkaction"] = TriggerScripts()
globalScripts["talkactionFirstWord"] = TriggerScripts()
globalScripts["login"] = Scripts()
globalScripts["logout"] = Scripts()
globalScripts["use"] = ThingScripts()
globalScripts["useWith"] = ThingScripts()
globalScripts["walkOn"] = ThingScripts()
globalScripts["walkOff"] = ThingScripts()
globalScripts["preWalkOn"] = ThingScripts()
globalScripts["addMapItem"] = ThingScripts()
globalScripts["lookAt"] = ThingScripts()

# Begin the scriptPool stuff, note: we got to add support for yield for the SQL stuff!
scriptPool = ThreadPool(5, config.suggestedGameServerScriptPoolSize)
scriptPool.start()
reactor.addSystemEventTrigger('before','shutdown',scriptPool.stop)

def handleModule(name):
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
    
    modPool.append([name, modules])
        
def importer():
    handleModule("spells")
    handleModule("monsters")
    handleModule("npcs")
    handleModule("scripts")

def reimporter():
    import game.spell
    game.spell.clear()
    
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
def get(type):
    return globalScripts[type]
    
def reg(type, *argc, **kwargs):
    globalScripts[type].reg(*argc, **kwargs)
