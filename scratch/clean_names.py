import sqlite3

conn = sqlite3.connect('mandap.db')
c = conn.cursor()

def clean_str(s):
    if not s:
        return s
    for bad in [chr(215), '\u00d7', '\u2013', '\u2014', '\ufffd']:
        s = s.replace(bad, 'x')
    return s.replace('  ', ' ')

c.execute('SELECT id, couple_names FROM enquiries')
for eid, name in c.fetchall():
    if name:
        clean = clean_str(name)
        c.execute('UPDATE enquiries SET couple_names = ? WHERE id = ?', (clean, eid))

c.execute('SELECT id, couple_names FROM weddings')
for wid, name in c.fetchall():
    if name:
        clean = clean_str(name)
        c.execute('UPDATE weddings SET couple_names = ? WHERE id = ?', (clean, wid))

conn.commit()

c.execute('SELECT id, couple_names FROM enquiries')
print('Updated enquiries:', c.fetchall())

c.execute('SELECT id, couple_names FROM weddings')
print('Updated weddings:', c.fetchall())

conn.close()
