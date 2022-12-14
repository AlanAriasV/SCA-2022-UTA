import threading
import time

from module.telegram_bot import TelegramBot
from module.camera import Camera
from module.rfid import RFID


def main():
    try:
        data = open('data/data.txt', 'r')
        doc = data.read()
        lines = doc.split('\n')
        token = lines[0].split(' ')[1]
        chat_id = int(lines[1].split(' ')[1])
        id_list = lines[2].split(' ')[1:]
        id_dict = {}
        if (id_list != ['']):
            for i in id_list:
                kv = i.split(':')
                id_dict[int(kv[0])] = kv[1].replace('.', ' ')
        t_bot = TelegramBot(token=token, chat_id=chat_id)
    except :
        data = open('data/data.txt', 'w')
        t_bot = TelegramBot(token=token)
        token = t_bot.token
        chat_id = t_bot.chat_id
        data.write(f'token: {token}\n')
        data.write(f'chat_id: {chat_id}')
        data.write(f'id_list: ')
    finally:
        data.close()
        rfid = RFID(id_dict=id_dict)
        camera = Camera()
        threads = {'telegram_bot': threading, 'camera': threading, 'rfid': threading}
        
        threads['telegram_bot'] = threading.Thread(target=lambda: t_bot.start(camera=camera, rfid=rfid))
        
        threads['camera'] = threading.Thread(target=lambda: camera.start(t_bot=t_bot, rfid=rfid))
        
        threads['rfid'] = threading.Thread(target=lambda: rfid.start(t_bot=t_bot, camera=camera))
        
        for _, thread in threads.items():
            thread.start()

        for _, thread in threads.items():
            thread.join()


if __name__ == '__main__':
    main()