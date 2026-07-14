import httpx
import json

def test_openapi():
    r = httpx.get("http://localhost:8000/openapi.json")
    print("Status code:", r.status_code)
    try:
        data = r.json()
        print("Keys:", list(data.keys()))
        print("Paths count:", len(data.get("paths", {})))
        print("OpenAPI version:", data.get("openapi"))
    except Exception as e:
        print("Failed to parse JSON:", e)

if __name__ == "__main__":
    test_openapi()
