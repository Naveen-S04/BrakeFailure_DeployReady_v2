import requests

url = "http://localhost:5000/predict"
data = {
    "brake_pressure": 135,
    "brake_temp": 98,
    "vehicle_speed": 70,
    "pad_wear_level": 92
}

response = requests.post(url, json=data)
print("✅ Prediction response:", response.json())
