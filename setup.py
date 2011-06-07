from distutils.core import setup, Extension
 
module1 = Extension('core/otcrypto', sources = ['core/otcrypto.c'], libraries = ["crypto"])

setup (name = 'PyOT',
	   version = '1.0',
	   author="(C) Stian 2011",
	   description = 'PyOt Setup script',
       ext_modules = [module1])
