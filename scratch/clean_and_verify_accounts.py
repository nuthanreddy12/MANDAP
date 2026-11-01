import sys
sys.path.insert(0, ".")
import sqlite3
from backend.core.auth import get_password_hash

conn = sqlite3.connect("mandap.db")
c = conn.cursor()

# Ensure the 4 staff accounts exist with correct passwords and roles
staff = [
    ("u1", "Aarav Mehta", "aarav@theroyalknot.in", "owner", "AM", "Password123!"),
    ("u2", "Nisha Sharma", "nisha@theroyalknot.in", "planner", "NS", "Password123!"),
    ("u3", "Kabir Verma", "kabir@theroyalknot.in", "coordinator", "KV", "Password123!"),
    ("u4", "Rhea Kapoor", "rhea@theroyalknot.in", "finance_manager", "RK", "Password123!"),
]

for uid, name, email, role, avatar, pwd in staff:
    pwd_hash = get_password_hash(pwd)
    c.execute("""
        INSERT INTO users (id, name, email, role, avatar_initials, password_hash)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            name=excluded.name,
            role=excluded.role,
            avatar_initials=excluded.avatar_initials,
            password_hash=excluded.password_hash
    """, (uid, name, email, role, avatar, pwd_hash))

# Ensure Priya Mehra (customer)
priya_hash = get_password_hash("Password123!")
c.execute("""
    INSERT INTO users (id, name, email, role, avatar_initials, password_hash)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(email) DO UPDATE SET
        name=excluded.name,
        role=excluded.role,
        avatar_initials=excluded.avatar_initials,
        password_hash=excluded.password_hash
""", ("u_cust_priya", "Priya Mehra", "priya.mehra@gmail.com", "customer", "PM", priya_hash))

# Ensure customer invitation code ROYAL-MK-2026 is properly linked
c.execute("""
    INSERT INTO customer_invitations (id, wedding_id, invitation_code, client_email, client_name, is_claimed, claimed_by_user_id)
    VALUES ('cinv_1', 'w1', 'ROYAL-MK-2026', 'priya.mehra@gmail.com', 'Priya Mehra', 1, 'u_cust_priya')
    ON CONFLICT(id) DO UPDATE SET
        wedding_id='w1',
        invitation_code='ROYAL-MK-2026',
        client_email='priya.mehra@gmail.com',
        client_name='Priya Mehra',
        is_claimed=1,
        claimed_by_user_id='u_cust_priya'
""")

# Clean up ephemeral flow/login test users
c.execute("DELETE FROM users WHERE email LIKE 'flow.%' OR email LIKE 'login.%' OR email LIKE 'malicious.%'")
c.execute("DELETE FROM customer_invitations WHERE client_email LIKE 'flow.%' OR client_email LIKE 'login.%' OR client_email LIKE 'malicious.%'")

conn.commit()

c.execute("SELECT id, name, email, role, avatar_initials FROM users ORDER BY id")
users = c.fetchall()
print("Active Canonical Users:")
for u in users:
    print(" ", u)

conn.close()
