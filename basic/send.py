# -*- coding: utf-8 -*-

from shared.shared import *


def send_txt_msg(wx_id, msg):
    qs = {
        'type': SEND_TXT_MSG,
        'wxid': wx_id,
        'msg': msg
    }
    return json.dumps(qs)


def send_at_msg(wx_id, room_id, msg):
    qs = {
        'type': SEND_TXT_AT_MSG,
        'wxids': wx_id,
        'chatRoomId': room_id,
        'msg': msg
    }
    return json.dumps(qs)


def send_pic_msg(wx_id, image_path):
    qs = {
        'type': SEND_PIC_MSG,
        'wxid': wx_id,
        'imagePath': image_path
    }
    return json.dumps(qs)


def send_attach_file(wx_id, file_path):
    qs = {
        'type': SEND_ATTACH_FILE,
        'wxid': wx_id,
        'filePath': file_path
    }
    return json.dumps(qs)


def send_custom_emoji(wx_id, file_path):
    qs = {
        'type': SEND_CUSTOM_EMJ,
        'wxid': wx_id,
        'filePath': file_path
    }
    return json.dumps(qs)


def send_pat_msg(wx_id, receiver_id):
    qs = {
        'type': SEND_PAT_MSG,
        'wxid': wx_id,
        'receiver': receiver_id
    }
    return json.dumps(qs)


def send_forward_msg(wx_id, msg_id):
    qs = {
        'type': SEND_FORWARD_MSG,
        'wxid': wx_id,
        'msgId': msg_id
    }
    return json.dumps(qs)


def send_forward_gzhmsg_id(wx_id, msg_id):
    qs = {
        'type': SEND_FORWARD_GZH_ID_MSG,
        'wxid': wx_id,
        'msgId': msg_id
    }
    return json.dumps(qs)


def send_forward_gzh_msg(wx_id, app_name, username, title, url, thumb_url, digest):
    qs = {
        'type': SEND_FORWARD_GZH_MSG,
        'wxid': wx_id,
        'appName': app_name,
        'userName': username,
        'title': title,
        'url': url,
        'thumbUrl': thumb_url,
        'digest': digest
    }
    return json.dumps(qs)


def send_applet_msg(wx_id, waid_concat, wa_id, appletwx_id, json_param, headimg_url, main_img, index_page):
    qs = {
        'type': SEND_APPLET_MSG,
        'wxid': wx_id,
        'waidConcat': waid_concat,
        'waid': wa_id,
        'appletWxid': appletwx_id,
        'jsonParam': json_param,
        'headImgUrl': headimg_url,
        'mainImg': main_img,
        'indexPage': index_page
    }
    return json.dumps(qs)
