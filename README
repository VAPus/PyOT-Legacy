In order to run PyOT you need:
================================

* Python 2.7+ or Pypy 1.7+ (2.2+ are HIGHLY recommended)

* Twisted 10+ 

* zope.interface (any version that works with your twisted version, PyOT does't directly depend on this)

* MySQLdb 1.2.3+ (or pymysql) (1.2.4+ recommended)

* Optional: cjson/usjon/simplejson (gives a speedup to saving and loading of players when your using CPython)

* Optional: pywin32 if you intend to use IOCP (default on windows)

Links for Windows:
------------------

http://www.python.org/ftp/python/2.7.3/python-2.7.3.msi

Grab MySQL-python-1.2.4c1.win32.py2.7.exe http://www.lfd.uci.edu/~gohlke/pythonlibs/#mysql-python

http://pypi.python.org/packages/2.7/T/Twisted/Twisted-12.3.0.win32-py2.7.msi

http://sourceforge.net/projects/pywin32/files/pywin32/Build%20218/pywin32-218.win32-py2.7.exe/download

Grab zope.interface-4.0.2.win32-py2.7.‌exe http://www.lfd.uci.edu/~gohlke/pythonlibs/#zope.interface 

and last

Base-13.X.YY.win32-py2.7.exe (X = a month and YY = a day, this package gets updated all the time!) http://www.lfd.uci.edu/~gohlke/pythonlibs/#base

note: http://www.lfd.uci.edu/~gohlke/pythonlibs/ (This site also got 64bit editions of all the libs)


Installation
============

Copy "config.py.dist" to "config.py" and edit it to match your database settings.

Archlinux:
----------

pacman -S python2 mysql-python twisted python-cjson python-distribute



Ubuntu(10.10+) or Debian 6 wheezy (testing)+:
---------------------------------------------

apt-get install python-twisted python-setuptools python-cjson python-mysqldb python2.7

An alternative method is required on older versions of Ubuntu and Debian, since those versions only have python 2.6
or below as standard support. 



Debian 6 Squeeze:
-----------------

The easy way will be to update your debian sources to get Python 2.7, like this:

nano (or vi) /etc/apt/sources.list

add this line in the end of the document:

deb http://ftp.no.debian.org/debian/ testing main contrib

and save (nano = ctrl + O, followed up by CTRL + X to quit), (vi = ESC :w, followed up by :quit)

apt-get update

apt-get upgrade

Then follow the Debian Wheezy installation instructions above.




Documentation
=============

You can find additional documentation of PyOT here: http://vapus.net/pyot_doc/index.html

Useful scripting guide here: http://vapus.net/pyot_doc/scriptevents.html
