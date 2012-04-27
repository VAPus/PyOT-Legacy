# Include the config
import sys
sys.path.append('../')
sys.path.append('../core')
import config

# Because mysql ain't that nice...
taken = set()

# Plural/article forms.
import inflect

INFLECT = inflect.engine()

# SQL
import MySQLdb
db = MySQLdb.connect(host=config.sqlHost, user=config.sqlUsername, passwd=config.sqlPassword, db=config.sqlDatabase)
cursor = db.cursor()
cursor.execute("SELECT DISTINCT name, sid, stackable FROM items")
for row in cursor.fetchall():
    if not row[0]: continue
    pin = False
    word = row[0]
        
    if word not in taken:
        print "# ID: %d" % row[1]
        print 'msgid "%s"' % word
        pin = True

    plural = INFLECT.plural(word)
    if row[2] and plural and plural != word and plural not in taken:
        pre = ""
        if not pin: 
            print "# This will bug!"
            pre = "# "
        print '%smsgid_plural "%s"' % (pre, plural)
        print '%smsgstr[0] ""' % pre
        print '%smsgstr[1] ""\n' % pre
        taken.add(plural)
        taken.add(word)

    elif pin:
        print 'msgstr ""\n'
        taken.add(word)
            
    if pin:
        article = INFLECT.a(word)
        if article:
            print 'msgid "%s"' % (article)
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


