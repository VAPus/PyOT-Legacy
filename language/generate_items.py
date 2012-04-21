# Include the config
import sys
sys.path.append('../')
import config

# Because mysql ain't that nice....
taken = set()

# More imports
import MySQLdb
db = MySQLdb.connect(host=config.sqlHost, user=config.sqlUsername, passwd=config.sqlPassword, db=config.sqlDatabase)
cursor = db.cursor()
cursor.execute("SELECT DISTINCT name, article, plural, sid FROM items")
for row in cursor.fetchall():
    pin = False

    if row[0] not in taken:
        print "# ID: %d" % row[3]
        print 'msgid "%s"' % row[0]
        pin = True

    if row[2] != row[0] and row[2] and row[2] not in taken:
        pre = ""
        if not pin: 
            print "# This will bug!"
            pre = "# "
        print '%smsgid_plural "%s"' % (pre, row[2])
        print '%smsgstr[0] ""' % pre
        print '%smsgstr[1] ""\n' % pre
        taken.add(row[2])
        taken.add(row[0])

    elif pin:
        print 'msgstr ""\n'
        taken.add(row[0])

    if pin:
        print 'msgid "%s %s"' % (row[1], row[0])
        print 'msgstr ""'
        print ""

cursor = db.cursor()
cursor.execute("SELECT DISTINCT value, sid FROM item_attributes WHERE `key` = 'description'")
for row in cursor.fetchall():
    if row[0] and row[0] not in taken:
        print "# Description for ID: %d" % row[1]
        print 'msgid "%s"' % row[0]
        print 'msgstr ""'
        print ""
        taken.add(row[0])


