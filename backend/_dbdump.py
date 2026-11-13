import sqlite3

db = sqlite3.connect("app.db")
db.row_factory = sqlite3.Row

tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]

print("=== TABLES ===")
for t in tables:
    count = db.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
    print(f"  {t}: {count} rows")

print()
for t in tables:
    print(f"=== {t.upper()} ===")
    rows = db.execute(f"SELECT * FROM [{t}] LIMIT 5").fetchall()
    if rows:
        print("  cols:", list(rows[0].keys()))
        for r in rows:
            print(" ", dict(r))
    else:
        print("  (empty)")
    print()
