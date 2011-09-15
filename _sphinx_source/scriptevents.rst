****************************
  Scriptable events in PyOT
****************************

:Author: Stian Andreassen (:vapus:`members/1-Stian`)
:Release: |release|
:Date: |today|

PyOT have several scriptable events you and use to interact with the core behavior (you and also overwrite the core calls from scripts aswell):

Events are registered using the global function ``reg`` (linkes to :func:`game.scriptsystem.reg`) or ``regFirst`` (linkes to :func:`game.scriptsystem.regFirst`).
All parameters are optional, if you don't intend to use them all (we suggest to add it regardless) you add "\**k" parameter to the end.

The registration function:

**For Scripts()**:

    .. function:: reg(type, callback)
    
    Register a ``callback`` (function) to the ``type`` script event.
    
**For TriggerScripts()**:

    .. function:: reg(type, trigger, callback)
    
    Register a ``callback`` (function) to the ``type`` script event. Which is called when the ``trigger`` matches.

**For ThingScripts() and CreatureScripts()**:

    .. function:: reg(type, id, callback [, toid=None])
    
    Register a ``callback`` (function) to the ``type`` script event. ``id`` is the identifier in which things are identified for this callback to be called.

    * It can be a number and it will be checked up against the things thingId(). Example: reg("use", 1234, onUse)
    * It can also a list of number to register bind to, or a range. Example: reg("useWith", (1142, 1234), onUse)
    * The third option is to use a string, a script will match against the things actions. Actionids is strings aswell. reg("use", "item", onUseAnyItem) or reg("lookAt", "Wolf", onLookAtWolf)
    * The fourth option is to bind it directly to a thing, this is usually only good if you intend to make one item chain the next, for instance if you use two pieces of wood together, then the next time you use the wood you want it to burst into flames. Example (inside a callback): reg("use", thing, someCallback)

    
The events are:

.. function:: talkaction(creature, text)

    Called when a creature(Player) say something. (TriggerScript)
    
    :param creature: The creature that tries to say something.
    :type creature: usually :class:`game.player.Player`
    :param text: What was said.
    :type text: :func:`str`
    :returns: Return True/None will use the default internal behavior, while return False will stop it.
    
    :example:
    
    .. code-block:: python
           
        def onSay(creature, text):
            creature.message("Apperently you tried to say 'Hello', but was intercepted by this function")
            return False
           
        reg("talkaction", "Hello", onSay)


.. function:: talkactionFirstWord(creature, text)

    Called with the remaining text (can also be blank) when the creature(Player) say something that begins with the action it was registered for. (TriggerScript)
  
    :param creature: The creature that tries to say something.
    :type creature: usually :class:`game.player.Player`
    :param text: What was said.
    :type text: :func:`str`
    :returns: Return True/None will use the default internal behavior, while return False will stop it.
    
    :example:
    
    .. code-block:: python
           
        def onSay(creature, text):
            creature.message("I was asked to repeat %s" % text)
            return False
           
        reg("talkactionFirstWord", "!repeater", onSay)
        
.. function:: use(creature, thing, position, stackpos, index)

    Called when a thing is used and the creature is max 1 square away from it. This is called AFTER farUse. (ThingScript)
    
    :param creature: The creature that tries to use something.
    :type creature: usually :class:`game.player.Player`
    :param thing: The thing that was used.
    :type thing: usually :class:`core.item.Item`
    :param position: The positon the thing have.
    :type position: :func:`list`
    :param stackpos: The position in the tile stack the thing have.
    :type stackpos: :func:`int`
    :param index: If the item was called inside a container, this is the position in the container stack.
    :type index: :func:`int`    
    :returns: Have no meaning.
    
    :example:
    
    .. code-block:: python
           
        def onUse(creature, thing, position, **k):
            if thing.isItem():
                creature.message("I seem to have used a '%s' on position %s" % (thing.name(), str(position)))

           
        reg("use", 1234, onUse)
        
.. function:: farUse(creature, thing, position, stackpos, index)

    Called when a thing is used. This is called BEFORE use. (ThingScript)
    
    :param creature: The creature that tries to use something.
    :type creature: usually :class:`game.player.Player`
    :param thing: The thing that was used.
    :type thing: usually :class:`core.item.Item`
    :param position: The positon the thing have.
    :type position: :func:`list`
    :param stackpos: The position in the tile stack the thing have.
    :type stackpos: :func:`int`
    :param index: If the item was called inside a container, this is the position in the container stack.
    :type index: :func:`int`    
    :returns: ``False`` will prevent the use events from running.
    
    :example:
    
    .. code-block:: python
           
        def onUse(creature, position, **k):
            creature.message("I seem to be %d steps away from this thing" % creature.distanceStepsTo(position))

           
        reg("farUse", 1234, onUse)
        
.. function:: useWith(creature, thing, position, stackpos, onThing, onPosition, onStackpos)

    Called when a thing is used. Note, this is called with twice with item in both directions, so you should not need to bind it to all possible things. (ThingScript)
    
    :param creature: The creature that tries to use something.
    :type creature: usually :class:`game.player.Player`
    :param thing: The thing that matched the register functions parameters.
    :type thing: usually :class:`core.item.Item`
    :param position: The positon the thing have.
    :type position: :func:`list`
    :param stackpos: The position in the tile stack the thing have.
    :type stackpos: :func:`int`
    
    :param onThing: The thing that the ``thing``` was used against.
    :type onThing: :class:`game.item.Item` or :class:`game.creature.Creature`
    :param onPosition: The positon the ``onThing`` have.
    :type onPosition: :func:`list`
    :param onStackpos: The position in the tile stack the ``onThing`` have.
    :type onStackpos: :func:`int`
    
    :returns: Have no meaning.
    
    :example:
    
    .. code-block:: python
           
        lockedDoors = 1209, 1212, 1231, 1234, 1249, 1252, 3535, 3544, 4913, 4616, 5098, 5107, 5116, 5125, 5134, 5137, 5140, 5143, 5278, 5281, 5732, 5735,\
                        6192, 6195, 6249, 6252, 6891, 6900, 7033, 7042, 8541, 8544, 9165, 9168, 9267, 9270, 10268, 10271, 10468, 10477 
        keys = range(2086, 2092+1)
        def onUseKey(creature, thing, onThing, onPosition, **k):
            if not onThing.actions or not onThing.itemId in lockedDoors or not onThing.itemId-1 in lockedDoors or not onThing.itemId-2 in lockedDoors:
                return
            
            canOpen = False
            for aid in thing.actions:
                if aid in onThing.actions:
                    canOpen = True
                    
            if not canOpen:
                creature.message("The key does not match.")
                return
                
            if onThing.itemId in lockedDoors:
                engine.transformItem(onThing, onThing.itemId+2, onPosition)
            elif onThing.itemId-2 in lockedDoors:
                engine.transformItem(onThing, onThing.itemId-2, onPosition)
            else:
                engine.transformItem(onThing, onThing.itemId-1, onPosition)

        reg('useWith', keys, onUseKey)