# -*- coding: utf-8 -*-

from shared.shared import *


def execute_sql(db_handle, sql):
    qs = {
        "type": EXEC_SQL,
        "dbHandle": db_handle,
        "sql": sql
    }
    return json.dumps(qs)


# ACTION BELOW IS FOR CHATROOM
def add_member_chatroom(wx_id, room_id):
    qs = {
        "type": ADD_MEMBER_CHATROOM,
        "memberIds": wx_id,
        "chatRoomId": room_id
    }
    return json.dumps(qs)


def invite_member_chatroom(wx_id, room_id):
    qs = {
        "type": INVITE_MEMBER_CHATROOM,
        "memberIds": wx_id,
        'chatRoomId': room_id
    }
    return json.dumps(qs)


def del_member_chatroom(wx_id, room_id):
    qs = {
        "type": DEL_MEMBER_CHATROOM,
        "memberIds": wx_id,
        "chatRoomId": room_id
    }
    return json.dumps(qs)


def create_chatroom(wx_id):
    qs = {
        "type": CREATE_CHATROOM,
        "memberIds": wx_id
    }
    return json.dumps(qs)


def quit_chatroom(room_id):
    qs = {
        "type": QUIT_CHATROOM,
        "chatRoomId": room_id
    }
    return json.dumps(qs)


def modify_selfname_chatroom(wx_id, room_id, nick_name):
    qs = {
        "type": MODIFY_SELF_NAME,
        "wxid": wx_id,
        "chatRoomId": room_id,
        "nickName": nick_name
    }
    return json.dumps(qs)


def add_top_msg(msg_id):
    qs = {
        "type": ADD_TOP_MSG,
        "msgId": msg_id
    }
    return json.dumps(qs)


def del_top_msg(room_id, msg_id):
    qs = {
        "type": DEL_TOP_MSG,
        "msgId": msg_id,
        'chatRoomId': room_id
    }
    return json.dumps(qs)


# ACTION BELOW IS GROCERIES
def get_sns_first():
    qs = {
        "type": GET_SNS_FIRST
    }
    return json.dumps(qs)


def get_sns_next(sns_id):
    qs = {
        'type': GET_SNS_NEXT,
        'snsId': sns_id
    }
    return json.dumps(qs)


def add_favour_msg(msg_id):
    qs = {
        'type': ADD_MSG_FAVOUR,
        'msgId': msg_id
    }
    return json.dumps(qs)


def add_favour_img(wx_id, image_path):
    qs = {
        'type': ADD_IMG_FAVOUR,
        'wxid': wx_id,
        "imagePath": image_path
    }
    return json.dumps(qs)


def dw_attach_file(msg_id):
    qs = {
        'type': DW_ATTACH_FILE,
        'msgId': msg_id
    }
    return json.dumps(qs)


def dw_voice_file(msg_id, store_dir):
    qs = {
        'type': DW_VOICE_FILE,
        'msgId': msg_id,
        'storeDir': store_dir
    }
    return json.dumps(qs)


def decode_img_file(file_path, store_dir):
    qs = {
        'type': DECODE_IMG_FILE,
        'filePath': file_path,
        'storeDir': store_dir
    }
    return json.dumps(qs)


def ocr_img_file(image_path):
    qs = {
        'type': OCR_IMG_FILE,
        'imagePath': image_path
    }
    return json.dumps(qs)


# ACTION BELOW IS FOR SERVER DEBUG
def enable_log():
    qs = {
        "type": ENABLE_WECHAT_LOG
    }
    return json.dumps(qs)


def disable_log():
    qs = {
        "type": DISABLE_WECHAT_LOG
    }
    return json.dumps(qs)
