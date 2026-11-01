import sqlite3

conn = sqlite3.connect("mandap.db")
c = conn.cursor()

# 1. Inspect duplicate unique_quote.pdf entries
c.execute("SELECT id FROM documents WHERE filename = 'unique_quote.pdf' ORDER BY created_at ASC")
ids = [r[0] for r in c.fetchall()]
print(f"Total unique_quote.pdf documents found: {len(ids)}")

if len(ids) > 1:
    keep_id = ids[0]
    delete_ids = ids[1:]
    print(f"Keeping {keep_id}, deleting {len(delete_ids)} duplicates: {delete_ids}")
    
    placeholders = ",".join(f"'{i}'" for i in delete_ids)
    c.execute(f"DELETE FROM documents WHERE id IN ({placeholders})")
    
    # Also clean up duplicate quotes referencing deleted documents
    c.execute(f"DELETE FROM quotes WHERE document_id IN ({placeholders})")
    
    conn.commit()
    print("Database deduplication completed successfully!")
else:
    print("Already 1 or 0 unique_quote.pdf documents.")

# Verify final counts
c.execute("SELECT filename, count(*) FROM documents WHERE wedding_id='w1' GROUP BY filename")
for r in c.fetchall():
    if r[1] > 1:
        print(f"WARNING: duplicate filename remaining: {r}")
    else:
        print(f"Unique: {r[0]} (count: {r[1]})")

conn.close()

