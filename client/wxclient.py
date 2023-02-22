# -*- coding: utf-8 -*-
import json
import time
import re
import websocket

from revChat.revChatGPT import Chatbot, configure

# config
with open(".config/config.json", encoding="utf-8") as f:
    config = json.load(f)
f.close()

server_host = config["server_host"]
autoReply = config["autoReply"]
groupChatKey = config["groupChatKey"]
groupReplyMode = config["groupReplyMode"]
privateChatKey = config["privateChatKey"]
privateReplyMode = config["privateReplyMode"]
helpKey = config["helpKey"]
resetChatKey = config["resetChatKey"]
regenerateKey = config["regenerateKey"]
rollbackKey = config["rollbackKey"]

rev_config = configure()

# Signal Number
HEART_BEAT = 5005
RECV_TXT_MSG = 1
RECV_PIC_MSG = 3
NEW_FRIEND_REQUEST = 37
RECV_TXT_CITE_MSG = 49

TXT_MSG = 555
PIC_MSG = 500
AT_MSG = 550

USER_LIST = 5000
GET_USER_LIST_SUCCSESS = 5001
GET_USER_LIST_FAIL = 5002
ATTACH_FILE = 5003
CHATROOM_MEMBER = 5010
CHATROOM_MEMBER_NICK = 5020

DEBUG_SWITCH = 6000
PERSONAL_INFO = 6500
PERSONAL_DETAIL = 6550

DESTROY_ALL = 9999
AGREE_TO_FRIEND_REQUEST = 10000

# data
global_dict = dict()


def getid():
    id = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    return id


def get_chat_nick_p(wx_id, room_id):
    qs = {
        "id": getid(),
        "type": CHATROOM_MEMBER_NICK,
        "wxid": wx_id,
        "roomid": room_id,
        "content": "",
        "nickname": "",
        "ext": ""
    }
    s = json.dumps(qs)
    return s


def debug_switch():
    qs = {
        "id": getid(),
        "type": DEBUG_SWITCH,
        "content": "off",
        "wxid": "",
    }
    s = json.dumps(qs)
    return s


def handle_nick(j):
    data = json.loads(j["content"])
    print("测试群成员昵称：" + data["nick"])
    return data["nick"]


def hanle_memberlist(j):
    data = j["content"]
    print(data)
    # for d in data:
    #     print(d["room_id"])


def get_chatroom_memberlist():
    qs = {
        "id": getid(),
        "type": CHATROOM_MEMBER,
        "wxid": "",
        "roomid": "",
        "content": "",
        "nickname": "",
        "ext": ""
    }
    s = json.dumps(qs)
    return s


def send_at_meg(wx_id, room_id, content, nickname):
    qs = {
        "id": getid(),
        "type": AT_MSG,
        "wxid": wx_id,
        "roomid": room_id,
        "content": content,
        "nickname": nickname,
        "ext": ""
    }
    s = json.dumps(qs)
    return s


def destroy_all():
    qs = {
        "id": getid(),
        "type": DESTROY_ALL,
        "content": "none",
        "wxid": "node",
    }
    s = json.dumps(qs)
    return s


def send_pic_msg():
    qs = {
        "id": getid(),
        "type": PIC_MSG,
        "content": ".jpg",
        "wxid": "获取的wxid",
    }
    s = json.dumps(qs)
    return s


def get_personal_info():
    qs = {
        "id": getid(),
        "type": PERSONAL_INFO,
        "wxid": "ROOT",
        "roomid": "",
        "content": "",
        "nickname": "",
        "ext": ""
    }
    s = json.dumps(qs)
    return s


def get_personal_detail(wx_id):
    qs = {
        "id": getid(),
        "type": PERSONAL_DETAIL,
        "wxid": wx_id,
        "roomid": "",
        "content": "",
        "nickname": "",
        "ext": ""
    }
    s = json.dumps(qs)
    return s


def send_txt_msg(text_string, wx_id):
    qs = {
        "id": getid(),
        "type": TXT_MSG,
        "wxid": wx_id,
        "roomid": "",
        "content": text_string,  # 文本消息内容
        "nickname": "",
        "ext": ""
    }
    s = json.dumps(qs)
    return s


def send_wxuser_list():
    qs = {
        "id": getid(),
        "type": USER_LIST,
        "wxid": "",
        "roomid": "",
        "content": "",
        "nickname": "",
        "ext": ""
    }
    s = json.dumps(qs)
    return s


def handle_wxuser_list(j):
    content = j["content"]
    i = 0
    # 微信群
    for item in content:
        i += 1
        id = item["wxid"]
        m = id.find("@")
        if m != -1:
            print(i, "群聊", id, item["name"])

    # 微信其他好友，公众号等
    for item in content:
        i += 1
        id = item["wxid"]
        m = id.find("@")
        if m == -1:
            print(i, "个体", id, item["name"], item["wxcode"])


def handle_recv_txt_msg(j):
    print(j)

    wx_id = j["wxid"]
    room_id = ""
    content: str = j["content"]
    reply = ""

    is_ask: bool = False
    is_room: bool

    chatbot: Chatbot

    if len(wx_id) < 9 or wx_id[-9] != "@":
        is_room = False
        wx_id: str = j["wxid"]
        chatbot = global_dict.get((wx_id, ""))

        if content.startswith(privateChatKey):
            is_ask = True
            content = re.sub(privateChatKey, "", content)

    else:
        is_room = True
        wx_id = j["id1"]
        room_id = j["wxid"]
        chatbot = global_dict.get((wx_id, room_id))

        if content.startswith(groupChatKey):
            is_ask = True
            content = re.sub(groupChatKey, "", content)

    if autoReply and ((not is_room and privateReplyMode) or (is_room and groupReplyMode)):
        if is_ask:
            if chatbot is None:
                chatbot = Chatbot(
                    rev_config,
                    conversation_id=None,
                    parent_id=None,
                )
                if is_room:
                    global_dict[(wx_id, room_id)] = chatbot
                else:
                    global_dict[(wx_id, "")] = chatbot

            print("ask:" + content)
            for data in chatbot.ask(
                    prompt=content,
            ):
                reply += data["message"][len(reply):]

        elif content.startswith(helpKey):
            if is_room:
                reply = str(
                    b'\xe6\xac\xa2\xe8\xbf\x8e\xe4\xbd\xbf\xe7\x94\xa8 ChatGPT-weBot\xef\xbc\x8c\xe6\x9c\xac\xe9'
                    b'\xa1\xb9\xe7\x9b\xae\xe5\x9c\xa8 github \xe5\x90\x8c\xe5\x90\x8d\xe5\xbc\x80\xe6\xba\x90\n',
                    'utf-8') + helpKey + " 查看可用命令帮助\n" + groupChatKey + " 唤醒群内机器人\n" + resetChatKey + \
                        " 重置上下文\n" + regenerateKey + " 重新生成答案\n" + rollbackKey + " +数字n 回滚到倒数第n个问题"

            else:
                reply = str(
                    b'\xe6\xac\xa2\xe8\xbf\x8e\xe4\xbd\xbf\xe7\x94\xa8 ChatGPT-weBot\xef\xbc\x8c\xe6\x9c\xac\xe9'
                    b'\xa1\xb9\xe7\x9b\xae\xe5\x9c\xa8 github \xe5\x90\x8c\xe5\x90\x8d\xe5\xbc\x80\xe6\xba\x90\n',
                    'utf-8') + helpKey + " 查看可用命令帮助\n" + privateChatKey + " 唤醒机器人\n" + resetChatKey + \
                        " 重置上下文\n" + regenerateKey + " 重新生成答案\n" + rollbackKey + " +数字n 回滚到倒数第n个问题"
            time.sleep(1.5)

        elif content.startswith(resetChatKey):
            if chatbot is not None:
                chatbot.clear_conversations()
                del (global_dict[(wx_id, room_id)])
                reply = "重置完成"
            else:
                reply = "您还没有开始第一次对话"
                time.sleep(1.5)

        elif content.startswith(regenerateKey):  # todo
            pass

        elif content.startswith(rollbackKey):  # todo
            pass
        else:
            return
    else:
        return

    if is_room:
        ws.send(send_txt_msg(text_string=reply.strip(), wx_id=room_id))
    else:
        ws.send(send_txt_msg(text_string=reply.strip(), wx_id=wx_id))
    print("reply:" + reply)


def handle_recv_pic_msg(j):
    print(j)


def handle_recv_txt_cite(j):
    content = j["content"]
    print(j)


def handle_heartbeat(j):
    print(j)


def on_open(ws):
    chatbot = Chatbot(
        rev_config,
        conversation_id=None,
        parent_id=None,
    )
    try:
        chatbot.login()
    except Exception:
        raise Exception("Exception detected, check revChatGPT login config")
    else:
        print("\nChatGPT login test success!\n")

    # ws.send(send_wxuser_list())  # 获取微信通讯录好友列表
    # ws.send(get_chatroom_memberlist())
    ws.send(get_personal_info())

    # ws.send(send_txt_msg("server is online", "filehelper"))

    # ws.send(send_txt_msg())     # 向你的好友发送微信文本消息


def on_message(ws, message):
    j = json.loads(message)
    # print(j)

    resp_type = j["type"]

    # switch
    action = {
        HEART_BEAT: handle_heartbeat,
        RECV_TXT_MSG: handle_recv_txt_msg,
        RECV_PIC_MSG: handle_recv_pic_msg,
        NEW_FRIEND_REQUEST: print,
        RECV_TXT_CITE_MSG: handle_recv_txt_cite,

        TXT_MSG: print,
        PIC_MSG: print,
        AT_MSG: print,

        USER_LIST: handle_wxuser_list,
        GET_USER_LIST_SUCCSESS: handle_wxuser_list,
        GET_USER_LIST_FAIL: handle_wxuser_list,
        ATTACH_FILE: print,

        CHATROOM_MEMBER: hanle_memberlist,
        CHATROOM_MEMBER_NICK: handle_nick,
        DEBUG_SWITCH: print,
        PERSONAL_INFO: print,
        PERSONAL_DETAIL: print,
    }

    action.get(resp_type, print)(j)


def on_error(ws, error):
    print(ws)
    print(error)


def on_close(ws):
    for key, value in global_dict.items():  # todo: still have bugs
        print("clear conversation id:" + value.parent_id)
        value.clear_conversations()
        del value

    print(ws)
    print("closed")


server = "ws://" + server_host

websocket.enableTrace(True)

ws = websocket.WebSocketApp(server,
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
