import urllib.request, json
from backend.core.auth import create_access_token

token = create_access_token({'sub': 'u2', 'email': 'nisha@theroyalknot.in', 'email_verified': True, 'role': 'planner', 'type': 'staff'})

url = 'http://127.0.0.1:8001/api/v1/weddings/w1/timeline/events/te_dj_arrival/delay'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
payload = json.dumps({
    'delay_minutes': 30,
    'reason': 'VIP Baraat convoy delayed in traffic on heritage palace approach'
}).encode('utf-8')

req = urllib.request.Request(url, data=payload, headers=headers, method='POST')

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Success! HTTP Status:", resp.status)
        print("Incident ID:", data.get("incident_id"))
        print("Is Feasible:", data.get("is_feasible"))
        print("Conflicts:", data.get("conflicts"))
        print("Proposed schedule length:", len(data.get("proposed_schedule", [])))
        for item in data.get("proposed_schedule", []):
            print(f"  {item.get('id')}: {item.get('original_start')} -> {item.get('proposed_start')} (offset: +{item.get('delay_offset_minutes')}m, affected: {item.get('is_affected')})")
except Exception as e:
    print("Error:", e)
    if hasattr(e, 'read'):
        print(e.read().decode('utf-8'))

