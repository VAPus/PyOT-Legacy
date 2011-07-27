# This file is quite important because it handles the script loading!

import glob, os

__all__ = []
for mod in glob.glob("data/scripts/*.py"):
    modm = mod.split(os.sep)[-1].replace('.py', '')
    if modm is "__init__":
        continue

    __all__.append(modm)