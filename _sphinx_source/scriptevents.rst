****************************
  Scriptable events in PyOT
****************************

:Author: Stian Andreassen (:vapus:`members/1-Stian`)
:Release: |release|
:Date: |today|

**NB! This page is work in progress!**

PyOT have several scriptable events you and use to interact with the core behavior (you and also overwrite the core calls from scripts aswell):

Events are registered using the global function ``reg`` (linkes to :func:`game.scriptsystem.reg`) or ``regFirst`` (linkes to :func:`game.scriptsystem.regFirst`).
All parameters are optional, if you don't intend to use them all (we suggest to add it regardless) you add "\**k" parameter to the end.

The registration function:

**For Scripts()**:

    .. function:: reg(type, callback [, weakfunc=True])
    
    Register a ``callback`` (function) to the ``type`` script event. ``Weakfunc`` should only be set to False if the event gets generated inside the function, non-weak functions won't be reloaded! 
    
**For TriggerScripts()**:

    .. function:: reg(type, trigger, callback [, weakfunc=True])
    
    Register a ``callback`` (function) to the ``type`` script event. Which is called when the ``trigger`` matches. ``Weakfunc`` should only be set to False if the event gets generated inside the function, non-weak functions won't be reloaded!

**For ThingScripts() and CreatureScripts()**:

    .. function:: reg(type, id, callback [, weakfunc=True])
    
    Register a ``callback`` (function) to the ``type`` script event. ``id`` is the identifier in which things are identified for this callback to be called.

    * It can be a number and it will be checked up against the things thingId(). Example: reg("use", 1234, onUse)
    * It can also a list of number to register bind to, or a range. Example: reg("useWith", (1142, 1234), onUse)
    * The third option is to use a string, a script will match against the things actions. Actionids is strings aswell. reg("use", "item", onUseAnyItem) or reg("lookAt", "Wolf", onLookAtWolf)
    * The fourth option is to bind it directly to a thing, this is usually only good if you intend to make one item chain the next, for instance if you use two pieces of wood together, then the next time you use the wood you want it to burst into flames. Example (inside a callback): reg("use", thing, someCallback)

    ``Weakfunc`` should only be set to False if the event gets generated inside the function, non-weak functions won't be reloaded!

Global Events use these registration functions:

    .. function:: regEvent(timeleap, callback)

    Register ``callback`` (function) to happend after ``timeleap`` seconds

    .. function:: regEventDate(date, callback)

    Register ``callback`` (function) to happend next time the clock is ``date``. Date is a string and can be "23:00", "10:00am", "16:00:15", or full date format such as "23:00 MM-DD-YYYY" or "Thu Sep 25 10:36:28", you can also use RFC822 format: "Thu, 25 Sep 2003 10:49:41 -0300".

    The format is documented here: http://labix.org/python-dateutil#head-c0e81a473b647dfa787dc11e8c69557ec2c3ecd2

A little note is that global events are always cleared on reload, there is no option to prevent it.



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
    :type thing: usually :class:`game.item.Item`
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
    :type thing: usually :class:`game.item.Item`
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

    Called when a thing is used and the thing is 1 square or less away from the creature. Note, this is called with twice with item in both directions, so you should not need to bind it to all possible things. (ThingScript)
    
    :param creature: The creature that tries to use something.
    :type creature: usually :class:`game.player.Player`
    :param thing: The thing that matched the register functions parameters.
    :type thing: usually :class:`game.item.Item`
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
                transformItem(onThing, onThing.itemId+2, onPosition)
            elif onThing.itemId-2 in lockedDoors:
                transformItem(onThing, onThing.itemId-2, onPosition)
            else:
                transformItem(onThing, onThing.itemId-1, onPosition)

        reg('useWith', keys, onUseKey)
        
.. function:: farUseWith(creature, thing, position, stackpos, onThing, onPosition, onStackpos)

    Called when a thing is used. Note, this is called with twice with item in both directions, so you should not need to bind it to all possible things. And it's called BEFORE useWith. (ThingScript)
    
    :param creature: The creature that tries to use something.
    :type creature: usually :class:`game.player.Player`
    :param thing: The thing that matched the register functions parameters.
    :type thing: usually :class:`game.item.Item`
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
        def onUseKey(creature, onThing, **k):
            if onThing.itemId in lockedDoors:
                creature.message("Can't reach the lock of the %s" % onThing.rawName())

        reg('farUseWith', keys, onUseKey)
        
.. function:: login(creature)

    Called when a player login. (Script)
    
    :param creature: Player object.
    :type creature: :class:`game.player.Player`
    
    :returns: Have no meaning.
    
    :example:
        
    .. code-block:: python
    
        def onLogin(creature):
            creature.message("Welcome back %s" % creature.name())
           
        reg("login", onLogin)
            
.. function:: logout(creature)

    Called when a player logout. (Script)
    
    :param creature: Player object.
    :type creature: :class:`game.player.Player`
    
    :returns: Have no meaning.
    
    :example:
        
    .. code-block:: python
    
        def onLogout(creature):
            creature.save()
                
        reg("logout", onLogout)
        
.. function:: walkOn(creature, thing, position, fromPosition)
    
    Called when the creature walks on a item. (ThingScript)
    
    :param creature: The creature that walked on this item.
    :type creature: :class:`game.creature.Creature`
    :param thing: The item that triggered this call.
    :type thing: :class:`game.item.Item`
    :param positon: The position where this item is.
    :type position: :func:`list`

    :returns: Have no meaning.
    
    :example:
        
    .. code-block:: python
        
        def walkOn(creature, thing, **k):
            creature.message("You can't stand here!")
            creature.move(NORTH)
            
        reg("walkOn", 1234, walkOn)
        
.. function:: walkOff(creature, thing, position)
    
    Called when the creature walks off a item. (ThingScript)
    
    :param creature: The creature that walked on this item.
    :type creature: :class:`game.creature.Creature`
    :param thing: The item that triggered this call.
    :type thing: :class:`game.item.Item`
    :param positon: The position where this item is.
    :type position: :func:`list`

    :returns: Have no meaning.
    
    :example:
        
    .. code-block:: python
        
        def walkOff(creature, **k):
            creature.message("You left this holy place!")
            creature.modifyHealth(-30)
            
        reg("walkOff", 1234, walkOff)
        
.. function:: preWalkOn(creature, thing, position, oldTile, newTile)
    
    Called when the creature walks on a item. (ThingScript)
    
    :param creature: The creature that walked on this item.
    :type creature: :class:`game.creature.Creature`
    :param thing: The item that triggered this call.
    :type thing: :class:`game.item.Item`
    :param positon: The position where this item is.
    :type position: :func:`list`
    :param newTile: The new tile that the creature might walk on.
    :param oldTile: The current tile where the creature is placed.
    
    :returns: ``False`` will prevent the creature from walking on to this tile.
    
    :example:
        
    .. code-block:: python
        
        def tileCheck(creature, **k):
            creature.message("We won't allow you to touch this holy ground!")
            return False
            
        reg("preWalkOn", 1234, tileCheck)
        
.. function:: lookAt(creature, thing, position, stackpos)

    Called when a player looks at a thing. (ThingScript)
    
    :param creature: The creature that looks at something.
    :type creature: :class:`game.player.Player`
    :param thing: The thing that the player tries to look at.
    :type thing: :class:`game.item.Item` or :class:`game.creature.Creature`
    :param position: The positon the thing have.
    :type position: :func:`list`
    :param stackpos: The position in the tile stack the thing have.
    :type stackpos: :func:`int`
 
    :returns: Return False prevents the default behavior.
    
    :example:
    
    .. code-block:: python
           
        def lookAt(creature, **k):
            creature.say("I can't look, that thing scare the crap out of me!")
            return False

           
        reg("lookAt", 1234, lookAt)

.. function:: addMapItem(thing)
    
    Called in the map loader when ``thing`` is gonna be put on to the map. (ThingScript)
    
    :returns: Item to add to the map (usually just ``thing``)
    
.. function:: playerSayTo(creature, creature2, ...)

    Currently not in use. (CreatureScript)
    
.. function:: close(creature, thing, index)
    
    Called when a container is closed.
    
.. function:: hit(creature, creature2, damage, type, textColor, magicEffect)

    Called when ``creature2`` hits ``creature``. damage, type, textColor and magicEffect is one item lists. Update them update the data used in the hit process. (CreatureScript)
    
    :returns: Return False prevent the hit from happening.
    
.. function:: death(creature, creature2, corpse)

    Called when ``creature`` gets killed by ``creature2``. Change the creature.alive value or add health to the creature to resurect him and prevent the rest of the death code from happening (CreatureScript)

.. function:: respawn(creature)

    Called as a notification call when a creature respawns. (Script)

.. function:: reload()

    Called when the server reloads.

.. function:: startup()

    Called when the server starts up. Useful to invoke core hooks or initialize your own scripts.

.. function:: shutdown()

    Called just before the server shuts down.

.. function:: move(creature)

    Called when a creature moves.

    :returns: False will prevent the creature from moving.

    :example:

    .. code-block:: python

        def preventWalking(creature):
            if random.randint(0, 10) == 1:
                creature.message("Your leg hurt too much")
                return False

        reg('move', preventWalking)

.. function:: appear(creature, creature2)
    
    Called when creature2 appear in the view field of creature (and reverse). (CreatureScript)

.. function:: disappear(creature, creature2)

    Called when creature2 appear in the view field of creature (and reverse). (CreatureScript)

.. function:: loot(creature, creature2, loot, maxSize)

    Called when creature dies and generate loot for creature2. maxSize is the amount of slots currently in the bag, you can't add items over this. (CreatureScript)

    :returns: New loot list.

.. function:: target(creature, creature2, attack)

    Called when creature target creature2, attack=True if the creature intend to attack it, false otherwise (follow etc). (CreatureScript)

.. function:: rotate(creature, thing, position, stackpos)

    Called when creature tries to rotate ``thing`` on ``position`` with ``stackpos``. (ThingScript)

    :returns: ``False`` prevent the rotation of the thing.

.. function:: questLog(creature, questLog)

    Called with the raw questLog, modify it to change the questLog that is sent to the client. (script)

.. function:: modeChange(creature, chase, attack, secure)

    Called when a ``creature`` (Player) change the modes. The parameters are the new modes, you can compare them against the old modes (creature.modes). (Script)

    :returns: False to prevent mode change.

.. function:: equip(creature, thing, slot) / dress(creature, thing, slot) / wield(creature, thing, slot)

    Called when a Player equips ``thing`` on inventory slot ``slot`` (check up against enums). (ThingScript)

.. function:: deEquip(creature, thing, slot) / undress(creature, thing, slot) / unwield(creature, thing, slot)

    Called when a Player dequips ``thing`` on inventory slot ``slot`` (check up against enums). (ThingScript)

.. function:: chargeRent(house)

    Called when it's time to charge rent for the house (Script)

.. function:: requestChannels(creature, channels)

    Called when the player (creature) request the channels list. Channels is a dict containing all the channels. This dict might be modified directly. Or returned.
    Format is {id: Channel Object} (Script)

    :returns: (Optional) dict of channels to display.

.. function:: joinChannel(creature, channelId)

    Called when Player (creature) attempts to join a channel. (Script)

    :returns: False to prevent the player from joining this channel.

.. function:: leaveChannel(creature, channelId)

    Called when Player (creature) leaves the channel. Since this can't be stopped server sided (aside from rejoining the channel) this is just a notification call. (Script)

    :returns: No meaning.

.. function:: getChannelMembers(creature, channelId, text, type, members)
    Called when the system want to get a list of members to send the channel list too. This works in the same way as requestChannels does, except that the members list is a list and not a dict. (TriggerScript)