import os
import cv2
import numpy as np
from PIL import Image

dataset_path = "dataset"

recognizer = cv2.face.LBPHFaceRecognizer_create()

faces = []
labels = []

print(" Reading dataset...")

for student_folder in os.listdir(dataset_path):

    folder_path = os.path.join(dataset_path, student_folder)

    if not os.path.isdir(folder_path):
        continue

    label = int(student_folder)

    count = 0

    for image_name in os.listdir(folder_path):

        
        if not image_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        if count >= 50:
            break

        image_path = os.path.join(folder_path, image_name)

        try:
            img = Image.open(image_path).convert('L')
            img = img.resize((100, 100))

            img_np = np.array(img, 'uint8')

            faces.append(img_np)
            labels.append(label)

            count += 1

        except:
            print("Error loading:", image_path)

print("Total images:", len(faces))

if len(faces) == 0:
    print(" No dataset found!")
    exit()

print(" Training model...")

recognizer.train(faces, np.array(labels))
recognizer.save("trainer.yml")

print(" Model trained successfully!")