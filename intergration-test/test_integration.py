import requests
import json

def test_integration():
    # Define the sample input data
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

    # Send a POST request to the deployed API
    response = requests.post("http://localhost:5000/predict", json=data)

    # Check if the request was successful
    assert response.status_code == 200

    # Get the prediction from the response
    prediction = response.json()[0]  # Extract the first value from the list
    print(prediction)

    # Assert the predicted price matches the expected value
    expected_prediction = 14259.82
    assert round(prediction, 2) == expected_prediction, f"Expected {expected_prediction}, got {prediction}"

    print("Integration test passed!")

if __name__ == '__main__':
    test_integration()
