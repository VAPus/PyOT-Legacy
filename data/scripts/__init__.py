# This file is quite important because it handles the script loading!

import glob, os
from twisted.python import log

__all__ = []
for mod in glob.glob("data/scripts/*.py"):
 modm = mod.split(os.sep)[-1].replace('.py', '')
 if modm is "__init__":
   continue

 __all__.append(modm)
log.msg("ScriptSystem found %d modules %s" % (len(__all__), str(__all__)))