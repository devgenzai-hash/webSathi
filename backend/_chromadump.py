import sqlite3, glob

hits = glob.glob("chroma_data/**/*.sqlite3", recursive=True) + glob.glob("chroma_data/*.sqlite3")
print("Found:", hits)
if not hits:
    print("No chroma sqlite3 found")
    exit()

db = sqlite3.connect(hits[0])
tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
print("\n=== TABLES ===")
for t in tables:
    try:
        count = db.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
        cols  = [c[1] for c in db.execute(f"PRAGMA table_info([{t}])").fetchall()]
        print(f"  {t}: {count} rows")
        print(f"    cols: {cols}")
    except Exception as e:
        print(f"  {t}: ERROR -> {e}")

print("\n=== SAMPLE DATA ===")
for t in tables:
    try:
        rows = db.execute(f"SELECT * FROM [{t}] LIMIT 2").fetchall()
        if rows:
            print(f"\n-- {t} --")
            for r in rows:
                print(" ", r)
    except Exception as e:
        print(f"  {t}: {e}")
