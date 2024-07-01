import sqlite3
con = sqlite3.connect("cars.db")
cur = con.cursor()
SQL ="ALTER TABLE car ADD COLUMN img VARCHAR(50)"

cur.execute(SQL)

