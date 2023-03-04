# -*- coding: utf-8 -*-

from shared.shared import *


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


def send_pic_msg(wx_id, content):
    qs = {
        "id": getid(),
        "type": PIC_MSG,
        "wxid": wx_id,
        "roomid": "",
        "content": content,
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
