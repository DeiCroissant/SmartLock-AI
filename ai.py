import cv2
import numpy as np
import requests
import os
import time
from threading import Thread
from queue import Queue

# --- CẤU HÌNH IP (Hãy kiểm tra IP hiện trên Thonny) ---
URL_CAPTURE = "http://192.168.4.1/capture"
URL_THONNY = "http://192.168.4.2" # Thay bằng IP từ LCD của Thonny

# Độ nhạy nhận diện (Threshold) - giảm để nhạy hơn
THRESHOLD = 60

# Tối ưu hóa Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

if os.path.exists('trainer.yml'):
    recognizer.read('trainer.yml')
    print("[INFO] Hệ thống AI đã sẵn sàng.")
else:
    print("[ERROR] Cần chạy file train.py để tạo trainer.yml trước!")
    exit()

last_cmd_time = 0
frame_queue = Queue(maxsize=1)
running = True

# Thread fetch frame từ camera để không làm block chính thread
def fetch_frames():
    while running:
        try:
            resp = requests.get(URL_CAPTURE, timeout=0.5)
            img_arr = np.array(bytearray(resp.content), dtype=np.uint8)
            frame = cv2.imdecode(img_arr, -1)
            
            if frame is not None:
                # Resize để xử lý nhanh hơn
                frame = cv2.resize(frame, (640, 480))
                if not frame_queue.empty():
                    try:
                        frame_queue.get_nowait()
                    except:
                        pass
                frame_queue.put(frame)
        except requests.exceptions.RequestException:
            pass
        except Exception as e:
            print(f"[ERROR] Fetch frame: {e}")
        time.sleep(0.01)

# Khởi động thread fetch
fetch_thread = Thread(target=fetch_frames, daemon=True)
fetch_thread.start()

# Thread gửi cmd để không làm block nhận diện
cmd_queue = Queue()
def send_commands():
    global last_cmd_time
    while running:
        try:
            cmd = cmd_queue.get(timeout=0.1)
            if time.time() - last_cmd_time > 5:
                try:
                    requests.get(URL_THONNY + cmd, timeout=0.3)
                    last_cmd_time = time.time()
                except requests.exceptions.Timeout:
                    pass
                except Exception as e:
                    print(f"[ERROR] Send cmd: {e}")
        except:
            pass

cmd_thread = Thread(target=send_commands, daemon=True)
cmd_thread.start()

frame_count = 0
skip_frames = 2  # Skip 2 frame để xử lý nhanh hơn

while True:
    try:
        if frame_queue.empty():
            time.sleep(0.01)
            continue
            
        frame = frame_queue.get()
        frame_count += 1
        
        # Skip frame để tăng tốc độ nhưng vẫn detection smooth
        if frame_count % (skip_frames + 1) != 0:
            cv2.imshow("AI SECURITY SYSTEM - VLU", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Cải thiện contrast để nhận diện tốt hơn
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        
        # Cải thiện hệ số phát hiện - scaleFactor nhỏ hơn = nhạy hơn nhưng chậm hơn
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=4, 
                                              minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

        for (x, y, w, h) in faces:
            # Cắt vùng an toàn hơn
            roi_gray = gray[max(0, y):min(gray.shape[0], y+h), max(0, x):min(gray.shape[1], x+w)]
            
            if roi_gray.size == 0:
                continue
                
            id, confidence = recognizer.predict(roi_gray)
            
            print(f"ID: {id} - Sai lech: {round(confidence, 2)}")

            if confidence < THRESHOLD:
                label, color, cmd = "CHU NHA", (0, 255, 0), "/open"
            else:
                label, color, cmd = "NGUOI LA", (0, 0, 255), "/alert"

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, f"{label} {round(100-confidence)}%", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Queue command thay vì gửi trực tiếp
            cmd_queue.put(cmd)

        cv2.imshow("AI SECURITY SYSTEM - VLU", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    except Exception as e:
        print(f"[ERROR] Main loop: {e}")
        time.sleep(0.01)
        continue

running = False
cv2.destroyAllWindows()
print("[INFO] Hệ thống dừng lại.")