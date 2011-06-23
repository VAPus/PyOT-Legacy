# This file is quite important because it handles the script loading!

import glob
__all__ = []
for mod in glob.glob("data/scripts/*.py"):
 modm = mod.split('/')[-1].replace('.py', '')
 print "Module found! %s" % modm
 __all__.append(modm)