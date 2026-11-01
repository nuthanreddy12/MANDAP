with open("backend/services/financial_reconciliation.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update desc and inv_line_total extraction
old_desc = 'desc = inv_item.get("original_description") or inv_item.get("description", "")'
new_desc = 'desc = inv_item.get("original_description") or inv_item.get("description") or inv_item.get("desc") or ""'
assert old_desc in content
content = content.replace(old_desc, new_desc, 1)

old_inv_rate = 'inv_rate = to_decimal(inv_item.get("unit_price"))'
new_inv_rate = 'inv_rate = to_decimal(inv_item.get("unit_price") or inv_item.get("rate") or inv_item.get("invoiced_amount", 0))'
assert old_inv_rate in content
content = content.replace(old_inv_rate, new_inv_rate, 1)

old_inv_total = 'inv_line_total = to_decimal(inv_item.get("line_total", inv_qty * inv_rate))'
new_inv_total = 'inv_line_total = to_decimal(inv_item.get("line_total") or inv_item.get("invoiced_amount") or (inv_qty * inv_rate))'
assert old_inv_total in content
content = content.replace(old_inv_total, new_inv_total, 1)

old_q_desc = 'q_desc = q_item.get("original_description") or q_item.get("description", "")'
new_q_desc = 'q_desc = q_item.get("original_description") or q_item.get("description") or q_item.get("desc") or ""'
assert old_q_desc in content
content = content.replace(old_q_desc, new_q_desc, 1)

old_exp_total = 'expected_total = to_decimal(best_match.get("line_total", q_qty * q_rate))'
new_exp_total = 'expected_total = to_decimal(best_match.get("line_total") or best_match.get("agreed_amount") or (q_qty * q_rate))'
assert old_exp_total in content
content = content.replace(old_exp_total, new_exp_total, 1)

assert "—" not in content, "Em dash detected in financial_reconciliation.py"

with open("backend/services/financial_reconciliation.py", "w", encoding="utf-8") as f:
    f.write(content)

print("backend/services/financial_reconciliation.py updated successfully.")

