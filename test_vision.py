import urllib.request
import urllib.error
import json

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key=FAKE_KEY"
req = urllib.request.Request(url, method="POST")
req.add_header("Content-Type", "application/json")
data = {
    "contents": [{"parts":[{"inline_data": {"mime_type": "image/jpeg", "data": "base64data"}}]}]
}
try:
    urllib.request.urlopen(req, data=json.dumps(data).encode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"gemini-3.5-flash: {e.code}")

