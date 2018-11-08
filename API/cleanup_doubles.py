import sqlite3

conn = sqlite3.connect('energy.db')
c = conn.cursor()

c.execute("SELECT * FROM energy")
rows = c.fetchall()

for i in range(1, len(rows)):
    if (rows[i][0] - rows[i-1][0]) < 1:
        c.execute("DELETE FROM energy WHERE timestamp == {};".format(rows[i][0]))
        conn.commit()
