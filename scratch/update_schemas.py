with open('backend/schemas/quote.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = 'selected_by: Optional[str] = "Aarav Mehta" '
replacement = 'selected_by: Optional[str] = "Aarav Mehta"\n    reassign: Optional[bool] = False'

if target not in content:
    target = 'selected_by: Optional[str] = "Aarav Mehta"'
    replacement = 'selected_by: Optional[str] = "Aarav Mehta"\n    reassign: Optional[bool] = False'

assert target in content, "Target not found"
content = content.replace(target, replacement, 1)

with open('backend/schemas/quote.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Schema updated successfully.")

