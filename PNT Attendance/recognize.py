import cv2
import pandas as pd
from datetime import datetime
from collections import Counter
import smtplib
from email.message import EmailMessage

# ---------------- LOAD MODEL ----------------
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# ---------------- STUDENT DATA ----------------
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

# ---------------- PERIOD SCHEDULE ----------------
periods = {
    "1st Period": {"start": 9, "end": 10, "faculty": "Sharmila"},
    "2nd Period": {"start": 10, "end": 11, "faculty": "Riyaz"},
    "3rd Period": {"start": 11, "end": 12, "faculty": "BhuLakshmi"},
    "4th Period": {"start": 12, "end": 13, "faculty": "Bhaskar"},
    "5th Period": {"start": 13, "end": 14, "faculty": "Samuel"},
    "6th Period": {"start": 14, "end": 15, "faculty": "Lavanya"},
    "7th Period": {"start": 15, "end": 16, "faculty": "Sravanthi"},
}

def get_current_period():
    now = datetime.now()
    hour = now.hour
    for pname, info in periods.items():
        if info["start"] <= hour < info["end"]:
            return pname, info["faculty"]
    return None, None

# ---------------- EMAIL FUNCTION ----------------
def send_email(file_path, period_name):
    sender_email = "23x51a0591@srecnandyal.edu.in"
    app_password = "otqi mdtp zsav yfgr"
    receiver_email = "23x51a0591@srecnandyal.edu.in"

    msg = EmailMessage()
    msg['Subject'] = f"Attendance - {period_name}"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content("Attendance attached.")

    with open(file_path, 'rb') as f:
        msg.add_attachment(
            f.read(),
            maintype='application',
            subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=file_path
        )

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
        print(" Email sent successfully!")
    except Exception as e:
        print("Email failed:", e)

# ---------------- CAMERA ----------------
cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print(" Camera not opening")
    exit()

print(" Camera started... Press Q or ESC to exit")

predictions = []
display_names = {}

try:
    while True:
        ret, frame = cam.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.3, minNeighbors=5, minSize=(80, 80)
        )

        for i, (x, y, w, h) in enumerate(faces):
            margin = 20
            face_img = gray[
                max(0, y-margin):y+h+margin,
                max(0, x-margin):x+w+margin
            ]

            face_img = cv2.resize(face_img, (200, 200))
            face_img = cv2.equalizeHist(face_img)

            label, confidence = recognizer.predict(face_img)

            # Collect predictions
            if confidence < 135:
                predictions.append(label)

            # Stabilize prediction
            if len(predictions) > 10:
                most_common = Counter(predictions).most_common(1)[0][0]
                display_name = student_names.get(most_common, "Unknown")
                display_names[i] = display_name
                attendance[display_name] = "Present"
                predictions.clear()
            else:
                display_name = display_names.get(i, "Detecting...")

            color = (0, 255, 0) if display_name != "Unknown" else (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, display_name, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("Attendance System", frame)

        
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q') or key == 27:
            print(" Exiting...")
            break

finally:
    cam.release()
    cv2.destroyAllWindows()

    # ---------------- SAVE ATTENDANCE ----------------
    date_today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M:%S")

    period_name, faculty_name = get_current_period()

    
    if period_name is None:
        period_name = "Out of Class"
        faculty_name = "None"

    data = []
    for student in student_names.values():
        status = attendance.get(student, "Absent")
        data.append([student, faculty_name, period_name, status, date_today, time_now])

    file_name = f"attendance_{date_today}.xlsx"

    df = pd.DataFrame(
        data,
        columns=["Name", "Faculty", "Period", "Status", "Date", "Time"]
    )

    df.to_excel(file_name, index=False)

    print(f" Attendance saved: {file_name}")

    # ---------------- SEND EMAIL ----------------
    send_email(file_name, period_name)