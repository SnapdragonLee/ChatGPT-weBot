# -*- coding: utf-8 -*-

from shared.shared import *


def get_self_login():
    qs = {
        'type': CHECK_LOGIN
    }
    return json.dumps(qs)


def get_self_info():
    qs = {
        'type': CHECK_SELF_INFO
    }
    return json.dumps(qs)


def get_personal_info(wx_id):
    qs = {

        'type': CHECK_PERSON_INFO,
        'wxid': wx_id,
    }
    return json.dumps(qs)


def get_db_info():
    qs = {
        'type': CHECK_DB_INFO
    }
    return json.dumps(qs)


def get_chatroom_memberlist(room_id):
    qs = {
        'type': GET_CHATROOM_MEMBER,
        'chatRoomId': room_id
    }
    return json.dumps(qs)


def get_chatroom_info(room_id):
    qs = {
        'type': GET_CHATROOM_INFO,
        'chatRoomId': room_id
    }
    return json.dumps(qs)


def get_user_list():
    qs = {
        'type': GET_USER_LIST
    }
    return json.dumps(qs)
