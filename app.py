import os
from datetime import datetime
from typing import Optional

import cv2
import face_recognition
import numpy as np
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Face Recognition API",
    description="A simple API for face recognition using FastAPI and face_recognition library",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


KNOWN_FACES_DIR = "known_faces"
os.makedirs(KNOWN_FACES_DIR, exist_ok=True)


known_face_encodings = []
known_face_names = []



class FaceRegister(BaseModel):
    name: str
    description: Optional[str] = None



def load_known_faces():
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []

    if not os.path.exists(KNOWN_FACES_DIR):
        return

    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            name = os.path.splitext(filename)[0]
            image_path = os.path.join(KNOWN_FACES_DIR, filename)

            try:
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)

                if len(encodings) > 0:
                    known_face_encodings.append(encodings[0])
                    known_face_names.append(name)
                    print(f"Loaded known face: {name}")
                else:
                    print(f"No face found in {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")


@app.on_event("startup")
async def startup_event():
    load_known_faces()
    print(f"Loaded {len(known_face_names)} known faces")



async def process_image(file: UploadFile) -> np.ndarray:
    contents = await file.read()


    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)


    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return rgb_img


@app.get("/")
async def root():
    return {"message": "Face Recognition API is running", "known_faces": len(known_face_names)}


@app.post("/recognize")
async def recognize_face(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:

        image = await process_image(file)


        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        results = []


        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):

            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            confidence = 0.0


            if known_face_encodings:
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    confidence = 1 - face_distances[best_match_index]
                    name = known_face_names[best_match_index]

            results.append({
                "name": name,
                "confidence": float(confidence),
                "location": {
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "left": left
                }
            })

        return {"faces_found": len(results), "results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


@app.post("/register")
async def register_face(name: str, file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:

        image = await process_image(file)


        face_locations = face_recognition.face_locations(image)

        if not face_locations:
            raise HTTPException(status_code=400, detail="No face detected in the image")

        if len(face_locations) > 1:
            raise HTTPException(status_code=400,
                                detail="Multiple faces detected in the image. Please upload an image with just one face.")


        face_encoding = face_recognition.face_encodings(image, face_locations)[0]


        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.jpg"
        filepath = os.path.join(KNOWN_FACES_DIR, filename)


        bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(filepath, bgr_image)


        known_face_encodings.append(face_encoding)
        known_face_names.append(name)

        return {"message": f"Face registered successfully for {name}", "file": filename}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering face: {str(e)}")


@app.get("/known_faces")
async def list_known_faces():
    return {"known_faces": known_face_names}


@app.delete("/known_faces/{name}")
async def delete_known_face(name: str):
    global known_face_encodings, known_face_names

    try:
        indices = [i for i, n in enumerate(known_face_names) if n == name]

        if not indices:
            raise HTTPException(status_code=404, detail=f"No face found with name {name}")


        for index in sorted(indices, reverse=True):
            del known_face_encodings[index]
            del known_face_names[index]


        for filename in os.listdir(KNOWN_FACES_DIR):
            if filename.startswith(f"{name}_") and filename.endswith(('.jpg', '.jpeg', '.png')):
                os.remove(os.path.join(KNOWN_FACES_DIR, filename))

        return {"message": f"Successfully removed all faces for {name}"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting face: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
