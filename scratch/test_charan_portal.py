import urllib.request, json

# 1. Login
url = 'http://127.0.0.1:8001/api/v1/customer/auth/login'
headers = {'Content-Type': 'application/json'}
payload = json.dumps({'email': 'charanraghu38@gmail.com', 'password': 'testpassword'}).encode('utf-8')

req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    token = data["token"]

# 2. Access portal wedding endpoint
portal_url = 'http://127.0.0.1:8001/api/v1/customer/wedding'
portal_req = urllib.request.Request(portal_url, headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(portal_req) as resp:
    w_data = json.loads(resp.read().decode('utf-8'))
    print("Success accessing customer wedding endpoint! HTTP Status:", resp.status)
    print("Wedding ID:", w_data.get("wedding_id"))
    print("Wedding couple:", w_data.get("couple_names"))
    print("Wedding venue:", w_data.get("venue"))
