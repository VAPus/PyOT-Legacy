# This file is quite important because it handles the script loading!

import glob, os

__all__ = []
for mod in glob.glob("data/scripts/*.py"):
    modm = mod.split(os.sep)[-1].replace('.py', '')
    if modm is "__init__":
        continue

    __all__.append(modm)

#Our own kind of scriptsystem use this
paths = []
for mod in glob.glob("data/scripts/*/__init__.py"):
    modm = mod.split(os.sep)[-2]
    if modm == "." or modm == "..":
        continue

    paths.append(modm)
