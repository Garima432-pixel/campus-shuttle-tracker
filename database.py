import sqlite3

conn = sqlite3.connect("shuttle.db")
cursor = conn.cursor()

cursor.execute("PRAGMA foreign_keys = ON;")
##created a routes table
cursor.execute("""
CREATE TABLE IF NOT EXISTS routes (
    id TEXT PRIMARY KEY,
    name TEXT,
    color TEXT
)
""")


# created a stops table and used forign keys so that it matches the id in routes table
cursor.execute("""
CREATE TABLE IF NOT EXISTS stops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id TEXT,
    name TEXT,
    latitude REAL,
    longitude REAL,
    stop_order INTEGER,
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
)
""")


# Inserting routes in route table

##created a list of tuple
routes_data=[
    ("route_1","Athelete Ground Loop", "#2563eb"),
    ("route_2","15 Street Loop","#f97316")
]

##used executory instead of the execute beacuse the execute only accept one set of the values while executemary
##can take more than one set of the value by looping on the list
cursor.executemany(""" 
INSERT OR IGNORE INTO routes (id ,name , color)
VALUES (?,?,?)""",routes_data)

stops_data = [
    # Route 1: Athlete Ground Loop
    ("route_1", "Main Gate", 27.801558, 75.036106, 1),
    ("route_1", "ABB", 27.804224, 75.031385, 2),
    ("route_1", "Mess", 27.803579, 75.030946, 3),
    ("route_1", "Athlete Ground", 27.802583, 75.030098, 4),
    ("route_1", "Mess", 27.803579, 75.030946, 5),
    ("route_1", "ABB", 27.804224, 75.031385, 6),
    ("route_1", "Main Gate", 27.801558, 75.036106, 7),

    # Route 2: 15 Street Loop
    ("route_2", "Main Gate", 27.801558, 75.036106, 1),
    ("route_2", "ABB", 27.804224, 75.031385, 2),
    ("route_2", "Mess", 27.803579, 75.030946, 3),
    ("route_2", "Tapovan", 27.801216, 75.029079, 4),
    ("route_2", "15 Street", 27.798435, 75.027298, 5),
    ("route_2", "Tapovan", 27.801216, 75.029079, 6),
    ("route_2", "Mess", 27.803579, 75.030946, 7),
    ("route_2", "ABB", 27.804224, 75.031385, 8),
    ("route_2", "Main Gate", 27.801558, 75.036106, 9),
]
cursor.execute("DELETE  FROM stops")

cursor.executemany(""" 
INSERT INTO stops (route_id,name,latitude,longitude,stop_order)
VALUES (?,?,?,?,?)
""",stops_data)

conn.commit()
conn.close()

print("shuttle.db populated successfully")
