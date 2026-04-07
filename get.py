import cv2
import requests
import numpy as np
import os

# --- CẤU HÌNH ---
URL_CAPTURE = "http://192.168.4.1/capture"
FOLDER_DATA = "data"
USER_NAME = "thay khang"  # Tên hiển thị
USER_ID = 2         # ID để AI phân biệt (Chủ nhà là 1)
TARGET_COUNT = 300  # Số ảnh cần lấy

# Tạo thư mục data nếu chưa có
if not os.path.exists(FOLDER_DATA):
    os.makedirs(FOLDER_DATA)

# Khởi tạo bộ dò mặt
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# CLAHE để tăng độ tương phản
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

count = 0
print("=== HỆ THỐNG QUÉT MẶT CHỦ NHÀ (RÕ NÉT) ===")
print(f"Mục tiêu: Lấy {TARGET_COUNT} ảnh")
print("Lưu ý: Nhìn thẳng, nghiêng nhẹ, ngước lên/xuống, quay trái/phải để AI học kỹ hơn.")
print("(Nhấn 'q' để dừng)\n")

while count < TARGET_COUNT:
    try:
        # Lấy ảnh từ ESP32-CAM
        resp = requests.get(URL_CAPTURE, timeout=1)
        img_arr = np.array(bytearray(resp.content), dtype=np.uint8)
        img = cv2.imdecode(img_arr, -1)

        if img is not None:
            # Resize để xử lý nhanh
            img = cv2.resize(img, (640, 480))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Cải thiện độ tương phản
            gray = clahe.apply(gray)
            
            # Phát hiện mặt với độ nhạy cao
            faces = face_cascade.detectMultiScale(gray, 1.05, 4, minSize=(50, 50))

            if len(faces) > 0:
                # Chỉ lấy mặt lớn nhất (chủ yếu là mặt người, không phải đối tượng khác)
                (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
                
                # Mở rộng vùng 20% để có context tốt hơn (mũi, tai...)
                pad = 10
                x1 = max(0, x - pad)
                y1 = max(0, y - pad)
                x2 = min(gray.shape[1], x + w + pad)
                y2 = min(gray.shape[0], y + h + pad)
                
                face_roi = gray[y1:y2, x1:x2]
                
                # Chuẩn hóa kích thước để AI học tốt hơn
                face_roi = cv2.resize(face_roi, (640, 640))
                
                count += 1
                # Lưu file
                file_path = f"{FOLDER_DATA}/{USER_NAME}.{USER_ID}.{count}.jpg"
                cv2.imwrite(file_path, face_roi)
                
                # Hiển thị
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, f"Dang quet: {count}/{TARGET_COUNT}", (x, y-15), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                print(f"✓ Đã lưu ảnh {count}/{TARGET_COUNT} -> {file_path}")
            else:
                cv2.putText(img, "Khong thay mat - Nhin vao camera", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            cv2.imshow("QUET MAT AI - RO NET", img)

        # Nhấn 'q' để dừng sớm
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n[!] Dừng sớm.")
            break
            
    except requests.exceptions.RequestException as e:
        print(f"Lỗi kết nối: {e}")
        continue
    except Exception as e:
        print(f"Lỗi: {e}")
        continue

print(f"\n[OK] Đã lưu {count} ảnh vào thư mục '{FOLDER_DATA}'.")
print("Tiếp theo: Chạy train.py để huấn luyện model.")
cv2.destroyAllWindows()