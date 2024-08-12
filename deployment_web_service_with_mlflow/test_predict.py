import requests
import json

# URL of the deployed web service
url = "http://localhost:5000/predict"

# Example payload with all features required by the model
data = {
    "year": 2020.0,
    "mileage": 15944.0,
    "enginesize": 1.0,
    "tax": 150.0,
    "mpg": 57.7,
    "make_bmw": False,
    "make_cclass": False,
    "make_focus": False,
    "make_ford": True,
    "make_hyundi": False,
    "make_merc": False,
    "make_skoda": False,
    "make_toyota": False,
    "make_vauxhall": False,
    "make_vw": False,
    "transmission_Manual": False,
    "transmission_Semi-Auto": True,
    "fueltype_Hybrid": False,
    "fueltype_Petrol": True
}

# Convert the payload to JSON format
data = json.dumps(data)

# Send POST request to the web service
response = requests.post(url, data=data, headers={"Content-Type": "application/json"})

# Check if the request was successful
if response.status_code != 200:
    print(f"Failed to get prediction, status code: {response.status_code}")
    print(f"Error message: {response.text}")
else:
    prediction = response.json()
    print(f"Predicted Car Price: ${round(prediction[0], 2)}")
