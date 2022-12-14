from datetime import datetime
from threading import Thread

import cv2


class Camera:
    def __init__(self):
        self.capture = cv2.VideoCapture(-1)
        self.motion_detection = True
# 
    def start(self, t_bot, rfid):
        self.t_bot = t_bot
        self.rfid = rfid
        i = 0
        while True:
            self.read, self.frame = self.capture.read()
            if self.read:
                gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                
                if i == 20:
                    bgGray = gray
                if i > 20:
                    dif = cv2.absdiff(gray, bgGray)
                    _, th = cv2.threshold(dif, 40, 255, cv2.THRESH_BINARY)
                    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    for c in cnts:
                        area = cv2.contourArea(c)
                        if area > 3000:
                            if self.motion_detection:
                                self.motion_detection = False
                                Thread(target=self.rfid.motion_detected).start()
                            x, y, w, h = cv2.boundingRect(c)
                            cv2.rectangle(self.frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.imshow('camera', self.frame)
                i += 1
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
        self.capture.release()

    def take_photo(self, caption: str):
        time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        if (self.read):
            cv2.imwrite(f'img/{caption} {time} hrs.png', self.frame)
            return (self.read, f'{caption} {time} hrs')
        else:
            return (self.read, 'Error al acceder a la cámara')
        
    def set_state_motion_detection(self, state: bool):
        self.motion_detection = state