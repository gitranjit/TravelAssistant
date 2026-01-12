import sqlite3

conn = sqlite3.connect("D:\\TravelAssistant\\database\\flights.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS flight_searches (
    search_id TEXT PRIMARY KEY,
    departure TEXT,
    arrival TEXT,
    outbound_date TEXT,
    return_date TEXT,
    trip_type TEXT,
    adults INTEGER,
    children INTEGER,
    min_price REAL,
    max_price REAL,
    flight_count INTEGER,
    created_at TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS flight_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_id TEXT,
    flight_data TEXT,
    FOREIGN KEY (search_id) REFERENCES flight_searches(search_id)
);
""")

conn.commit()
conn.close()
