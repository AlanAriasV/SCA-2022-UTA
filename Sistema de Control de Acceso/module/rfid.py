import threading
import time

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522


class RFID:
    def __init__(self, id_dict: dict = {}):
        GPIO.setwarnings(False)
        self.on = True
        self.reader = SimpleMFRC522()
        self.id_dict = id_dict
        self.mode = 'read'
        self.id_name = ''
        self.id = None
    
    def start(self, t_bot, camera):
        self.t_bot = t_bot
        self.camera = camera
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(7, GPIO.OUT)
        GPIO.output(7, False)
        while self.on:
            self.id = self.reader.read_id()
            if self.mode == 'read':
                self.__read_id()
            elif self.mode == 'register':
                self.__add_id()
            else:
                self.__remove_id()
            self.id = None
                
    def __read_id(self):
        GPIO.output(7, True)
        if (self.id in self.id_dict) :
            message = f'TAG identificado\n{self.id_dict[self.id]} ha ingresado al domicilio'
            self.t_bot.send_message(message=message)
        else :
            caption = f'TAG no identificado\nExtraño en la entrada al domicilio'
            self.t_bot.send_photo(caption=caption)
        self.mode = 'read'
        time.sleep(5)
        GPIO.output(7, False)
    
        
                
    def __add_id(self):
        GPIO.output(7, True)
        if (self.id not in self.id_dict):
#             print(self.id_name)
            self.id_dict[self.id] = self.id_name
            self.save_id_dict()
            self.id_name = ''
            message = 'El TAG se registró correctamente'
        else:
            message = 'El TAG ya se encuentra registrado'
        self.t_bot.send_message(message=message)
        self.mode = 'read'
        time.sleep(5)
        GPIO.output(7, False)
    
    def __remove_id(self):
        GPIO.output(7, True)
        if (self.id in self.id_dict):
            self.id_dict.pop(self.id)
            self.save_id_dict()
            message = 'El TAG se eliminó correctamente'
        else:
            message = 'El TAG no se encuentra registrado'
        self.t_bot.send_message(message=message)
        self.mode = 'read'
        time.sleep(5)
        GPIO.output(7, False)
        
    def __save_id_dict(self):
        with open('./data/data.txt', 'r') as data:
            data_list = data.readlines()
        new_id_list = 'id_list:'
        for k, v in self.id_dict.items():
            new_id_list += f' {k}:{v.replace(" ", ".")}'
        data_list[2] = new_id_list
        with open('./data/data.txt', 'w') as data:
            data.writelines(data_list)
    
    def set_mode(self, mode: str, name: str = ''):
        self.mode = mode
        self.id_name = name
    
    def motion_detected(self):
        time.sleep(10)
        if not self.id:
            self.t_bot.send_photo(caption='Intruso')
        time.sleep(7)
        self.camera.set_state_motion_detection(state=True)
    
    def stop(self):
        print('stop')
        self.on = False;
        GPIO.cleanup()
