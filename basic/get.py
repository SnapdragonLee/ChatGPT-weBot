# -*- coding: utf-8 -*-

from shared.shared import *


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
