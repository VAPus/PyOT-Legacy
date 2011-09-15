****************************
  Scriptable events in PyOT
****************************

:Author: Stian Andreassen (:vapus:`members/1-Stian`)
:Release: |release|
:Date: |today|

PyOT have several scriptable events you and use to interact with the core behavior (you and also overwrite the core calls from scripts aswell):

Events are registered using the global function ``reg`` (linkes to :func:`game.scriptsystem.reg`) or ``regFirst`` (linkes to :func:`game.scriptsystem.regFirst`).
All parameters are optional, if you don't intend to use them all (we suggest to add it regardless) you add "**k" parameter to the end.

The events are:

.. function:: talkaction(creature, test)

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

