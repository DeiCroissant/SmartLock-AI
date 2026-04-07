import cv2
import numpy as np
import os
from PIL import Image

# Cấu hình đường dẫn
path = 'data'
recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def getImagesAndLabels(path):
    # Lấy tất cả file ảnh trong thư mục data
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(('.jpg', '.png', '.jpeg'))]     
    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        try:
            # Chuyển ảnh sang màu xám và mảng numpy
            PIL_img = Image.open(imagePath).convert('L') 
            img_numpy = np.array(PIL_img, 'uint8')

            # Lấy ID từ tên file: vinh.1.jpg -> lấy 1. Nếu vinh.jpg -> lấy mặc định 1
            filename = os.path.split(imagePath)[-1]
            parts = filename.split(".")
            
            if len(parts) > 2 and parts[1].isdigit():
                user_id = int(parts[1])
            else:
                user_id = 1 # ID mặc định cho chủ nhà
                
            faces = detector.detectMultiScale(img_numpy)

            for (x, y, w, h) in faces:
                faceSamples.append(img_numpy[y:y+h, x:x+w])
                ids.append(user_id)
                print(f" > Đã học xong ảnh: {filename} (ID: {user_id})")
        except Exception as e:
            print(f" ! Lỗi file {imagePath}: {e}")

    return faceSamples, ids

print("\n[INFO] Đang huấn luyện AI. Vui lòng chờ...")
faces, ids = getImagesAndLabels(path)

if len(faces) == 0:
    print("[ERROR] Không tìm thấy khuôn mặt nào trong thư mục data!")
else:
    recognizer.train(faces, np.array(ids))
    recognizer.save('trainer.yml') 
    print(f"\n[SUCCESS] Đã học xong {len(set(ids))} người với {len(faces)} ảnh mẫu.")
    print("[SUCCESS] Đã lưu bộ não vào file: trainer.yml")