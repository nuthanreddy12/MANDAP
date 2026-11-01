import urllib.request, json
from backend.core.auth import create_access_token

token = create_access_token({'sub': 'u2', 'email': 'nisha@theroyalknot.in', 'email_verified': True, 'role': 'planner', 'type': 'staff'})

url = 'http://127.0.0.1:8001/api/v1/weddings/w1/timeline/incidents/inc_bf5358f2/approve'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

req = urllib.request.Request(url, data=b'{}', headers=headers, method='POST')

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Success! HTTP Status:", resp.status)
        print("Response:", data)
except Exception as e:
    print("Error:", e)
    if hasattr(e, 'read'):
        print(e.read().decode('utf-8'))

