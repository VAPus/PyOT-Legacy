# The script system
from twisted.internet import reactor, threads, defer
from twisted.python.threadpool import ThreadPool
from twisted.python import log
import config
import weakref
import sys
import time
import traceback
from os import sep as os_seperator
from os.path import split as os_path_split
from glob import glob
import inspect

modPool = []
globalScripts = {}

class InvalidScriptFunctionArgument(Exception):
    pass

class Value(object):
    pass

class Scripts(object):
    __slots__ = ('scripts', 'parameters')
    def __init__(self, parameters = ()):
        self.scripts = []
        self.parameters = parameters
        
    def register(self, callback, weakfunc=True):

        if weakfunc:
            func = weakref.proxy(callback, self.unregCallback)
        else:
            func = callback
        self.scripts.append(func)
        
    def unregister(self, callback):
        self.scripts.remove(callback)
    
    def unregCallback(self, callback):
        if game.engine.IS_RUNNING:
            self.scripts.remove(callback)
                
    def run(self, creature, end=None, **kwargs):
        #scriptPool.callInThread(self._run, creature, end, **kwargs)
        raise Exception("Threaded script is not allowed in this branch!")

    def runSync(self, creature, end=None, **kwargs):
        return self._run(creature, end, **kwargs)

    def runDefer(self, creature, end=None, **kwargs):
        return defer.maybeDeferred(self._run, creature, end, **kwargs)
        
    def _run(self, creature, end=None, **kwargs):
        ok = True
        for func in self.scripts:
            if func:
                ok = func(creature=creature, **kwargs)
                if not (ok if ok is not None else True):
                    break
                
        if end and (ok if ok is not None else True):
            end()
        else:
            return ok

class NCScripts(Scripts):
    def run(self, end=None, **kwargs):
        #scriptPool.callInThread(self._run, end, **kwargs)
        raise Exception("Threaded script is not allowed in this branch!")

    def runSync(self, end=None, **kwargs):
        return self._run(end, **kwargs)

    def runDefer(self, end=None, **kwargs):
        return defer.maybeDeferred(self._run, end, **kwargs)

    def _run(self, end=None, **kwargs):
        ok = True
        for func in self.scripts:
            if func:
                ok = func(**kwargs)
                if not (ok if ok is not None else True):
                    break
                
        if end and (ok if ok is not None else True):
            end()
        else:
            return ok
                
class TriggerScripts(object):
    __slots__ = ('scripts', 'parameters')
    def __init__(self, parameters = ()):
        self.scripts = {}
        self.parameters = parameters

    def register(self, trigger, callback, weakfunc=True):
        if weakfunc:
            func = weakref.proxy(callback, self._unregCallback(trigger))
        else:
            func = callback
            
        if not trigger in self.scripts:
            self.scripts[trigger] = [func]
        else:
            self.scripts[trigger].append(func)
        
    def registerFirst(self, trigger, callback, weakfunc=True):
        if not trigger in self.scripts:
            self.register(trigger, callback, weakfunc)
        else:
            if weakfunc:
                func = weakref.proxy(callback, self._unregCallback(trigger))
            else:
                func = callback
            self.scripts[trigger].insert(0, func)
            
    def unregister(self, trigger, callback):
        self.scripts[trigger].remove(callback)

        if not len(self.scripts[trigger]):
            del self.scripts[trigger]
        
    def run(self, trigger, creature, end=None, **kwargs):
        #scriptPool.callInThread(self._run, trigger, creature, end, **kwargs)
        raise Exception("Threaded script is not allowed in this branch!")

    def runSync(self, trigger, creature, end=None, **kwargs):
        return self._run(trigger, creature, end, **kwargs)
        
    def _unregCallback(self, trigger):
        def trigger_cleanup_callback(func):
            if game.engine.IS_RUNNING: # If we're shutting down, this is a waste of time
                self.scripts[trigger].remove(func)
                if not len(self.scripts[trigger]):
                    del self.scripts[trigger]
                
        return trigger_cleanup_callback
                
    def _run(self, trigger, creature, end, **kwargs):
        ok = True

        if not trigger in self.scripts:
            return end() if end else None
            
        for func in self.scripts[trigger]:
            if func:
                ok = func(creature=creature, **kwargs)
                if not (ok if ok is not None else True):
                    break

        if end and (ok if ok is not None else True):
            end()
        return ok

# Thing scripts is a bit like triggerscript except it might use id ranges etc
class ThingScripts(object):
    __slots__ = ('scripts', 'thingScripts', 'parameters')
    def __init__(self, parameters = ()):
        self.scripts = {}
        self.thingScripts = {}
        self.parameters = parameters
        
    def haveScripts(self, id):
        if type(id) in (list, tuple, set):
            for i in id:
                if i in self.scripts:
                    return True
                    
        elif id in self.scripts or (type(id) not in (int, long, str) and id in self.thingScripts):
            return True
        else:
            return False
            
    def register(self, id, callback, weakfunc=True):
        
        if weakfunc:
            func = weakref.proxy(callback, self._unregCallback(id))
        else:
            func = callback
            
        if type(id) in (tuple, list, set):
            for xid in id:
                if not xid in self.scripts:
                    self.scripts[xid] = [func]
                else:
                    self.scripts[xid].append(func)   
                    
        elif type(id) in (int, long, str):
            if not id in self.scripts:
                self.scripts[id] = [func]
            else:
                self.scripts[id].append(func)
                
        else:
            if not id in self.thingScripts:
                self.thingScripts[id] = [func]
            else:
                self.thingScripts[id].append(func)
                
    def registerFirst(self, id, callback, weakfunc=True):
        
        if weakfunc:
            func = weakref.proxy(callback, self._unregCallback)
        else:
            func = callback
            
        if type(id) in (tuple, list, set):
            for xid in id:
                if not xid in self.scripts:
                    self.scripts[xid] = [func]
                else:
                    self.scripts[xid].insert(0, func)  
                    
        elif type(id) in (int, long, str):
            if not id in self.scripts:
                self.scripts[id] = [func]
            else:
                self.scripts[id].insert(0, func)
                
        else:
            if not id in self.thingScripts:
                self.thingScripts[id] = [func]
            else:
                self.thingScripts[id].insert(0, func) 
                
    def unregister(self, id, callback):
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
     
    def _unregCallback(self, id):
        def thing_cleanup_callback(func):
            if game.engine.IS_RUNNING: # If we're shutting down, this is a waste of time
                if type(id) in (tuple, list, set):
                    for xid in id:
                        self.scripts[xid].remove(func)  
                        if not self.scripts[xid]:
                            del self.scripts[xid]
                        
                elif type(id) in (int, long, str):
                    self.scripts[id].remove(func)
                    if not self.scripts[id]:
                        del self.scripts[id]
                        
                else:
                    self.thingScripts[id].remove(func)
                    if not self.thingScripts[id]:
                        del self.scripts[id]
                    
        return thing_cleanup_callback
        
    def run(self, thing, creature, end=None, **kwargs):
        #scriptPool.callInThread(self._run, thing, creature, end, False, **kwargs)
        raise Exception("Threaded script is not allowed in this branch!")
    
    def runDefer(self, thing, creature, end=None, **kwargs):
        return defer.maybeDeferred(self._runDefer, thing, creature, end, True, **kwargs)

    def runDeferNoReturn(self, thing, creature, end=None, **kwargs):
        return defer.maybeDeferred(self._run, thing, creature, end, False, **kwargs)
        
    def runSync(self, thing, creature, end=None, **kwargs):
        return self._run(thing, creature, end, True, **kwargs)

    def makeResult(self, obj):
        def _handleResult(result):
            cache = True
            for value in result:
                if value is False:
                    cache = False
                    break
                else:
                    cache = value
            obj.value = cache
        return _handleResult

    def handleCallback(self, callback):
        def _handleResult(result):
            for value in result:
                if value is False:
                    return

            callback()
        return _handleResult
        
    def _run(self, thing, creature, end, returnVal, **kwargs):
        deferList = []
        if thing in self.thingScripts:
            for func in self.thingScripts[thing]:
                if func:
                    deferList.append(defer.maybeDeferred(func, creature=creature, thing=thing, **kwargs))
        
        if thing.thingId() in self.scripts:
            for func in self.scripts[thing.thingId()]:
                if func:
                    deferList.append(defer.maybeDeferred(func, creature=creature, thing=thing, **kwargs)) 
        
        for aid in thing.actionIds():
            if aid in self.scripts:
                for func in self.scripts[aid]:
                    if func:
                        deferList.append(defer.maybeDeferred(func, creature=creature, thing=thing, **kwargs))
            
        if returnVal:
            # This is actually blocking code, but is rarely used.
            ok = Value()
            d = defer.gatherResults(deferList)
            d.addCallback(self.makeResult(ok))
            d.addErrback(log.err)
            while True:
                try:
                    ok.value
                    break
                except:
                    time.sleep(0.001)
            if end:
                end()
                
            return ok.value if type(ok.value) != bool else None
        elif end:
            d = defer.gatherResults(deferList)
            d.addCallback(self.handleCallback(end))
            d.addErrback(log.err)
        else:
            d = defer.DeferredList(deferList)
            d.addErrback(log.err)
            
    @defer.inlineCallbacks
    def _runDefer(self, thing, creature, end, returnVal, **kwargs):
        deferList = []
        if thing in self.thingScripts:
            for func in self.thingScripts[thing]:
                if func:
                    deferList.append(defer.maybeDeferred(func, creature=creature, thing=thing, **kwargs))
        
        if thing.thingId() in self.scripts:
            for func in self.scripts[thing.thingId()]:
                if func:
                    deferList.append(defer.maybeDeferred(func, creature=creature, thing=thing, **kwargs)) 
        
        for aid in thing.actionIds():
            if aid in self.scripts:
                for func in self.scripts[aid]:
                    if func:
                        deferList.append(defer.maybeDeferred(func, creature=creature, thing=thing, **kwargs))
            
        if returnVal:
            # This is actually blocking code, but is rarely used.
            ok = Value()
            d = defer.gatherResults(deferList)
        elif end:
            d = defer.gatherResults(deferList)
            d.addCallback(self.handleCallback(end))
        else:
            d = defer.DeferredList(deferList)
            
        d.addErrback(log.err)  
        yield d
class CreatureScripts(ThingScripts):
    def _run(self, thing, creature, end, returnVal, **kwargs):
        ok = True
        
        if thing in self.thingScripts:
            for func in self.thingScripts[thing]:
                if func:
                   ok = func(creature=creature, creature2=thing, **kwargs)
                   if ok is False:
                       break

        if ok and thing.thingId() in self.scripts:
            for func in self.scripts[thing.thingId()]:
                if func:
                    ok = func(creature=creature, creature2=thing, **kwargs)
                    if ok is False:
                        break  

        if ok:
            for aid in thing.actionIds():
                if aid in self.scripts:
                    for func in self.scripts[aid]:
                        if func:
                            ok = func(creature=creature, creature2=thing, **kwargs)
                            if ok is False:
                                break
                            
        if not returnVal and end and ok is not False:
            return end()
        elif returnVal:
            return ok if type(ok) != bool else None
            
# All global events can be initialized here
globalScripts["talkaction"] = TriggerScripts(('creature', 'text'))
globalScripts["talkactionFirstWord"] = TriggerScripts(('creature', 'text'))
globalScripts["login"] = Scripts(('creature',))
globalScripts["loginAccountFailed"] = NCScripts()
globalScripts["loginCharacterFailed"] = NCScripts()
globalScripts["logout"] = Scripts(('creature',))
globalScripts["use"] = ThingScripts(('creature', 'thing', 'position', 'index'))
globalScripts["useWith"] = ThingScripts(('creature', 'thing', 'position', 'onThing', 'onPosition'))
globalScripts["rotate"] = ThingScripts()
globalScripts["walkOn"] = ThingScripts(('creature', 'thing', 'position', 'fromPosition'))
globalScripts["walkOff"] = ThingScripts(('creature', 'thing', 'position'))
globalScripts["preWalkOn"] = ThingScripts(('creature', 'thing', 'position', 'oldTile', 'newTile'))
globalScripts["postLoadSector"] = TriggerScripts(('sector', 'instanceId'))
globalScripts["lookAt"] = ThingScripts(('creature', 'thing', 'position'))
globalScripts["lookAtTrade"] = ThingScripts()
globalScripts["playerSayTo"] = CreatureScripts()
globalScripts["close"] = ThingScripts(('creature', 'thing', 'index'))
globalScripts["hit"] = CreatureScripts(('creature', 'creature2', 'damage', 'type', 'textColor', 'magicEffect'))
globalScripts["death"] = CreatureScripts(('creature', 'creature2', 'corpse'))
globalScripts["respawn"] = Scripts(('creature',))
globalScripts["reload"] = NCScripts()
globalScripts["startup"] = NCScripts()
globalScripts["shutdown"] = NCScripts()
globalScripts["move"] = Scripts(('creature',))
globalScripts["appear"] = CreatureScripts()
globalScripts["disappear"] = CreatureScripts()
globalScripts["loot"] = CreatureScripts()
globalScripts["target"] = CreatureScripts()
globalScripts["thankYou"] = Scripts()
globalScripts["modeChange"] = Scripts()
globalScripts["questLog"] = Scripts()
globalScripts["chargeRent"] = NCScripts()
globalScripts["equip"] = globalScripts["dress"] = globalScripts["wield"] = ThingScripts()
globalScripts["unequip"] = globalScripts["undress"] = globalScripts["unwield"] =ThingScripts()
globalScripts["requestChannels"] = Scripts()
globalScripts["joinChannel"] = Scripts()
globalScripts["leaveChannel"] = Scripts()
globalScripts["getChannelMembers"] = TriggerScripts()
globalScripts["level"] = Scripts()
globalScripts["skill"] = Scripts()

if config.letGameServerRunTheLoginServer:
    globalScripts["preSendLogin"] = NCScripts()
    
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
"""scriptPool = ThreadPool(5, config.suggestedGameServerScriptPoolSize)
scriptPool.start()"""

def run():
    game.engine.IS_ONLINE = False
    game.engine.IS_RUNNING = False
    get('shutdown').runSync()
    
reactor.addSystemEventTrigger('before','shutdown',run)
#reactor.addSystemEventTrigger('before','shutdown',scriptPool.stop)

def handleModule(name):
    try:
        modules = __import__('data.%s' % name, globals(), locals(), ["*"], -1)
    except:
        (exc_type, exc_value, exc_traceback) = sys.exc_info()

        tb_list = traceback.extract_tb(exc_traceback)
        tb_list = traceback.format_list(tb_list)
        
        print "--------------------------"
        print "EXCEPTION IN SCRIPT:"
        
        for elt in tb_list[1:]:
            print elt

        print "%s: %s" % (exc_type.__name__, exc_value)
        print "--------------------------"
        
        return
        
    if modules.paths:
        for subModule in modules.paths:
            handleModule("%s.%s" % (name, subModule))

    modPool.append([name, modules])

def importer():
    handleModule("scripts")
    handleModule("spells")
    handleModule("monsters")
    handleModule("npcs")
    
def scriptInitPaths(base, subdir=True):
    all = []
    paths = []
    
    base = os_path_split(base)[0] # Remove the ending of the paths!
    
    for mod in glob("%s/*.py" % base):
        modm = mod.split(os_seperator)[-1].replace('.py', '')
        if modm == "__init__":
            continue

        all.append(modm)
    
    if subdir:
        for mod in glob("%s/*/__init__.py" % base):
            paths.append(mod.split(os_seperator)[-2])
    return all, paths
    
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
    
def register(type, *argc):
    def _wrapper(f):
        object = globalScripts[type]
        iargs = inspect.getargspec(f)
        vars = iargs[0]
        # Step 1, check if it has **f
        hasKeyword = bool(iargs[2])
        
        # Step 2, vertify parameters
        if object.parameters and not hasKeyword:
            if len(object.parameters) > 4:
                raise InvalidScriptFunctionArgument("Function lakes the **k argument")
            
            for param in object.parameters:
                if not param in vars:
                    print vars
                    raise InvalidScriptFunctionArgument("Function does not have all the valid parameters (and doesn't supply a **k argument). '%s' not found." % param)
                
        # Step 3, veritify parameter names
        if object.parameters:
            for param in vars:
                if param == 'k': continue
                if param not in object.parameters:
                    raise InvalidScriptFunctionArgument("Function parameter '%s' is invalid" % param)
                
        object.register(*argc, callback=f)
        return f
        
    return _wrapper

def unregister(type, *argc):
    def _wrapper(f):
        globalScripts[type].unregister(*argc, callback=f)
        return f
        
    return _wrapper
    
def registerFirst(type, *argc):
    def _wrapper(f):
        object = globalScripts[type]
        iargs = inspect.getargspec(f)
        vars = iargs[0]
        # Step 1, check if it has **f
        hasKeyword = bool(iargs[2])
        
        # Step 2, vertify parameters
        if object.parameters and not hasKeyword:
            if len(object.parameters) > 4:
                raise InvalidScriptFunctionArgument("Function lakes the **k argument")
            
            for param in object.parameters:
                if not param in vars:
                    raise InvalidScriptFunctionArgument("Function does not have all the valid parameters (and doesn't supply a **k argument). '%s' not found." % param)
                
        # Step 3, veritify parameter names
        if object.parameters:
            for param in vars:
                if param == 'k': continue
                if param not in object.parameters:
                    raise InvalidScriptFunctionArgument("Function parameter '%s' is invalid" % param)
                
        object.registerFirst(*argc, callback=f)
        return f
        
    return _wrapper
    
def regEvent(timeleap, callback):
    globalEvents.append(reactor.callLater(timeleap, callEvent, timeleap, callback))
    
def regEventTime(date, callback):
    import dateutil.parser.parse as parse
    import datetime.datetime.now as now
    globalEvents.append(reactor.callLater(parse(date) - now(), callEventDate, date, callback))
    
# Another cool decorator
def access(isPlayer=True, isMonster=False, isNPC=False, *groupFlags):
    def _wrapper(f):
        def access_wrapper_inner(creature, **k):
            if isMonster and not creature.isMonster():
                return
                
            if isNPC and not creature.isNPC():
                return
            
            if isPlayer:
                if not creature.isPlayer() or not creature.hasGroupFlags(*groupFlags):
                    return 
                    
            else:
                assert not groupFlags
                
            return f(creature, **k)
        return access_wrapper_inner
    return _wrapper