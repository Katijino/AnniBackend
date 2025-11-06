import sqlite3

conn = sqlite3.connect("database.db")
conn.execute("DROP TABLE IF EXISTS timeline;")
conn.execute("DROP TABLE IF EXISTS future_plans;")
conn.executescript(open("schema.sql").read())
conn.close()
print("✅ Database recreated.")
