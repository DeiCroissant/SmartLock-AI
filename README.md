# SmartLock-AI 🚪

This is the source code for our IoT final project at Van Lang University. We built an "air-gapped" smart door lock that uses facial recognition to let you in. The cool part? It doesn't use the internet or any cloud services. The whole thing runs on a local WiFi network created by the ESP32 itself, making it immune to remote hacking.

## Hardware setup
* **ESP32-CAM:** Acts as the camera and the WiFi Access Point.
* **A standard Laptop:** Connects to the ESP32 network, runs Python, and handles the face recognition (the "brain").
* **ESP32 (NodeMCU):** Connected to a Servo, an I2C LCD, and a Buzzer. This is the physical lock that receives commands from the laptop.

## Why LBPH instead of YOLO?
We originally wanted to use YOLOv8 for this project. But honestly, streaming video from an ESP32-CAM to a heavy deep learning model made our laptop overheat and the lag was unbearable (barely scraping 3 FPS). We pivoted to OpenCV's **LBPH (Local Binary Patterns Histograms)**. It's an older machine learning algorithm, but it's incredibly lightweight, sensitive enough, and runs at 20+ FPS smoothly on a standard CPU. 

## How to run the system
*(Note: We didn't upload the `data/` folder or `trainer.yml` to protect our privacy. You have to train it with your own face!)*

1. Power up both ESP32 boards.
2. Connect your laptop to the ESP32-CAM's WiFi network (e.g., `AI-CAMERA-VINH`).
3. Run `python get.py` and look at the camera to collect your face data.
4. Run `python train.py` to train the model. It will generate a `trainer.yml` file.
5. Run `python ai.py`. If it recognizes you, it sends an HTTP request to the door ESP32 to open the servo. If it sees a stranger, the buzzer goes off.

> **Hardware code:** The MicroPython script for the door lock ESP32 is inside `thony.py`. You'll need to flash it to the board using Thonny IDE.
