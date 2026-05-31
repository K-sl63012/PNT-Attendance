import streamlit as st
import cv2
import pandas as pd
from datetime import datetime

st.title("🎓 Smart Attendance System")

# Load model
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

student_names = {
    1: "Haritha",
    2: "Jyoshna",
    3: "Shiva Lakshmi",
    4: "Anusha",
    5: "Poojitha",
    6: "Naga Lakshmi",
    7: "Parvati",
    8: "Revati",
    9: "Yamini",
    10: "Supriya",
    11: "Nitya"
}

attendance = {}

run = st.checkbox("Start Camera")

FRAME_WINDOW = st.image([])

cap = cv2.VideoCapture(0)

while run:
    ret, frame = cap.read()
    if not ret:
        st.write("Camera error")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    for (x, y, w, h) in faces:
        face_img = gray[y:y+h, x:x+w]
        face_img = cv2.resize(face_img, (100, 100))

        label, confidence = recognizer.predict(face_img)

        if confidence < 120:
            name = student_names.get(label, "Unknown")
            attendance[name] = "Present"
            color = (0,255,0)
        else:
            name = "Unknown"
            color = (0,0,255)

        cv2.rectangle(frame, (x,y), (x+w,y+h), color, 2)
        cv2.putText(frame, name, (x,y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    FRAME_WINDOW.image(frame, channels="BGR")

cap.release()

# Save attendance
if st.button("Save Attendance"):
    date_today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M:%S")

    data = []
    for student in student_names.values():
        status = attendance.get(student, "Absent")
        data.append([student, status, date_today, time_now])

    df = pd.DataFrame(data, columns=["Name", "Status", "Date", "Time"])
    file_name = f"attendance_{date_today}.xlsx"
    df.to_excel(file_name, index=False)

    st.success(f"Saved as {file_name}")