
import logging
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials
import io
from PIL import Image

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Azure Custom Vision setup
ENDPOINT = "https://p2ic-prediction.cognitiveservices.azure.com/"
prediction_key = "64bfcfb8949d484fae93402fa55e1425"
project_id = "c450da0e-a657-4c10-a1a4-f8ed35e8d40a"
publish_name = "DiseaseClassification"

# Create CustomVisionPredictionClient
credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
predictor = CustomVisionPredictionClient(ENDPOINT, credentials)

# Function to make predictions
def predict_image(image_path):
    with open(image_path, "rb") as image_data:
        results = predictor.classify_image(project_id, publish_name, image_data.read())
    
    # Output the results
    logging.info(f"Predictions for image: {image_path}")
    for prediction in results.predictions:
        logging.info(f"Tag: {prediction.tag_name}, Probability: {prediction.probability:.2f}")

# Example usage
image_path = r"ImageClassification\BrainTumorAndChestX_RayDatasets\Training\covid19\COVID19(4).jpg"  # Replace with your image path
predict_image(image_path)