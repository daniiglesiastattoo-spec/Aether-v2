import urllib.request
import urllib.error

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=FAKE_KEY"
req = urllib.request.Request(url, method="POST")
req.add_header("Content-Type", "application/json")
try:
    urllib.request.urlopen(req, data=b"{}")
except urllib.error.HTTPError as e:
    print(f"gemini-1.5-flash: {e.code}")

url2 = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=FAKE_KEY"
req2 = urllib.request.Request(url2, method="POST")
req2.add_header("Content-Type", "application/json")
try:
    urllib.request.urlopen(req2, data=b"{}")
except urllib.error.HTTPError as e:
    print(f"gemini-1.5-pro: {e.code}")
