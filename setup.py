from distutils.core import setup, Extension
import sys

try:
    sys.getwindowsversion()
    module1 = Extension('otcrypto', sources = ['core/otcrypto.c'], libraries = ["eay32"])
except:
    module1 = Extension('core/otcrypto', sources = ['core/otcrypto.c'], libraries = ["crypto"])    

setup (name = 'PyOT',
	   version = '1.0',
	   author="(C) Stian 2011",
	   description = 'PyOt Setup script',
       ext_modules = [module1])
