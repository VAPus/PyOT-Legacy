# This file is quite important because it handles the script loading!

import glob, os

__all__ = []
for mod in glob.glob("data/monsters/*.py"):
    modm = mod.split(os.sep)[-1].replace('.py', '')
    if modm == "__init__":
        continue

    __all__.append(modm)
    
#Our own kind of scriptsystem use this
__paths__ = []
for mod in glob.glob("data/monsters/*/__init__.py"):
    modm = mod.split(os.sep)[-2]
    if modm == "." or modm == "..":
        continue

    __paths__.append(modm)