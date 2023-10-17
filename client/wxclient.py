# -*- coding: utf-8 -*-

from basic.task import *
from multithread.threads import *
from .handle import handle_response

# data
global_thread = []


def on_open(ws):
    # ws.send(send_pic_msg(wx_id='filehelper', room_id='', content=''))
    # ws.send(send_wxuser_list())
    # ws.send(get_chatroom_memberlist())

    # ws.send(send_txt_msg('server is online', 'filehelper'))
    # ws.send(send_pic_msg(wx_id='filehelper', content=os.path.join(os.path.abspath(cache_dir), '')))
    # ws.send(get_personal_info())
    # ws.send(send_at_msg('wxid_im782exge5tk12', '43840311309@chatroom', '000','' ))

    for i in range(0, 4):
        normal_processor = Processor(nrm_que)
        global_thread.append(normal_processor)

    for i in range(0, 2):
        chat_processor = Processor(chat_que)
        global_thread.append(chat_processor)

    for i in range(0, 4):
        image_processor = Processor(img_que)
        global_thread.append(image_processor)


def on_message(ws, message):
    j = json.loads(message)
    # print(j)

    handle_response(ws, j)


def on_error(ws, error):
    print(ws)
    print(error)


def on_close(ws, close_status_code, close_msg):
    for key, value in global_dict.items():
        print('clear conversation:' + key)
        del value

    print(f'WebSocket closed with status code: 0')
    print(f'Closed!')


server = 'ws://' + server_host + '/ws'

# websocket.enableTrace(True)

ws = websocket.WebSocketApp(server,
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
