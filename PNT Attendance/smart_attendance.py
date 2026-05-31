import cv2
import sqlite3
from datetime import datetime

# Load model
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Student names
student_names = {
    1: "Haritha",
    2: "Jyoshna",
    3: "KSL",
    4: "Anusha",
    5: "Poojitha",
    6: "Naga Lakshmi",
    7: "Parvati",
    8: "Revati",
    9: "Yamini",
    10: "Supriya",
    11: "Nitya"
}

marked = set()

# Save attendance to DB
def mark_attendance(name):
    if name in marked:
        return

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    cursor.execute("INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)",
                   (name, date, time))

    conn.commit()
    conn.close()

    marked.add(name)
    print(f"✅ {name} marked present")

# Start camera
cam = cv2.VideoCapture(0)

print("🎥 Smart Attendance Started (Press Q to exit)")

while True:
    ret, frame = cam.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (200, 200))

        label, confidence = recognizer.predict(face)

        if confidence < 110:
            name = student_names.get(label, "Unknown")
            color = (0, 255, 0)

            mark_attendance(name)
        else:
            name = "Unknown"
            color = (0, 0, 255)

        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, name, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    cv2.imshow("Smart Attendance System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()