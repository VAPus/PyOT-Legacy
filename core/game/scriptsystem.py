# The script system
from twisted.internet import reactor, threads, defer
from twisted.python.threadpool import ThreadPool
import config
import weakref
import sys
import time

modPool = []
globalScripts = {}

class Value(object):
    pass

class Scripts(object):
    __slots__ = ('scripts')
    def __init__(self):
        self.scripts = []
        
    def reg(self, callback, weakfunc=True):
        if weakfunc:
            func = weakref.proxy(callback, self.unregCallback)
        else:
            func = callback
        self.scripts.append(func)
        
    def unreg(self, callback):
        self.scripts.remove(callback)
    
    def unregCallback(self, callback):
        self.scripts.remove(callback)
                
    def run(self, creature, end=None, **kwargs):
        scriptPool.callInThread(self._run, creature, end, **kwargs)

    def runSync(self, creature, end=None, **kwargs):
        return self._run(creature, end, **kwargs)

    def runDefer(self, creature, end=None, **kwargs):
        return threads.deferToThreadPool(reactor, scriptPool, self._run, creature, end, **kwargs)
        
    def _run(self, creature, end=None, **kwargs):
        ok = True
        for func in self.scripts:
            if func:
                ok = func(creature=creature, **kwargs)
                if not (ok if ok is not None else True):
                    break
            else:
                self.scripts.remove(func)
                
        if end and (ok if ok is not None else True):
            end()
        else:
            return ok

class NCScripts(Scripts):
    def run(self, end=None, **kwargs):
        scriptPool.callInThread(self._run, end, **kwargs)

    def runSync(self, end=None, **kwargs):
        return self._run(end, **kwargs)

    def runDefer(self, end=None, **kwargs):
        return threads.deferToThreadPool(reactor, scriptPool, self._run, end, **kwargs)
    def _run(self, end=None, **kwargs):
        ok = True
        for func in self.scripts:
            if func:
                ok = func(**kwargs)
                if not (ok if ok is not None else True):
                    break
            else:
                self.scripts.remove(func)
                
        if end and (ok if ok is not None else True):
            end()
        else:
            return ok
                
class TriggerScripts(object):
    __slots__ = ('scripts')
    def __init__(self):
        self.scripts = {}
        
        
    def reg(self, trigger, callback, weakfunc=True):
        if weakfunc:
            func = weakref.proxy(callback, self.unregCallback)
        else:
            func = callback
            
        if not trigger in self.scripts:
            self.scripts[trigger] = []
        self.scripts[trigger].append(func)
        print "%s - %s" % (trigger, callback)
        
    def regFirst(self, trigger, callback, weakfunc=True):
        if not trigger in self.scripts:
            self.reg(trigger, callback, weakfunc)
        else:
            if weakfunc:
                func = weakref.proxy(callback, self.unregCallback)
            else:
                func = callback
            self.scripts[trigger].insert(0, func)
            
    def unreg(self, trigger, callback):
        self.scripts[trigger].remove(callback)

        if not len(self.scripts[trigger]):
            del self.scripts[trigger]
        
    def run(self, trigger, creature, end=None, **kwargs):
        scriptPool.callInThread(self._run, trigger, creature, end, **kwargs)

    def runSync(self, trigger, creature, end=None, **kwargs):
        return self._run(trigger, creature, end, **kwargs)
        
    def unregCallback(self, callback):
        remove = []
        for s in self.scripts:
            try:
                self.scripts[s].remove(callback)
            except:
                pass
            
            if not len(self.scripts[s]):
                remove.append(s)
        
        for s in remove:
            del self.scripts[s]
                
    def _run(self, trigger, creature, end, **kwargs):
        ok = True
        print self.scripts.keys()
        if not trigger in self.scripts:
            return end() if end else None
            
        for func in self.scripts[trigger][:]:
            if func:
                ok = func(creature=creature, **kwargs)
                if not (ok if ok is not None else True):
                    break
            else:
                try:
                    self.scripts[trigger].remove(func)
                except:
                    pass
        if end and (ok if ok is not None else True):
            end()
        return ok

# Thing scripts is a bit like triggerscript except it might use id ranges etc
class ThingScripts(object):
    __slots__ = ('scripts', 'thingScripts')
    def __init__(self):
        self.scripts = {}
        self.thingScripts = {}

    def haveScripts(self, id):
        if type(id) in (list, tuple, set):
            for i in id:
                if i in self.scripts:
                    return True
                    
        elif id in self.scripts or (type(id) not in (int, long, str) and id in self.thingScripts):
            return True
        else:
            return False
            
    def reg(self, id, callback, weakfunc=True):
        if weakfunc:
            func = weakref.proxy(callback, self.unregCallback)
        else:
            func = callback
            
        if type(id) in (tuple, list, set):
            for xid in id:
                if not xid in self.scripts:
                    self.scripts[xid] = [func]
                else:
                    self.scripts[xid].append(func)                
        elif type(id) not in (int, long, str):
            # This ensures we remove the script object if the object disappear
            id = weakref.ref(id, self.unregAll) 
                
            if not id in self.thingScripts:
                self.thingScripts[id] = [func]
            else:
                self.thingScripts[id].append(func)
        else:
            if not id in self.scripts:
                self.scripts[id] = [func]
            else:
                self.scripts[id].append(func)

    def regFirst(self, id, callback, weakfunc=True):
        if weakfunc:
            func = weakref.proxy(callback, self.unregCallback)
        else:
            func = callback
            
        if type(id) in (tuple, list, set):
            for xid in id:
                if not xid in self.scripts:
                    self.scripts[xid] = [func]
                else:
                    self.scripts[xid].insert(0, func)                
        elif type(id) not in (int, long, str):
            # This ensures we remove the script object if the object disappear
            id = weakref.ref(id, self.unregAll) 
                
            if not id in self.thingScripts:
                self.thingScripts[id] = [func]
            else:
                self.thingScripts[id].insert(0, func)
        else:
            if not id in self.scripts:
                self.scripts[id] = [func]
            else:
                self.scripts[id].insert(0, func)
                    
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
     
    def unregCallback(self, callback):
        remove = []
        for s in self.scripts:
            try:
                self.scripts[s].remove(callback)
            except:
                pass
            
            if not len(self.scripts[s]):
                remove.append(s)
        
        for s in remove:
            del self.scripts[s]
                
    def run(self, thing, creature, end=None, **kwargs):
        scriptPool.callInThread(self._run, thing, creature, end, False, **kwargs)
    
    def runDefer(self, thing, creature, end=None, **kwargs):
        return threads.deferToThreadPool(reactor, scriptPool, self._run, thing, creature, end, True, **kwargs)

    def runDeferNoReturn(self, thing, creature, end=None, **kwargs):
        return threads.deferToThreadPool(reactor, scriptPool, self._run, thing, creature, end, False, **kwargs)
        
    def runSync(self, thing, creature, end=None, **kwargs):
        return self._run(thing, creature, end, True, **kwargs)

    def makeResult(self, obj):
        def _handleResult(result):
            cache = True
            for (success, value) in result:
                if value is False:
                    cache = False
                    break
                else:
                    cache = value
            obj.value = cache
        return _handleResult

    def handleCallback(self, callback):
        def _handleResult(result):
            for (success, value) in result:
                if value is False:
                    return

            callback()
        return _handleResult
        
    def _run(self, thing, creature, end, returnVal, **kwargs):
        ok = Value()

        deferList = []
        for weakthing in self.thingScripts:
            if weakthing() == thing:
                for func in self.thingScripts[weakthing][:]:
                    if func:
                        deferList.append(defer.maybeDeferred(func, creature=creature, thing=thing, **kwargs))
                    else:
                        try:
                            self.thingScripts[weakthing].remove(func) 
                        except:
                            pass
            elif weakthing() == None:
                del self.thingScripts[weakthing]
        try:
            for func in self.scripts[thing.thingId()][:]:
                if func:
                    deferList.append(defer.maybeDeferred(func, creature=creature, thing=thing, **kwargs))
                else:
                    try:
                        self.scripts[thing.thingId()].remove(func) 
                    except:
                        pass   

        except:
            pass
        
        for aid in thing.actionIds():
            try:
                for func in self.scripts[aid][:]:
                    if func:
                        deferList.append(defer.maybeDeferred(func, creature=creature, thing=thing, **kwargs))
                    else:
                        try:
                            self.scripts[aid].remove(func) 
                        except:
                            pass
            except:
                pass
            
        if returnVal:
            # This is actually blocking code, but is rarely used.
            d = defer.DeferredList(deferList)
            d.addCallback(self.makeResult(ok))
            while True:
                try:
                    ok.value
                    break
                except:
                    time.sleep(0.001)
            
            return ok.value if type(ok.value) != bool else None
        elif end:
            d = defer.DeferredList(deferList)
            d.addCallback(self.handleCallback(end))
            
class CreatureScripts(ThingScripts):
    def _run(self, thing, creature, end, returnVal, **kwargs):
        ok = True
        
        for weakthing in self.thingScripts:
            if weakthing() == thing:
                for func in self.thingScripts[weakthing][:]:
                    if func:
                        ok = func(creature=creature, creature2=thing, **kwargs)
                        if ok is False:
                            break
                    else:
                        try:
                            self.thingScripts[weakthing].remove(func) 
                        except:
                            pass
            elif weakthing() == None:
                del self.thingScripts[weakthing]
                
        if ok and thing.thingId() in self.scripts:
            for func in self.scripts[thing.thingId()][:]:
                if func:
                    ok = func(creature=creature, creature2=thing, **kwargs)
                    if ok is False:
                        break
                else:
                    try:
                        self.scripts[thing.thingId()].remove(func) 
                    except:
                        pass   

        if ok:
            for aid in thing.actionIds():
                if aid in self.scripts:
                    for func in self.scripts[aid][:]:
                        if func:
                            ok = func(creature=creature, creature2=thing, **kwargs)
                            if ok is False:
                                break
                        else:
                            try:
                                self.scripts[aid].remove(func) 
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
globalScripts["farUse"] = ThingScripts()
globalScripts["useWith"] = ThingScripts()
globalScripts["farUseWith"] = ThingScripts()
globalScripts["rotate"] = ThingScripts()
globalScripts["walkOn"] = ThingScripts()
globalScripts["walkOff"] = ThingScripts()
globalScripts["preWalkOn"] = ThingScripts()
globalScripts["postLoadSector"] = TriggerScripts()
globalScripts["lookAt"] = ThingScripts()
globalScripts["lookAtTrade"] = ThingScripts()
globalScripts["playerSayTo"] = CreatureScripts()
globalScripts["close"] = ThingScripts()
globalScripts["hit"] = CreatureScripts()
globalScripts["death"] = CreatureScripts()
globalScripts["respawn"] = Scripts()
globalScripts["reload"] = NCScripts()
globalScripts["startup"] = NCScripts()
globalScripts["shutdown"] = NCScripts()
globalScripts["move"] = Scripts()
globalScripts["appear"] = CreatureScripts()
globalScripts["disappear"] = CreatureScripts()
globalScripts["loot"] = CreatureScripts()
globalScripts["target"] = CreatureScripts()
globalScripts["modeChange"] = Scripts()
globalScripts["questLog"] = Scripts()
globalScripts["chargeRent"] = NCScripts()
globalScripts["equip"] = globalScripts["dress"] = globalScripts["wield"] = ThingScripts()
globalScripts["unequip"] = globalScripts["undress"] = globalScripts["unwield"] =ThingScripts()
globalScripts["requestChannels"] = Scripts()
globalScripts["joinChannel"] = Scripts()
globalScripts["leaveChannel"] = Scripts()
globalScripts["getChannelMembers"] = TriggerScripts()

globalEvents = []

# Events
def callEvent(time, func):
    func()
    globalEvents.append(reactor.callLater(time, callEvent, time, func))
    
def callEventDate(date, func):
    import dateutil.parser.parse as parse
    import datetime.datetime.now as now
    func()
    globalEvents.append(reactor.callLater(parse(date) - now(), callEventDate, date, func))
    
# Begin the scriptPool stuff, note: we got to add support for yield for the SQL stuff!
scriptPool = ThreadPool(5, config.suggestedGameServerScriptPoolSize)
scriptPool.start()

def run():
    get('shutdown').runSync()
    
reactor.addSystemEventTrigger('before','shutdown',run)
reactor.addSystemEventTrigger('before','shutdown',scriptPool.stop)

def handleModule(name):
    modules = __import__('data.%s' % name, globals(), locals(), ["*"], -1)

    try:
        modules.paths
    except:
        pass
    else:
        for subModule in modules.paths:
            handleModule("%s.%s" % (name, subModule))

    modPool.append([name, modules])

def importer():
    handleModule("scripts")
    handleModule("spells")
    handleModule("monsters")
    handleModule("npcs")
    

def reimporter():
    global globalEvents
    process = get("reload").runSync()
    if process == False:
        return

    # Unload all the global events
    for event in globalEvents:
        try:
            event.cancel()
        except:
            pass
    
    # Reset global events
    globalEvents = []
    
    # Clear spells
    game.spell.clear()
    
    # Reload modules
    for mod in modPool:
        # Step 1 reload self
        del mod[1]
        mod.append(__import__('data.%s' % mod[0], globals(), locals(), ["*"], -1))
        
        # Step 2, reload submodules
        for sub in mod[1].__all__:
            if sub != "__init__":
                reload(sys.modules["data.%s.%s" % (mod[0], sub)])
                
# This is the function to get events, it should also be a getAll, and get(..., creature)
def get(type):
    return globalScripts[type]
    
def reg(type, *argc, **kwargs):
    globalScripts[type].reg(*argc)

def regFirst(type, *argc, **kwargs):
    globalScripts[type].regFirst(*argc)
    
def regEvent(timeleap, callback):
    globalEvents.append(reactor.callLater(timeleap, callEvent, timeleap, callback))
    
def regEventTime(date, callback):
    import dateutil.parser.parse as parse
    import datetime.datetime.now as now
    globalEvents.append(reactor.callLater(parse(date) - now(), callEventDate, date, callback))