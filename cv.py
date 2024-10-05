
import logging
import os
from azure.storage.blob import BlobServiceClient
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from msrest.authentication import ApiKeyCredentials

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Azure Storage setup
connection_string = "DefaultEndpointsProtocol=https;AccountName=p2rev;AccountKey=cDDE2LCX6kyllJL6hfPV2ki8Y8Wo4/8cM1+S6CXaQulCnKnWYqFJ2hXqQ7V28xB086aYedTiy941+AStRQUjOw==;EndpointSuffix=core.windows.net"  
container_name = "p2s"  

# Create BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Check if container exists
try:
    container_client = blob_service_client.get_container_client(container_name)
    container_properties = container_client.get_container_properties()
    print(f"Container '{container_name}' exists and is accessible.")
except Exception as e:
    print(f"Error accessing container: {e}")
    exit(1)

# Azure Custom Vision setup
ENDPOINT = "https://p2ic.cognitiveservices.azure.com/"  
training_key = "110645cac4364943bf00012cf61a180a"  
project_id = "c450da0e-a657-4c10-a1a4-f8ed35e8d40a"  

# Create CustomVisionTrainingClient
credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

# Function to create or retrieve the tag
def get_or_create_tag(trainer, project_id, tag_name):
    tags = trainer.get_tags(project_id)
    for tag in tags:
        if tag.name == tag_name:
            return tag
    return trainer.create_tag(project_id, tag_name)

# Upload images from Azure Blob Storage to Custom Vision
base_folder = "BrainTumorAndCovid19/Training/"

# List blobs in the base folder
blob_list = container_client.list_blobs(name_starts_with=base_folder)

# Dictionary to hold tags
tags_dict = {}

# Iterate over the blobs
for blob in blob_list:
    logging.info(f"Found blob: {blob.name}")
    if blob.name.endswith(('.jpg', '.jpeg', '.png')):
        # Extract the class label from the blob's path (subfolder name)
        class_label = os.path.basename(os.path.dirname(blob.name))
        
        logging.info(f"Processing image: {blob.name} with class label: '{class_label}'")

        # Create or retrieve the tag based on class_label
        if class_label not in tags_dict:
            tag = get_or_create_tag(trainer, project_id, class_label)
            tags_dict[class_label] = tag
            logging.info(f"Created or retrieved tag: '{class_label}' with ID: {tag.id}")

        # Download the image
        try:
            blob_client = container_client.get_blob_client(blob.name)
            download_stream = blob_client.download_blob()
            image_data = download_stream.readall()

            # Upload the image to Custom Vision with the appropriate tag
            logging.info(f"Uploading {blob.name} with tag '{class_label}'")
            trainer.create_images_from_data(project_id, image_data, tag_ids=[tags_dict[class_label].id])
            logging.info(f"Successfully uploaded {blob.name}.")
        except Exception as e:
            logging.error(f"Failed to upload {blob.name}: {e}")
    else:
        logging.info(f"Skipping non-image file: {blob.name}")

print("Image upload complete.")
