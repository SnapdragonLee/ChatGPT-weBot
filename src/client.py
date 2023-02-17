# -*- coding: utf-8 -*-
import websocket
import time
import json

server_host = '127.0.0.1:5555'
SERVER = "ws://" + server_host

HEART_BEAT = 5005
RECV_TXT_MSG = 1
RECV_PIC_MSG = 3
USER_LIST = 5000
GET_USER_LIST_SUCCSESS = 5001
GET_USER_LIST_FAIL = 5002
TXT_MSG = 555
PIC_MSG = 500
AT_MSG = 550
CHATROOM_MEMBER = 5010
CHATROOM_MEMBER_NICK = 5020
PERSONAL_INFO = 6500
DEBUG_SWITCH = 6000
PERSONAL_DETAIL = 6550
DESTROY_ALL = 9999


# def getid():
#     id = int(time.time() * 1000)
#     return id

def getid():
    id = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    return id


def get_chat_nick_p(roomid):
    qs = {
        'id': getid(),
        'type': CHATROOM_MEMBER_NICK,
        'content': roomid,
        'wxid': 'ROOT',
    }
    s = json.dumps(qs)
    return s


def debug_switch():
    qs = {
        'id': getid(),
        'type': DEBUG_SWITCH,
        'content': 'off',
        'wxid': 'ROOT',
    }
    s = json.dumps(qs)
    return s


def handle_nick(j):
    data = j.content
    i = 0
    for d in data:
        print(d.nickname)
        i += 1


def hanle_memberlist(j):
    data = j.content
    i = 0
    for d in data:
        print(d.roomid)
        i += 1


def get_chatroom_memberlist():
    qs = {
        'id': getid(),
        'type': CHATROOM_MEMBER,
        'wxid': 'null',
        'content': 'op:list member ',
    }
    s = json.dumps(qs)
    return s


def send_at_meg():
    qs = {
        'id': getid(),
        'type': AT_MSG,
        'roomid': 'Your roomid',  # not null
        'content': '我能吞下玻璃而不伤身体',
        'nickname': '[微笑]Python',
    }
    s = json.dumps(qs)
    return s


def destroy_all():
    qs = {
        'id': getid(),
        'type': DESTROY_ALL,
        'content': 'none',
        'wxid': 'node',
    }
    s = json.dumps(qs)
    return s


def send_pic_msg():
    qs = {
        'id': getid(),
        'type': PIC_MSG,
        'content': 'C:\\Users\\14988\\Desktop\\temp\\2.jpg',
        'wxid': '获取的wxid',
    }
    s = json.dumps(qs)
    return s


def get_personal_detail():
    qs = {
        'id': getid(),
        'type': PERSONAL_DETAIL,
        'content': 'op:personal detail',
        'wxid': '获取的wxid',
    }
    s = json.dumps(qs)
    return s


def get_personal_info():
    qs = {
        'id': getid(),
        'type': PERSONAL_INFO,
        'wxid': 'null',
        'roomid': 'null',
        'content': 'null',
        'nickname': "null",
        'ext': 'null'
    }
    s = json.dumps(qs)
    return s


def send_txt_msg(text_string, wxid):
    '''
    发送消息给好友
    '''
    qs = {
        'id': getid(),
        'type': TXT_MSG,
        'wxid': wxid,  # wxid,
        'roomid': 'null',
        'content': text_string,  # 文本消息内容
        'nickname': "null",
        'ext': 'null'
    }
    s = json.dumps(qs)
    return s


def send_wxuser_list():
    '''
    获取微信通讯录用户名字和wxid
    '''
    qs = {
        'id': getid(),
        'type': USER_LIST,
        'wxid': '',
        'roomid': '',
        'content': '',
        'nickname': '',
        'ext': 'null'
    }
    s = json.dumps(qs)
    return s


def handle_wxuser_list(j):
    j_ary = j['content']
    i = 0
    # 微信群
    for item in j_ary:
        i += 1
        id = item['wxid']
        m = id.find('@')
        if m != -1:
            print(i, id, item['name'])
    # 微信其他好友，公众号等
    for item in j_ary:
        i += 1
        id = item['wxid']
        m = id.find('@')
        if m == -1:
            print(i, id, item['name'])


def handle_recv_pic_msg(j):
    print(j)


def handle_recv_txt_msg(j):
    print(j)


def heartbeat(j):
    print(j)


def on_open(ws):
    ws.send(send_wxuser_list())  # 获取微信通讯录好友列表
    # ws.send(send_txt_msg('我上号了', 'filehelper'))

    # ws.send(send_txt_msg())     # 向你的好友发送微信文本消息


def on_message(ws, message):
    print(ws)
    j = json.loads(message)
    # print(j)
    resp_type = j['type']
    # switch结构
    action = {
        CHATROOM_MEMBER_NICK: handle_nick,
        PERSONAL_DETAIL: print,
        AT_MSG: print,
        DEBUG_SWITCH: print,
        PERSONAL_INFO: print,
        TXT_MSG: print,
        PIC_MSG: print,
        CHATROOM_MEMBER: hanle_memberlist,
        RECV_PIC_MSG: handle_recv_pic_msg,
        RECV_TXT_MSG: handle_recv_txt_msg,
        HEART_BEAT: heartbeat,
        USER_LIST: handle_wxuser_list,
        GET_USER_LIST_SUCCSESS: handle_wxuser_list,
        GET_USER_LIST_FAIL: handle_wxuser_list,
    }
    action.get(resp_type, print)(j)


def on_error(ws, error):
    print(ws)
    print(error)


def on_close(ws):
    print(ws)
    print("closed")


websocket.enableTrace(True)
ws = websocket.WebSocketApp(SERVER,
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.run_forever()
