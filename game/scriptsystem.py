# The script system
import config
import sys
import time
import traceback
import gc
from os import sep as os_seperator
from os.path import split as os_path_split
from glob import glob
import inspect
from tornado import gen

modPool = []
globalScripts = {}

class InvalidScriptFunctionArgument(Exception):
    pass

class Scripts(object):
    def __init__(self, parameters = ()):
        self.scripts = []
        self.parameters = parameters
        self.weaks = set() 
    def register(self, callback, weakfunc=True):
        if weakfunc:
            self.weaks.add(callback)
        
        self.scripts.append(callback)
        
    def unregister(self, callback):
        self.scripts.remove(callback)
        if callback in self.weaks:
            self.weaks.remove(callback)
   
    def run(self, end=None, **kwargs):
        res = True
        for func in self.scripts:
            res = func(**kwargs)
            if res == False:
                break 

        if end: end(res)
        return res
                
class TriggerScripts(object):
    def __init__(self, parameters = ()):
        self.scripts = {}
        self.parameters = parameters
        self.weaks = set()

    def register(self, trigger, callback, weakfunc=True):
        if weakfunc:
            self.weaks.add((trigger, callback))
            
        if not trigger in self.scripts:
            self.scripts[trigger] = [callback]
        else:
            self.scripts[trigger].append(callback)
        
    def registerFirst(self, trigger, callback, weakfunc=True):
        if not trigger in self.scripts:
            self.register(trigger, callback, weakfunc)
        else:
            if weakfunc:
                self.weaks.add((trigger, callback))
                
            self.scripts[trigger].insert(0, callback)
            
    def unregister(self, trigger, callback):
        self.scripts[trigger].remove(callback)

        if not len(self.scripts[trigger]):
            del self.scripts[trigger]
        if (trigger, callback) in self.weaks:
            self.weaks.remove((trigger, callback))

    def run(self, trigger, end=None, **kwargs):
        res = None
        if not trigger in self.scripts:
            if end:
                return end(None)
            return None

        for func in self.scripts[trigger]:
            res = func(**kwargs)
            
        if end:
            return end(res)
        return res

class NCTriggerScripts(TriggerScripts):
    """ Designed for webrequests. """
    def run(self, trigger, end=None, **kwargs):

        trig = self.scripts
        if not trigger in trig:
            if end:
                end(None)
            return
            
        trig = trig[trigger]

        if not trig:
            return

        d = maybeDeferred(trig[0], kwargs)

        if end:
            d.addCallback(end)
        return d

class RegexTriggerScripts(TriggerScripts):
    def __init__(self, parameters = ()):
        self.scripts = {}
        self.parameters = () # We can't have parameters
        self.weaks = set()

    def register(self, trigger, callback, weakfunc=True):
        if weakfunc:
            self.weaks.add((trigger, callback))
        
            
        if not trigger in self.scripts:
            self.scripts[trigger] = [callback], re.compile(trigger).search
        else:
            self.scripts[trigger][0].append(callback)
        
    def registerFirst(self, trigger, callback, weakfunc=True):
        if not trigger in self.scripts:
            self.register(trigger, callback, weakfunc)
        else:
            if weakfunc:
                self.weaks.add((trigger, callback))
            
            self.scripts[trigger][0].insert(0, callback)

    def run(self, trigger, end=None, **kwargs):

        res = None
        """if not trigger in self.scripts:
            return end() if end else None"""
        for scriptTrigger in self.scripts:
            spectre = self.scripts[scriptTrigger]

            obj = spectre[1](trigger)

            if not obj:
                continue
            else:
                args = obj.groupdict()
            args.update(kwargs)
                               
            for func in spectre[0]:
                res = func(**args)
               
        
        if end: return end(None)
        return res

        
# Thing scripts is a bit like triggerscript except it might use id ranges etc
class ThingScripts(object):
    def __init__(self, parameters = ()):
        self.scripts = {}
        self.thingScripts = {}
        self.parameters = parameters
        self.weaks = set()
        
    def haveScripts(self, id):
        if hasattr(id, '__iter__') and not type(id) == str: #type(id) in (list, tuple, set, dict_keys):
            for i in id:
                if i in self.scripts:
                    return True
                    
        elif id in self.scripts or (type(id) not in (int, int, str) and id in self.thingScripts):
            return True
        else:
            return False
            
    def register(self, id, callback, weakfunc=True):
        if hasattr(id, '__iter__') and not type(id) == str: #type(id) in (tuple, list, set):
            for xid in id:
                if not xid in self.scripts:
                    self.scripts[xid] = [callback]
                else:
                    self.scripts[xid].append(callback)   
                if weakfunc:
                    self.weaks.add((xid, callback))                    
        elif type(id) in (int, str):
            if not id in self.scripts:
                self.scripts[id] = [callback]
            else:
                self.scripts[id].append(callback)
            self.weaks.add((id, callback))
        else:
            if not id in self.thingScripts:
                self.thingScripts[id] = [callback]
            else:
                self.thingScripts[id].append(callback)
                
    def registerFirst(self, id, callback, weakfunc=True):
        if hasattr(id, '__iter__') and not type(id) == str: #type(id) in (tuple, list, set):
            for xid in id:
                if not xid in self.scripts:
                    self.scripts[xid] = [callback]
                else:
                    self.scripts[xid].insert(0, callback)  
                self.weaks.add((xid, callback))
        elif type(id) in (int, str):
            if not id in self.scripts:
                self.scripts[id] = [callback]
            else:
                self.scripts[id].insert(0, callback)
            self.weaks.add((id, callback))
        else:
            if not id in self.thingScripts:
                self.thingScripts[id] = [callback]
            else:
                self.thingScripts[id].insert(0, callback) 
                
    def unregister(self, id, callback):
        try:
            self.scripts[id].remove(callback)

            if not self.scripts[id]:
                del self.scripts[id]
                
        except:
            pass # Nothing
        if (id, callback) in self.weaks:
            self.weaks.remove((id, callback))

    def unregAll(self, id):
        try:
            del self.scripts[id]
        except:
            pass
       
    def run(self, end=None, **kwargs):
        res = None
        thing = kwargs["thing"]
        if thing in self.thingScripts:
            for func in self.thingScripts[thing]:
                res = func(**kwargs)
                

        thingId = thing.thingId()
        if thingId in self.scripts:
            for func in self.scripts[thingId]:
                res = func(**kwargs)

        for aid in thing.actionIds():
            if aid in self.scripts:
                for func in self.scripts[aid]:
                    res = gen.maybe_future(func(**kwargs)

        
        if end:
            return end(res)
        return None

class CreatureScripts(ThingScripts):
    @gen.coroutine
    def run(self, end=None, **kwargs):
        res = None
        thing = kwargs["creature2"]
        if thing in self.thingScripts:
            for func in self.thingScripts[thing]:
                res = func(**kwargs)
        

        thingId = thing.thingId()
        if thingId in self.scripts:
            for func in self.scripts[thingId]:
                res = func(**kwargs)
        

        for aid in thing.actionIds():
            if aid in self.scripts:
                for func in self.scripts[aid]:
                    res = func(**kwargs)
           

        if end:
            return end(res)
        return res
    
# All global events can be initialized here
globalScripts["talkaction"] = TriggerScripts(('creature', 'text'))
globalScripts["talkactionFirstWord"] = TriggerScripts(('creature', 'text'))
globalScripts["talkactionRegex"] = RegexTriggerScripts(('creature', 'text'))
globalScripts["login"] = Scripts(('creature',))
globalScripts["loginAccountFailed"] = Scripts()
globalScripts["loginCharacterFailed"] = Scripts()
globalScripts["logout"] = Scripts(('creature',))
globalScripts["use"] = ThingScripts(('creature', 'thing', 'position', 'index'))
globalScripts["useWith"] = ThingScripts(('creature', 'thing', 'position', 'onThing', 'onPosition'))
globalScripts["dropOnto"] = ThingScripts(('creature', 'thing', 'position', 'onThing', 'onPosition'))
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
globalScripts["reload"] = Scripts()
globalScripts["postReload"] = Scripts()
globalScripts["startup"] = Scripts()
globalScripts["shutdown"] = Scripts()
globalScripts["move"] = Scripts(('creature',))
globalScripts["appear"] = CreatureScripts()
globalScripts["disappear"] = CreatureScripts()
globalScripts["loot"] = CreatureScripts()
globalScripts["target"] = CreatureScripts()
globalScripts["thankYou"] = Scripts()
globalScripts["modeChange"] = Scripts()
globalScripts["questLog"] = Scripts()
globalScripts["chargeRent"] = Scripts()
globalScripts["equip"] = globalScripts["dress"] = globalScripts["wield"] = ThingScripts()
globalScripts["unequip"] = globalScripts["undress"] = globalScripts["unwield"] =ThingScripts()
globalScripts["requestChannels"] = Scripts()
globalScripts["joinChannel"] = Scripts()
globalScripts["leaveChannel"] = Scripts()
globalScripts["getChannelMembers"] = TriggerScripts()
globalScripts["level"] = Scripts()
globalScripts["skill"] = Scripts()

# Web stuff.
globalScripts["webPage"] = NCTriggerScripts(('request'))

# Login stuff
if config.letGameServerRunTheLoginServer:
    globalScripts["preSendLogin"] = Scripts()
    
globalEvents = []

# Events
def callEvent(time, func):
    func()
    globalEvents.append(call_later(time, callEvent, time, func))
    
def callEventDate(date, func):
    import dateutil.parser.parse as parse
    import datetime.datetime.now as now
    func()
    globalEvents.append(call_later(parse(date) - now(), callEventDate, date, func))
    
# Begin the scriptPool stuff, note: we got to add support for yield for the SQL stuff!
"""scriptPool = ThreadPool(5, config.suggestedGameServerScriptPoolSize)
scriptPool.start()"""

def run():
    global IS_ONLINE
    global IS_RUNNING
    IS_ONLINE = False
    IS_RUNNING = False
    return get('shutdown').run()
 
# XXX: port this. 
#reactor.addSystemEventTrigger('before','shutdown',run)

def handleModule(name):
    try:
        modules = __import__('%s.%s' % (config.dataDirectory, name), globals(), locals(), ["*"], 0)
    except:
        (exc_type, exc_value, exc_traceback) = sys.exc_info()

        #tb_list = traceback.extract_tb(exc_traceback)
        #tb_list = traceback.format_list(tb_list)
        
        print("--------------------------")
        # This may not be available.
        try:
            print(("EXCEPTION IN SCRIPT (%s):" % exc_value.filename))
        except AttributeError:
            print("EXCEPTION IN SCRIPT:")
            
        #for elt in tb_list[1:]:
        #    print(elt)
        #traceback.print_last()#exc_traceback)
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        
        
        print("--------------------------")
        
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
    if config.enableWebProtocol:
        handleModule("web")
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
    process = yield get("reload").run()
    if process == False:
        print("[WARNING]: Reload cancelled.")
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

    # Cleanups
    reimportCleanup()
        
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

    # Call gc.collect(). May be needed.
    gc.collect()
    
    # postReload.
    get("postReload").run()
    
def reimportCleanup():
    for script in globalScripts.values():
        if isinstance(script, Scripts):
            for func in script.weaks:
                script.scripts.remove(func)
            
        elif type(script) == TriggerScripts:
            for (trigger, func) in script.weaks:
                script.scripts[trigger].remove(func)
                if len(script.scripts[trigger]) == 0:
                    del script.scripts[trigger]
            
        elif type(script) == RegexTriggerScripts:
            for (trigger, func) in script.weaks:
                script.scripts[trigger][0].remove(func)
                if len(script.scripts[trigger][0]) == 0:
                    del script.scripts[trigger]
                            
        elif isinstance(script, ThingScripts):
            for (trigger, func) in script.weaks:
                script.scripts[trigger].remove(func)
                if len(script.scripts[trigger]) == 0:
                    del script.scripts[trigger]
                    
            for trigger in script.thingScripts.copy():
                for func in script.thingScripts[trigger][:]:
                    if not func:
                        script.thingScripts[trigger].remove(func)
                if len(script.thingScripts[trigger]) == 0:
                    del script.thingScripts[trigger]
        script.weaks = set()

# This is the function to get events, it should also be a getAll, and get(..., creature)
get = globalScripts.get
def register(type, *argc):
    def _wrapper(f):
        object = globalScripts[type]
        iargs = inspect.getargspec(f)
        vars = iargs[0]
        # Step 1, check if it has **f
        hasKeyword = bool(iargs[2])
        
        # Step 2, verify parameters
        if object.parameters and not hasKeyword:
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
    globalEvents.append(call_later(timeleap, callEvent, timeleap, callback))
    
def regEventTime(date, callback):
    import dateutil.parser.parse as parse
    import datetime.datetime.now as now
    globalEvents.append(call_later(parse(date) - now(), callEventDate, date, callback))
    
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
            #if isPlayer:
            #    #check.append("if not creature.isPlayer() or not creature.hasGroupFlags(*%s): return" % groupFlags)
        else:
            raise TypeError("Calling scriptsystem.access() with invalid parameter %s" % arg)
            
    # Notice: We may make a optimized wrapper call when len(groupFlags) == 1 using creature.hasGroupFlag(unwrapperGroupFlag).
    def _wrapper(f):
        """iargs = inspect.getargspec(f)
        vars = ", ".join(iargs[0])
        if iargs[2]:
            if vars:
                vars += ", **k"
            else:
                vars = "**k"
        """
        def inner(**k):
            if k['creature'].isPlayer() and k['creature'].hasGroupFlags(*groupFlags):
                return f(**k)
        return inner
    return _wrapper

# A special post-loading cache thingy.
postLoadEntries = {}

def registerForAttr(type, attr, callback):
    postLoadEntries.setdefault(attr, []).append((type, callback))

def handlePostLoadEntries():
    _unpackPostLoad = list(postLoadEntries.items())
    for id, attr in game.item.items.items():
        for key, entries in _unpackPostLoad:
            if key in attr:
                for entry in entries:
                    globalScripts[entry[0]].register(id, entry[1])


    postLoadEntries.clear()

# A register function for classes. It's cool, because it keeps state. No param vertification tho.
def registerClass(type, *argc):
    def _wrapper(c):
        assert isinstance(c, type)

        object = globalScripts[type]

        _class_ = c()        
        def function_class_wrapper(*a, **k): return _class_

        object.register(*argc, callback=function_class_wrapper)
        

    return 
