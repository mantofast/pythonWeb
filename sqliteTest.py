__author__ = 'Administrator'
import sqlite3

conn = sqlite3.connect('test.db')
cursor = conn.cursor()
#cursor.execute('create table user (id varchar(20) primary key, name varchar(20))')
#cursor.execute('insert into user (id, name) values (\'1\', \'Michael\')')
print "rowcount= "
print cursor.rowcount
cursor.close()
conn.commit()
conn.close()

conn1 = sqlite3.connect('test.db')
cursor = conn1.cursor()

cursor.close()
conn1.close()





