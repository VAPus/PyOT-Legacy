# The script system
from twisted.internet import reactor, defer
from twisted.python import log
import config
import weakref
import sys
import time
import traceback
import gc
from os import sep as os_seperator
from os.path import split as os_path_split
from glob import glob
import inspect

modPool = []
globalScripts = {}

class InvalidScriptFunctionArgument(Exception):
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
            ok = func(creature=creature, **kwargs)
            if ok is False:
                break
                
        if end and (ok or ok is None):
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
            ok = func(**kwargs)
            if ok is False:
                break
                
        if end and (ok or ok is None):
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
            ok = func(creature=creature, **kwargs)
            if ok is False:
                break

        if end and (ok or ok is None):
            end()
        return ok

class RegexTriggerScripts(TriggerScripts):
    __slots__ = ('scripts', 'parameters')

    def __init__(self, parameters = ()):
        self.scripts = {}
        self.parameters = () # We can't have parameters
        
    def register(self, trigger, callback, weakfunc=True):
        if weakfunc:
            func = weakref.proxy(callback, self._unregCallback(trigger))
        else:
            func = callback
            
        if not trigger in self.scripts:
            self.scripts[trigger] = [func], re.compile(trigger).search
        else:
            self.scripts[trigger][0].append(func)
        
    def registerFirst(self, trigger, callback, weakfunc=True):
        if not trigger in self.scripts:
            self.register(trigger, callback, weakfunc)
        else:
            if weakfunc:
                func = weakref.proxy(callback, self._unregCallback(trigger))
            else:
                func = callback
            self.scripts[trigger][0].insert(0, func)

        
    def _unregCallback(self, trigger):
        def trigger_cleanup_callback(func):
            if game.engine.IS_RUNNING: # If we're shutting down, this is a waste of time
                for elm in self.scripts[trigger]:
                    if func in elm[0]:
                        elm[0].remove(func)
                        if not len(elm[0]):
                            del self.scripts[trigger]
                        return
                
        return trigger_cleanup_callback
    
    def _run(self, trigger, creature, end, **kwargs):
        ok = True

        """if not trigger in self.scripts:
            return end() if end else None"""
        for scriptTrigger in self.scripts:
            spectre = self.scripts[scriptTrigger]

            obj = spectre[1](trigger)

            if not obj:
                continue
            else:
                args = obj.groupdict()
                
            for func in spectre[0]:
                for arg in kwargs:
                    args[arg] = kwargs[arg]
                          
                ok = func(creature=creature, **args)
                if ok is False:
                    break
                             
        if end and (ok or ok is None):
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
        ok = None
        if thing in self.thingScripts:
            for func in self.thingScripts[thing]:
                ok = func(creature=creature, thing=thing, **kwargs)
                if ok is False:
                    break
                    
        thingId = thing.thingId()
        
        if thingId in self.scripts:
            for func in self.scripts[thingId]:
                ok = func(creature=creature, thing=thing, **kwargs)
                if ok is False:
                    break
        for aid in thing.actionIds():
            if aid in self.scripts:
                for func in self.scripts[aid]:
                    ok = func(creature=creature, thing=thing, **kwargs)
                    if ok is False:
                        break
        if returnVal:
            if end:
                end()
                
            return ok if ok != True else None
        elif end:
            end()
            
    @defer.inlineCallbacks
    def _runDefer(self, thing, creature, end, returnVal, **kwargs):
        deferList = []
        if thing in self.thingScripts:
            for func in self.thingScripts[thing]:
                deferList.append(defer.maybeDeferred(func, creature=creature, thing=thing, **kwargs))
        
        thingId = thing.thingId()
        if thingId in self.scripts:
            for func in self.scripts[thingId]:
                deferList.append(defer.maybeDeferred(func, creature=creature, thing=thing, **kwargs)) 
        
        for aid in thing.actionIds():
            if aid in self.scripts:
                for func in self.scripts[aid]:
                    deferList.append(defer.maybeDeferred(func, creature=creature, thing=thing, **kwargs))
            
        if returnVal:
            # This is actually blocking code, but is rarely used.
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
               ok = func(creature=creature, creature2=thing, **kwargs)
               if ok is False:
                   break

        thingId = thing.thingId()
        if ok and thingId in self.scripts:
            for func in self.scripts[thingId]:
                ok = func(creature=creature, creature2=thing, **kwargs)
                if ok is False:
                    break  

        if ok:
            for aid in thing.actionIds():
                if aid in self.scripts:
                    for func in self.scripts[aid]:
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
globalScripts["talkactionRegex"] = RegexTriggerScripts(('creature', 'text'))
globalScripts["login"] = Scripts(('creature',))
globalScripts["loginAccountFailed"] = NCScripts()
globalScripts["loginCharacterFailed"] = NCScripts()
globalScripts["logout"] = Scripts(('creature',))
globalScripts["use"] = ThingScripts(('creature', 'thing', 'position', 'index'))
globalScripts["useWith"] = ThingScripts(('creature', 'thing', 'position', 'onThing', 'onPosition'))
globalScripts["rotate"] = ThingScripts()
globalScripts["stack"] = ThingScripts(('creature', 'thing', 'position', 'onThing', 'onPosition', 'count'))
globalScripts["walkOn"] = ThingScripts(('creature', 'thing', 'position', 'fromPosition'))
globalScripts["walkOff"] = ThingScripts(('creature', 'thing', 'position'))
globalScripts["preWalkOn"] = ThingScripts(('creature', 'thing', 'position', 'oldTile', 'newTile'))
globalScripts["postLoadSector"] = TriggerScripts(('sector', 'instanceId'))
globalScripts["lookAt"] = ThingScripts(('creature', 'thing', 'position'))
globalScripts["lookAtTrade"] = ThingScripts()
globalScripts["playerSayTo"] = CreatureScripts()
globalScripts["close"] = ThingScripts(('creature', 'thing', 'index'))
globalScripts["hit"] = CreatureScripts(('creature', 'creature2', 'damage', 'type', 'textColor', 'magicEffect'))
globalScripts["death"] = CreatureScripts(('creature', 'creature2', 'deathData', 'corpse'))
globalScripts["respawn"] = Scripts(('creature',))
globalScripts["reload"] = NCScripts()
globalScripts["postReload"] = NCScripts()
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
        modules = __import__('%s.%s' % (config.dataDirectory, name), globals(), locals(), ["*"], -1)
    except:
        (exc_type, exc_value, exc_traceback) = sys.exc_info()

        tb_list = traceback.extract_tb(exc_traceback)
        tb_list = traceback.format_list(tb_list)
        
        print "--------------------------"
        # This may not be available.
        try:
            print "EXCEPTION IN SCRIPT (%s):" % exc_value.filename
        except AttributeError:
            print "EXCEPTION IN SCRIPT:"
            
        for elt in tb_list[1:]:
            print elt
        if exc_type == SyntaxError:
            print ">>>", exc_value.text,
        print "%s: %s" % (exc_type.__name__, exc_value)
        print "--------------------------"
        
        return
        
    paths = None
    try:
        paths = modules.paths
    except AttributeError:
        pass # Not a module.
    else:
        if paths:
            for subModule in modules.paths:
                handleModule("%s.%s" % (name, subModule))

        modPool.append([name, modules])

def importer():
    handleModule("scripts")
    handleModule("spells")
    handleModule("monsters")
    handleModule("npcs")
    handlePostLoadEntries()

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
        print "[WARNING]: Reload cancelled."
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
        mod.append(__import__('%s.%s' % (config.dataDirectory, mod[0]), globals(), locals(), ["*"], -1))
        
        # Step 2, reload submodules
        for sub in mod[1].__all__:
            if sub != "__init__":
                reload(sys.modules["%s.%s.%s" % (config.dataDirectory, mod[0], sub)])

    handlePostLoadEntries()

    # Call gc.collect()
    gc.collect()

    # Cleanups.
    reimportCleanup()
    
    # postReload.
    get("postReload").runSync()
    
def reimportCleanup():
    for script in globalScripts:
        if isinstance(script, Scripts):
            for func in script.scripts[:]:
                if not func:
                    script.scripts.remove(func)
        elif type(script) == TriggerScripts:
            for trigger in script.triggers.copy():
                for func in script.triggers[trigger][:]:
                    if not func:
                        script.triggers[trigger].remove(func)
                if len(script.triggers[trigger]) == 0:
                    del script.triggers[trigger]
        elif type(script) == RegexTriggerScripts:
            for trigger in script.triggers.copy():
                for func in script.triggers[trigger][0][:]:
                    if not func:
                        script.triggers[trigger][0].remove(func)
                if len(script.triggers[trigger][0]) == 0:
                    del script.triggers[trigger]
                    
                            
        elif isinstance(script, ThingScripts):
            for trigger in script.scripts.copy():
                for func in script.scripts[trigger][:]:
                    if not func:
                        script.scripts[trigger].remove(func)
                if len(script.scripts[trigger]) == 0:
                    del script.scripts[trigger]
                    
            for trigger in script.thingScripts.copy():
                for func in script.scripts[trigger][:]:
                    if not func:
                        script.scripts[trigger].remove(func)
                if len(script.scripts[trigger]) == 0:
                    del script.scripts[trigger]
                    
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
        
        # Step 2, verify parameters
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
        
        # Step 2, verify parameters
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
def access(*groupFlags, **kwargs):
    assert groupFlags
    isPlayer = True
    isMonster = False
    isNPC = False
    checks = []
    # XXX: Cheat Python2 syntax, Python3 got a nice fix for this by allowing kwargs to come after a *argc argument. Too bad pypy and twisted still is py2 only.
    # Unwrap it to get the overhead in loading instead of runtime.
    for arg in kwargs:
        if arg == "isPlayer":
            isPlayer = kwargs[arg]
            if isPlayer:
                check.append("if not creature.isPlayer() or not creature.hasGroupFlags(*%s): return" % groupFlags)
        elif arg == "isMonster":
            isMonster = kwargs[arg]
            if isMonster:
                checks.append("if not creature.isMonster(): return")
        elif arg == "isNPC":
            isNPC = kwargs[arg]
            if isNPC:
                checks.append("if not creature.isNPC(): return")
        else:
            raise TypeError("Calling scriptsystem.access() with invalid parameter %s" % arg)
            
    # Notice: We may make a optimized wrapper call when len(groupFlags) == 1 using creature.hasGroupFlag(unwrapperGroupFlag).
    def _wrapper(f):
        iargs = inspect.getargspec(f)
        vars = ", ".join(iargs[0])
        if iargs[2]:
            if vars:
                vars += ", **k"
            else:
                vars = "**k"
                
        exec """
def access_wrapper_inner(%s):
    %s
    return f(%s)""" % (vars, '\n    '.join(checks), vars) in locals(), locals()
        return access_wrapper_inner
    return _wrapper

# A special post-loading cache thingy.
postLoadEntries = {}

def registerForAttr(type, attr, callback):
    postLoadEntries.setdefault(attr, []).append((type, callback))

def handlePostLoadEntries():
    _unpackPostLoad = postLoadEntries.items()
    for id, attr in game.item.items.iteritems():
        for key, entries in _unpackPostLoad:
            if key in attr:
                for entry in entries:
                    globalScripts[entry[0]].register(id, entry[1])


    postLoadEntries.clear()
