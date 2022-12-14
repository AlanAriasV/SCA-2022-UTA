import time

import telegram


class TelegramBot():
    def __init__(self, token: str = '', chat_id: int = 0):
        self.valid = False
        self.token = token
        self.chat_id = chat_id
        self.init_bot()
        
    def init_bot(self):
        if (self.token == ''):
            while (not self.valid):
                self.token = str(input('enter token: '))
                try:
                    self.bot = telegram.Bot(self.token)
                    self.valid = True
                except:
                    print('invalid token\n')
        else:
            self.bot = telegram.Bot(self.token)
            self.valid = True
        self.updates = self.bot.get_updates()
        self.commands = [f'/{i["command"]}' for i in self.bot.getMyCommands()]# + ['/stop']
#         print(self.commands)
        try:
            self.update_id = self.updates[-1].update_id
            self.set_chat_id()
        except:
            self.update_id = None

    def set_chat_id(self):
        i = -1
        while (self.chat_id == 0):
            answer = str(input(f'is <<{self.updates[-1].message.chat.username}>> your username? [y/n]: ')).lower()
            if (answer == 'y'):
                self.chat_id = int(self.updates[i].message.chat.id)
            elif (answer == 'n'):
                i -= 1
            else:
                print('invalid option, try again\n')

    def start(self, camera = None, rfid = None):
        self.camera = camera
        self.rfid = rfid
        self.on = True
#         self.send_message(message='try')
        while self.on:
            if (self.updates != []):
                if (self.update_id != self.updates[-1].update_id):
                    self.update_id = self.updates[-1].update_id
                    text: str = self.updates[-1].message.text
                    if (text in self.commands):
                        if text == self.commands[0]:
                            self.__send_help()
                        elif text == self.commands[1]:
                            self.send_photo() 
                        elif text == self.commands[2]:
                            self.__read_id()
                        elif text in self.commands[3]:
                            self.__incomplete(text=text)
                        elif text == self.commands[4]:
                            self.__delete_id()
                        elif text == self.commands[5]:
                            self.__start_motion_detection()
                        elif text == self.commands[6]:
                            self.__stop_motion_detection()
                        else:
                            self.__send_state()
                    elif (text.startswith('/registrar')):
                        name = text[10:].replace('.', ' ').replace(',', ' ').replace('_', ' ').replace('-', ' ').strip()
                        self.__register_id(name=name)
                    else:
                        message = 'Ingrese /help para obtener más información'
                        self.send_message(message=message)
                time.sleep(1)
                try:
                    self.updates = self.bot.get_updates()
                except:
                    continue
                # on = False

    

    def __send_help(self):
        message = 'Lista de Comandos'
        for command in self.commands:
            message += f'\n{command}'
        self.send_message(message=message)

    def send_photo(self, caption: str = 'foto'):
        result = self.camera.take_photo(caption=caption)
        if (result[0]):
            caption = result[1]
            photo = f'img/{result[1]}.png'
            self.bot.send_photo(self.chat_id, open(photo, 'rb'), caption)
        else:
            message = result[1]
            self.send_message(message=message)
    
    def __incomplete(self, text: str):
        message = f'Ingrese el comando {text} con uno de los siguientes formatos:\n'
        message += f'{text} nombre apellido'
        self.send_message(message=message)
    
    def __read_id(self):
        message = 'RFID en modo de lectura'
        self.send_message(message=message)
        self.rfid.set_mode(mode='read')
    
    def __register_id(self, name: str):
        message = 'Acerque el TAG que desea registrar al RFID'
        self.send_message(message=message)
        self.rfid.set_mode(mode='register', name=name)
        
    def __delete_id(self):
        message = 'Acerque el TAG que desea eliminar al RFID'
        self.send_message(message=message)
        self.rfid.set_mode(mode='delete')
        
    def __start_motion_detection(self):
        message = 'Detección de  movimiento activado'
        self.send_message(message=message)
        self.camera.set_state_motion_detection(state=True)
    
    def __stop_motion_detection(self):
        message = 'Detección de  movimiento desactivado'
        self.send_message(message=message)
        self.camera.set_state_motion_detection(state=False)
    
    def send_message(self, message: str):
        self.bot.send_message(self.chat_id, message)
        
    def __send_state(self):
        message = f'Estado del Sistema'
        self.send_message(message=message)
        
        time.sleep(2)
        message = f'Bot:\n-Estado: Funcionando'
        self.send_message(message=message)
        
        time.sleep(2)
        rfid_state = 'Funcionando' if self.rfid else 'Detenido'
        message = f'RFID:\n-Estado: {rfid_state}\n'
        if self.rfid:
            rfid_mode = 'Lectura' if self.rfid.mode == 'read' else 'Registro' if self.rfid.mode == 'register' else 'Eliminar'
            message += f'-Modo: {rfid_mode}'
        else:
            message += f'Comuniquese al {123} para obtener ayuda'
        self.send_message(message=message)
        
        time.sleep(2)
        camera_state = 'Funcionando' if self.camera else 'Detenido'
        message = f'Cámara:\n-Estado: {camera_state}\n'
        if self.rfid:
            camera_md_state = 'Activado' if self.camera.motion_detection else 'Desactivado'
            message += f'-Detección de Movimiento: {camera_md_state}'
        else:
            message += f'Comuniquese al {123} para obtener ayuda'
        self.send_message(message=message)
        

    def __stop(self):
        message = 'Deteniendo...'
        self.send_message(message=message)
        self.on = False
