import requests
import json
import base64
from io import BytesIO
from PIL import Image

# API Endpoint
API_URL = "http://127.0.0.1:8000/process_quiz"

# Load a real image from the file system
image_path = "./empty_room.jpg"  # Change this to your image path
with open(image_path, "rb") as img_file:
    image_base64 = base64.b64encode(img_file.read()).decode("utf-8")

# Define the request payload
test_payload = {
    "quizAnswer": [
        {
            "questionID": "q1",
            "selectedOption": [
                {
                    "option": "A",
                    "optionContent": "Modern"
                }
            ]
        }
    ],
    "emptyRoom": {
        "image": image_base64,  # Send image as Base64 string
        "length": 5.0,
        "width": 4.0
    }
}

# Send the request
headers = {"Content-Type": "application/json"}
response = requests.post(API_URL, json=test_payload, headers=headers)

# Handle response
if response.status_code == 200:
    result = response.json()
    
    # Process decorated room image
    decorated_image_base64 = result["decoratedRoom"]["image"]
    if decorated_image_base64:
        decorated_image_data = base64.b64decode(decorated_image_base64)
        decorated_image = Image.open(BytesIO(decorated_image_data))
        decorated_image.show()  # Show the decorated room image

    # Process furniture images
    print("Furniture List:")
    for item in result["furnitureList"]:
        print(f"Name: {item['name']}")

        if item["image"]:
            furniture_image_data = base64.b64decode(item["image"])
            furniture_image = Image.open(BytesIO(furniture_image_data))
            furniture_image.show()  # Show each furniture image
else:
    print("Error:", response.status_code, response.text)
