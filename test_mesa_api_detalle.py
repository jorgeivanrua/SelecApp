import requests
import json

response = requests.get('http://127.0.0.1:5000/api/ubicacion/mesas/225')
data = response.json()

print("Response completo:")
print(json.dumps(data, indent=2, ensure_ascii=False))
