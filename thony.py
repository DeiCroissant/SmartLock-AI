import network
import socket
from machine import Pin, SoftI2C, PWM
import time
from i2c_lcd import I2cLcd

# --- 1. CÀI ĐẶT THIẾT BỊ ---
buzzer = Pin(19, Pin.OUT)
servo = PWM(Pin(18), freq=50)
i2c = SoftI2C(sda=Pin(21), scl=Pin(22), freq=100000)

try:
    lcd = I2cLcd(i2c, 0x27, 2, 16)
except OSError:
    lcd = I2cLcd(i2c, 0x3f, 2, 16)

# Thông tin WiFi do ESP32-CAM phát ra
SSID_CAM = "AI-CAMERA-VINH"
PASS_CAM = "12345678"

def set_servo_angle(angle):
    duty = int(40 + (angle / 180) * 75)
    servo.duty(duty)

def update_lcd(l1, l2):
    lcd.clear()
    lcd.move_to(0, 0); lcd.putstr(l1)
    lcd.move_to(0, 1); lcd.putstr(l2)

# --- 2. KỊCH BẢN XỬ LÝ ---

def handle_owner():
    print(">>> XÁC NHẬN CHỦ NHÀ: ĐANG MỞ CỬA")
    update_lcd("XIN CHAO VINH!", "CUA DANG MO...")
    # Kêu 2 tiếng bíp ngắn (Ting ting)
    for _ in range(2):
        buzzer.value(1); time.sleep(0.1); buzzer.value(0); time.sleep(0.1)
    set_servo_angle(90) 
    time.sleep(3) # Đợi 3 giây cho người đi qua (đóng lại sau 3s theo yêu cầu)
    set_servo_angle(0)
    update_lcd("TRANG THAI:", "DA KHOA CUA")
    # Kêu 1 tiếng bíp dài báo đã đóng
    buzzer.value(1); time.sleep(0.5); buzzer.value(0)

def handle_alert():
    print(">>> CẢNH BÁO: NGƯỜI LẠ XÂM NHẬP")
    update_lcd("CANH BAO!!!", "NGUOI LA XAM NHAP")
    # Kêu 4 tiếng dồn dập (Ting ting ting ting)
    for _ in range(4):
        buzzer.value(1); time.sleep(0.08); buzzer.value(0); time.sleep(0.08)
    time.sleep(1)
    update_lcd("TRANG THAI:", "DA KHOA CUA")

# --- 3. SERVER NHẬN LỆNH ---

def start_server():
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    update_lcd("DANG KET NOI...", "WIFI CAMERA")
    sta.connect(SSID_CAM, PASS_CAM)
    
    while not sta.isconnected(): 
        time.sleep(0.5)
        print(".", end="")
    
    ip = sta.ifconfig()[0]
    update_lcd("DA KET NOI!", "IP: " + ip)
    print("\nIP của Thonny là:", ip)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))
    s.listen(1)
    
    while True:
        try:
            conn, addr = s.accept()
            req = conn.recv(1024).decode()
            if "GET /open" in req:
                conn.send('HTTP/1.1 200 OK\n\nOK')
                conn.close()
                handle_owner()
            elif "GET /alert" in req:
                conn.send('HTTP/1.1 200 OK\n\nOK')
                conn.close()
                handle_alert()
            else:
                conn.send('HTTP/1.1 200 OK\n\nREADY')
                conn.close()
        except: pass

try:
    set_servo_angle(0) # Khóa cửa ban đầu
    buzzer.value(0)
    start_server()
except:
    print("Dừng hệ thống.")
