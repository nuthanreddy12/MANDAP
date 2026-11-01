import urllib.request, json

url = 'http://127.0.0.1:8001/api/v1/customer/auth/login'
headers = {'Content-Type': 'application/json'}
payload = json.dumps({'email': 'charanraghu38@gmail.com', 'password': 'testpassword'}).encode('utf-8')

req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print("Success! HTTP Status:", resp.status)
        print("Customer login response:")
        print(json.dumps(data, indent=2))
except Exception as e:
    print("Error:", e)
    if hasattr(e, 'read'):
        print(e.read().decode('utf-8'))

