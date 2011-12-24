import glob, os

__all__ = []
for mod in glob.glob("data/monsters/Goblins/*.py"):
    modm = mod.split(os.sep)[-1].replace('.py', '')
    if modm == "__init__":
        continue

    __all__.append(modm)