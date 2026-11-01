from backend.core.auth import create_access_token
import urllib.request, json

token = create_access_token({'sub': 'u2', 'email': 'nisha@theroyalknot.in', 'email_verified': True, 'role': 'planner', 'type': 'staff'})
req = urllib.request.Request('http://127.0.0.1:8001/api/v1/enquiries', headers={'Authorization': f'Bearer {token}'})

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    print('Total enquiries count:', len(data))
    for d in data:
        print(f"ID: {d.get('id')} | Couple: {d.get('couple_names')} | Email: {d.get('email')} | Status: {d.get('status')}")
