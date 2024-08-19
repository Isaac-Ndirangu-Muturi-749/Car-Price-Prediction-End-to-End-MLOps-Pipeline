# unit_tests/model_test.py

import unittest
from unittest.mock import Mock, patch
import pandas as pd
from model import get_model_location, ModelService

class TestCarPriceModel(unittest.TestCase):
    @patch('os.getenv')
    def test_get_model_location(self, mock_getenv):
        # Mock environment variables
        mock_getenv.side_effect = lambda key, default=None: 'mlflow-artifacts-capstone-mlops' if key == 'MODEL_BUCKET' else default
        run_id = '9c4533e2d8c049fdae991d4ba055ff38'
        expected_location = 's3://mlflow-artifacts-capstone-mlops/5/9c4533e2d8c049fdae991d4ba055ff38/artifacts/xgboost_model/'
        self.assertEqual(get_model_location(run_id), expected_location)

    def test_prepare_features(self):
        model_service = ModelService(None)
        car_data = {
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
        expected_features = pd.DataFrame([car_data])
        actual_features = model_service.prepare_features(car_data)
        pd.testing.assert_frame_equal(actual_features, expected_features)

    def test_predict(self):
        mock_model = Mock()
        mock_model.predict.return_value = [14259.82]
        model_service = ModelService(mock_model)
        features = pd.DataFrame([{
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
        }])
        actual_prediction = model_service.predict(features)
        expected_prediction = 14259.82
        self.assertEqual(actual_prediction, expected_prediction)

    def test_predict_car_price(self):
        mock_model = Mock()
        mock_model.predict.return_value = [14259.82]
        model_service = ModelService(mock_model, model_version="v1")
        car_data = {
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
        result = model_service.predict_car_price(car_data)
        expected_output = {
            'model': 'car_price_prediction_model',
            'version': 'v1',
            'prediction': {'car_price': 14259.82}
        }
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()
