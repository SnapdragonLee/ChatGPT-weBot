# -*- coding: utf-8 -*-
import json
import time

from revChat.revChatGPT import Chatbot, configure

with open(".config/config.json", encoding="utf-8") as f:
    config = json.load(f)
f.close()

rev_config = configure()

global_dict = dict()

# 标志数字
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


def getid():
    id = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    return id


def get_chat_nick_p(wx_id, room_id):
    qs = {
        "id": getid(),
        "type": CHATROOM_MEMBER_NICK,
        "wxid": wx_id,
        "roomid": room_id,
        "content": "null",
        "nickname": "null",
        "ext": "null"
    }
    s = json.dumps(qs)
    return s


def debug_switch():
    qs = {
        "id": getid(),
        "type": DEBUG_SWITCH,
        "content": "off",
        "wxid": "ROOT",
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
        "wxid": "null",
        "roomid": "null",
        "content": "null",
        "nickname": "null",
        "ext": "null"
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
        "ext": "null"
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
        "roomid": "null",
        "content": "null",
        "nickname": "null",
        "ext": "null"
    }
    s = json.dumps(qs)
    return s


def get_personal_detail(wx_id):
    qs = {
        "id": getid(),
        "type": PERSONAL_DETAIL,
        "wxid": wx_id,
        "roomid": "null",
        "content": "null",
        "nickname": "null",
        "ext": "null"
    }
    s = json.dumps(qs)
    return s


def send_txt_msg(text_string, wx_id):
    qs = {
        "id": getid(),
        "type": TXT_MSG,
        "wxid": wx_id,
        "roomid": "null",
        "content": text_string,  # 文本消息内容
        "nickname": "null",
        "ext": "null"
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
        "ext": "null"
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


def handle_recv_txt_msg(j):  # todo
    print(j)
    content: str = j["content"]
    wx_id: str = j["wxid"]
    room_id = ""
    chatbot: Chatbot

    if wx_id[-9] != "@":
        chatbot = global_dict.get(tuple[wx_id, ""])
    else:
        room_id = wx_id
        wx_id = j["id1"]
        chatbot = global_dict.get(tuple[wx_id, room_id])

    if config["autoReply"] and (((content.startswith(config["privateChatKey"]) and config["privateReplyMode"]) or
                                 (content.startswith(config["groupChatKey"]) and config["groupReplyMode"]))):

        if wx_id[-9] != "@":
            chatbot = Chatbot(
                rev_config,
                conversation_id=None,
                parent_id=None,
            )
            print(j)

        else:  # todo groupchat recognition
            pass
    elif content.startswith(config["resetChatKey"]):
        pass

    elif content.startswith(config["regenerateKey"]):
        pass

    elif content.startswith(config["rollbackKey"]):
        pass


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
        raise Exception("exception detected, check revChatGPT login")
    else:
        print("ChatGPT login success!\n")

    # ws.send(send_wxuser_list())  # 获取微信通讯录好友列表
    # ws.send(get_chatroom_memberlist())
    ws.send(get_personal_info())

    # ws.send(send_txt_msg("我上号了", "filehelper"))

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
    for item in global_dict:
        print("clear conversation id:" + item.parent_id)
        item.clear_conversations()

    print(ws)
    print("closed")
