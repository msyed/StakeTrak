import sqlite3 as lite
import sys


con = lite.connect('ASG.db')

with con:    
    
    cur = con.cursor()    
    cur.execute("SELECT * FROM ENTITIES")

    rows = cur.fetchall()

    for row in rows:
        print row