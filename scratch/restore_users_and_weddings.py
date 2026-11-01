import sqlite3

conn = sqlite3.connect('mandap.db')
c = conn.cursor()

# Restore staff roles
c.execute("UPDATE users SET role = 'owner' WHERE email = 'aarav@theroyalknot.in'")
c.execute("UPDATE users SET role = 'planner' WHERE email = 'nisha@theroyalknot.in'")
c.execute("UPDATE users SET role = 'coordinator' WHERE email = 'kabir@theroyalknot.in'")
c.execute("UPDATE users SET role = 'finance_manager' WHERE email = 'rhea@theroyalknot.in'")

# Restore wedding assigned planners for tests
c.execute("UPDATE weddings SET assigned_planner = 'Nisha Sharma' WHERE id = 'w1'")
c.execute("UPDATE weddings SET assigned_planner = 'Kabir Verma' WHERE id = 'w2'")
c.execute("UPDATE weddings SET assigned_planner = 'Aarav Mehta' WHERE id = 'w3'")
c.execute("UPDATE weddings SET assigned_planner = 'Kabir Verma' WHERE id = 'w4'")

conn.commit()

c.execute("SELECT id, name, email, role FROM users WHERE role != 'customer'")
print("Staff users:", c.fetchall())

c.execute("SELECT id, couple_names, assigned_planner FROM weddings WHERE is_archived = 0")
print("Weddings:", c.fetchall())

conn.close()

