import urllib.request, json
from backend.core.auth import create_access_token

token = create_access_token({'sub': 'u2', 'email': 'nisha@theroyalknot.in', 'email_verified': True, 'role': 'planner', 'type': 'staff'})

url = 'http://127.0.0.1:8001/api/v1/weddings'
headers = {
    'Authorization': f'Bearer {token}',
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Total weddings from API:", len(data))
        for w in data:
            print(" -", w.get("id"), w.get("couple_names"), w.get("venue"), w.get("dates"))
except Exception as e:
    print("Error:", e)

