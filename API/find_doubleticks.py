import sqlite3

conn = sqlite3.connect('energy.db')
c = conn.cursor()

c.execute("SELECT * FROM energy")
rows = c.fetchall()

count = 0

for i in range(1, len(rows)):
    if (rows[i][0] - rows[i-1][0]) < 1:
        count = count + 1
        print(rows[i][0])

print("Found {} doubleticks!".format(count))
