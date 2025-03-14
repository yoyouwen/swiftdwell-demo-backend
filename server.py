from fastapi import FastAPI, UploadFile, File, Response
from pydantic import BaseModel
from typing import List, Optional
import uuid
from io import BytesIO
from PIL import Image
import numpy as np
import base64
import os
import base64

app = FastAPI()

# Ensure output directory exists
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Data Models
class SelectedOption(BaseModel):
    option: str
    optionContent: str

class QuizAnswerItem(BaseModel):
    questionID: str
    selectedOption: List[SelectedOption]

class EmptyRoom(BaseModel):
    image: Optional[bytes]  # Image as bytes
    length: float
    width: float
    roomStyle: str
    roomID: str

class QuizRequest(BaseModel):
    quizAnswer: List[QuizAnswerItem]
    emptyRoom: EmptyRoom

class FurnitureItem(BaseModel):
    id: str
    name: str
    image: Optional[str]  # Base64-encoded image string
    size: List[float]
    url: str

class DecoratedRoom(BaseModel):
    image: Optional[str]  # Base64-encoded image string
    length: float
    width: float

class QuizResponse(BaseModel):
    decoratedRoom: DecoratedRoom
    furnitureList: List[FurnitureItem]

# Dummy function to process quiz answers and return a furniture list
def generate_furniture_list(room_style: str) -> List[FurnitureItem]:
    furniture_items_livingroom = [
        {"name": "Sofa", "image_path": "product/elegant white and gold Victorian-style armchair.png", "size": [2.0, 1.0], "url": "https://example.com/sofa","price": 100},
        {"name": "Table", "image_path": "product/Greek-style round coffee table with gold accents.png", "size": [1.5, 1.0], "url": "https://example.com/table","price": 200}
    ]

    furniture_items_bedroom = [
        {"name": "Bed", "image_path": "product/Vintage Wooden Bed.png", "size": [2.0, 1.0], "url": "https://example.com/bed","price": 100},
        {"name": "Dresser", "image_path": "product/Antique Wooden Dresser.png", "size": [1.5, 1.0], "url": "https://example.com/dresser","price": 200},
        {"name": "Lamp", "image_path": "product/Decorative Table Lamps.png", "size": [1.5, 1.0], "url": "https://example.com/lamps","price": 200},
    ]

    if room_style == "livingroom":
        furniture_items = furniture_items_livingroom
        furniture_path = "livingroom1_bbaa"
    if room_style == "bedroom":
        furniture_items = furniture_items_bedroom
        furniture_path = "bedroom1_edcb"
    furniture_list = []
    for item in furniture_items:
        image_filename = f"{OUTPUT_DIR}/{furniture_path}/{item['image_path']}"
        
        # Read the saved image and encode it as base64
        if os.path.exists(image_filename):
            with open(image_filename, "rb") as img_file:
                image_base64 = base64.b64encode(img_file.read()).decode("utf-8")
        else:
            image_base64 = None

        furniture_list.append(FurnitureItem(
            id=str(uuid.uuid4()),
            name=item["name"],
            image=image_base64,
            size=item["size"],
            url=item["url"],
            price=item["price"]
        ))
    
    return furniture_list

@app.post("/process_quiz", response_model=QuizResponse)
def process_quiz(data: QuizRequest):
    furniture_list = generate_furniture_list(data.emptyRoom.roomStyle)
    
    # Process image if provided
    if data.emptyRoom.image:
        try:
            # Decode Base64 image
            image_bytes = base64.b64decode(data.emptyRoom.image)
            image_data = BytesIO(image_bytes)
            image = Image.open(image_data)

            # Save processed image locally
            image_filename = f"{OUTPUT_DIR}/decorated_room_{uuid.uuid4().hex}.png"
            image.save(image_filename, format="PNG")

            furniture_path = ""
            if data.emptyRoom.roomStyle == "livingroom":
                furniture_path = "livingroom1_bbaa"
            if data.emptyRoom.roomStyle == "bedroom":
                furniture_path = "bedroom1_edcb"
            output_image_filaname = f"{OUTPUT_DIR}/{furniture_path}/{furniture_path}.png"
            # Read the saved image and encode it as base64
            with open(output_image_filaname, "rb") as img_file:
                decorated_image_base64 = base64.b64encode(img_file.read()).decode("utf-8")
        except Exception as e:
            return {"error": f"Image processing failed: {str(e)}"}
    else:
        decorated_image_base64 = None
    
    decorated_room = DecoratedRoom(
        image=decorated_image_base64,
        length=data.emptyRoom.length,
        width=data.emptyRoom.width
    )
    
    return QuizResponse(
        decoratedRoom=decorated_room,
        furnitureList=furniture_list
    )
