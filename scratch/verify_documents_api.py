import requests

# 1. Login as planner
login_res = requests.post("http://127.0.0.1:8001/api/v1/auth/login", json={"email": "nisha@theroyalknot.in", "password": "Password123!"})
assert login_res.status_code == 200, f"Login failed: {login_res.text}"
token = login_res.json()["token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Get documents
docs_res = requests.get("http://127.0.0.1:8001/api/v1/weddings/w1/documents", headers=headers)
assert docs_res.status_code == 200, f"Get documents failed: {docs_res.text}"
docs = docs_res.json()

print(f"Total documents returned by backend: {len(docs)}")
filenames = [d["filename"] for d in docs]
unique_filenames = set(filenames)

print(f"Unique filenames: {len(unique_filenames)}")
assert len(filenames) == len(unique_filenames), f"Duplicates found! {filenames}"

print("\nAll documents:")
for d in docs:
    print(f" - [{d['id']}] {d['title']} ({d['filename']}) - {d['status']}")

print("\nVerification successful: 0 duplicates in backend response!")

