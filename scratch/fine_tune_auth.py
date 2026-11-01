# 1. Update customer.py
with open("backend/api/customer.py", "r", encoding="utf-8") as f:
    cust = f.read()

old_cust_block = '''    norm_email = payload.email.strip().lower()
    user = db.query(User).filter(User.email.ilike(norm_email)).first()
    if not user:
        # Fallback / Demo Access: Auto-create customer account for local testing
        user = User(
            id=f"u_cust_{uuid.uuid4().hex[:8]}",
            auth_user_id=f"sub_cust_{uuid.uuid4().hex[:12]}",
            name=norm_email.split('@')[0].capitalize(),
            email=norm_email,
            role="customer",
            avatar_initials=norm_email[0].upper(),
            created_at=datetime.datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif user.role != "customer":
        # Allow planner or staff account to view customer sanctuary in demo mode
        user.role = "customer"
        db.commit()
        db.refresh(user)

    # Verify customer is linked to an active wedding
    wedding = (
        db.query(Wedding)
        .filter(
            (Wedding.customer_user_id == user.id) | (Wedding.client_email.ilike(norm_email)),
            Wedding.is_archived == False,
        )
        .first()
    )
    if not wedding:
        inv = (
            db.query(CustomerInvitation)
            .filter(
                (CustomerInvitation.claimed_by_user_id == user.id) |
                (CustomerInvitation.client_email.ilike(norm_email))
            )
            .first()
        )
        if inv:
            wedding = db.query(Wedding).filter(Wedding.id == inv.wedding_id, Wedding.is_archived == False).first()

    # Fallback / Demo Access: Map valid test/planner/client accounts to primary active wedding
    if not wedding:
        wedding = db.query(Wedding).filter(Wedding.is_archived == False).order_by(Wedding.id.asc()).first()
        if wedding:
            wedding.customer_user_id = user.id
            db.commit()
            db.refresh(wedding)

    if not wedding:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active wedding record found associated with this account. Please contact your wedding planner.",
        )'''

new_cust_block = '''    norm_email = payload.email.strip().lower()
    user = db.query(User).filter(User.email.ilike(norm_email)).first()
    if not user:
        if norm_email in ("charanraghu38@gmail.com", "priya.mehra@gmail.com"):
            user = User(
                id=f"u_cust_{uuid.uuid4().hex[:8]}",
                auth_user_id=f"sub_cust_{uuid.uuid4().hex[:12]}",
                name=norm_email.split('@')[0].capitalize(),
                email=norm_email,
                role="customer",
                avatar_initials=norm_email[0].upper(),
                created_at=datetime.datetime.utcnow(),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="We couldn't find an account associated with this email. Check your details or contact your wedding planner.",
            )
    elif user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="We couldn't find an account associated with this email. Check your details or contact your wedding planner.",
        )

    # Verify customer is linked to an active wedding
    wedding = (
        db.query(Wedding)
        .filter(
            (Wedding.customer_user_id == user.id) | (Wedding.client_email.ilike(norm_email)),
            Wedding.is_archived == False,
        )
        .first()
    )
    if not wedding:
        inv = (
            db.query(CustomerInvitation)
            .filter(
                (CustomerInvitation.claimed_by_user_id == user.id) |
                (CustomerInvitation.client_email.ilike(norm_email))
            )
            .first()
        )
        if inv:
            wedding = db.query(Wedding).filter(Wedding.id == inv.wedding_id, Wedding.is_archived == False).first()

    # Fallback / Demo Access for test/demo accounts: map to primary active wedding
    if not wedding and (norm_email in ("charanraghu38@gmail.com", "priya.mehra@gmail.com") or (user.auth_user_id and user.auth_user_id.startswith("sub_cust_"))):
        wedding = db.query(Wedding).filter(Wedding.is_archived == False).order_by(Wedding.id.asc()).first()
        if wedding:
            wedding.customer_user_id = user.id
            db.commit()
            db.refresh(wedding)

    if not wedding:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active wedding record found associated with this account. Please contact your wedding planner.",
        )'''

cust_lf = old_cust_block.replace("\r\n", "\n")
cust_crlf = old_cust_block.replace("\r\n", "\n").replace("\n", "\r\n")

if cust_crlf in cust:
    cust = cust.replace(cust_crlf, new_cust_block.replace("\n", "\r\n"), 1)
    print("Found CRLF in customer.py")
elif cust_lf in cust:
    cust = cust.replace(cust_lf, new_cust_block, 1)
    print("Found LF in customer.py")
else:
    raise ValueError("old_cust_block not found in customer.py")

assert "—" not in cust, "Em dash in customer.py"
with open("backend/api/customer.py", "w", encoding="utf-8") as f:
    f.write(cust)
print("Updated customer.py successfully!")

# 2. Update auth.py
with open("backend/core/auth.py", "r", encoding="utf-8") as f:
    auth_code = f.read()

old_auth_block = '''    # Fallback / Demo Access for test/demo accounts: map to primary active wedding
    if not linked_wedding:
        linked_wedding = query.order_by(Wedding.id.asc()).first()'''

new_auth_block = '''    # Fallback / Demo Access for test/demo accounts: map to primary active wedding
    if not linked_wedding and customer.email and customer.email.lower() in ("charanraghu38@gmail.com", "priya.mehra@gmail.com"):
        linked_wedding = query.order_by(Wedding.id.asc()).first()'''

auth_lf = old_auth_block.replace("\r\n", "\n")
auth_crlf = old_auth_block.replace("\r\n", "\n").replace("\n", "\r\n")

if auth_crlf in auth_code:
    auth_code = auth_code.replace(auth_crlf, new_auth_block.replace("\n", "\r\n"), 1)
    print("Found CRLF in auth.py")
elif auth_lf in auth_code:
    auth_code = auth_code.replace(auth_lf, new_auth_block, 1)
    print("Found LF in auth.py")
else:
    raise ValueError("old_auth_block not found in auth.py")

assert "—" not in auth_code, "Em dash in auth.py"
with open("backend/core/auth.py", "w", encoding="utf-8") as f:
    f.write(auth_code)
print("Updated auth.py successfully!")

