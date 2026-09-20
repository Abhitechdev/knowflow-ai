import time
import httpx

docs = [
    ("HR-POL-108-Leave-and-Attendance-Policy.docx", "HR-POL-108: Leave and Attendance Policy", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ("IT-SEC-015-Password-and-Access-Control-Policy.txt", "IT-SEC-015: Password & Access Control Policy", "text/plain"),
    ("CLIN-SOP-009-Cold-Chain-Storage.md", "CLIN-SOP-009: Refrigerated Storage & Cold Chain", "text/markdown"),
]

for fn, title, mime in docs:
    with open(f"demo_documents/{fn}", "rb") as f:
        r = httpx.post(
            "http://127.0.0.1:8000/api/documents/upload",
            data={"title": title},
            files={"file": (fn, f, mime)},
            timeout=60.0,
        )
        print("Uploaded:", fn, r.status_code, r.json()["document"]["id"])

print("Waiting 12 seconds for background pipeline to complete...")
time.sleep(12)

r = httpx.get("http://127.0.0.1:8000/api/documents", timeout=30.0)
items = r.json().get("items", [])
print(f"Total documents in database: {len(items)}")
for item in items:
    print(f"-> {item['title']} | Status: {item['status']} | Chunks: {item['total_chunks']} | Pages: {item['page_count']} | Type: {item['file_type']}")
