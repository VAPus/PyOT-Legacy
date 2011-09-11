****************************
  What's PyOT
****************************

:Author: Stian Andreassen (stian at vapus.net)
:Release: |release|
:Date: |today|

PyOT is a server written in Python, using that Twisted framework that emulates the Tibia protocol.

PyOT is super fast, and uses diffrent methods than other projects. Some of which is:

* Async SQL
* Async core code
* Async, multithreaded scriptsystem
* Ability to utilize epoll (Linux), iocp (Windows) and kpoll (FreeBSD)
* Ability to utilize jit from pypy (currently the logger module is a bit of a slowdown, we'll work on it, or just wait until pypy 1.7 which seems to fix this)
* Very flexible core
* Very configurable core
* Very fast save format (save takes 0.2ms per player, scales over several sql connections, allowing for upto 10k saves per second)
* Sector maps, dynamic load and unload for optimal memory usage (down to ~22MB on a 32bit system)


The Future for PyOT
=========================
* Make all core logic possible to tap into using scripts (say, a war system should be possible to make entierly using scripts)
* More intelligent monsters
* Better NPC framework
* Even more configurable behavior
* Core support for all client features
* Support for Houses
* Support for Tile saving
* Support for scripted mapping (say you want to add a extra floor to houses using scripts)
* Finish a base of scripts that emulates the default behavior rather well (can also be configurable)
* Document all features
* Write a couple of pages on scripting
* Write a couple of pages on monsters, npc and other resources
* Write a couple of pages on core development
* Write a couple of pages on things should as installation
* Write a much more detailed :ref:`todo`  list.

Ideas (not yet desided):

* Support for own Status protocol
* Support for dynamic upgrade of custom clients over a custom protocol (useful for say, autoupdaters)


PyOT Features (so far)
=======================
TODO: Write this one.

When will we see PyOT v1.0
===========================
We'll likely release v1.0 once all the features in the future section and our :ref:`todo` list is done.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`todo`
.. toctree::
   :maxdepth: 2

   todo

