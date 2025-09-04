from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import face_recognition
import numpy as np
import cv2
import pickle
import os
from PIL import Image, ImageDraw, ImageFont
import io
import base64

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Store known faces
KNOWN_FACES_FILE = "known_faces.pkl"
if os.path.exists(KNOWN_FACES_FILE):
    with open(KNOWN_FACES_FILE, "rb") as f:
        known_faces = pickle.load(f)
else:
    known_faces = {}

@app.get("/", response_class=HTMLResponse)
def serve_index():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/add_face/")
def add_face(name: str = Form(...), file: UploadFile = File(...)):
    image = face_recognition.load_image_file(file.file)
    encodings = face_recognition.face_encodings(image)
    if encodings:
        known_faces[name] = encodings[0]
        with open(KNOWN_FACES_FILE, "wb") as f:
            pickle.dump(known_faces, f)
        return {"message": "Face added successfully"}
    return {"message": "No face detected"}

@app.post("/detect_faces/")
def detect_faces(file: UploadFile = File(...)):
    image = face_recognition.load_image_file(file.file)
    face_locations = face_recognition.face_locations(image)
    encodings = face_recognition.face_encodings(image, face_locations)
    detected_faces = []
    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)
    font = ImageFont.load_default()
    
    for encoding, location in zip(encodings, face_locations):
        matches = face_recognition.compare_faces(list(known_faces.values()), encoding)
        name = "Unknown"
        if True in matches:
            name = list(known_faces.keys())[matches.index(True)]
        detected_faces.append(name)

        # Draw bounding box
        top, right, bottom, left = location
        draw.rectangle([(left, top), (right, bottom)], outline="red", width=3)
        draw.text((left + int((right - left)*0.5), top - 10), name, fill="red", font=font)
    
    # Save processed image to bytes
    output = io.BytesIO()
    pil_image.save(output, format="JPEG")
    output.seek(0)
    encoded_img = base64.b64encode(output.read()).decode()
    
    return HTMLResponse(content=f"<img src='data:image/jpeg;base64,{encoded_img}'/>", status_code=200)
