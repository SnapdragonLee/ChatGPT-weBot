import re

from basic.task import *
from multithread.threads import *
from services.model import Selfinfo
from services.chat.ChatGPTAPI import Chatbot

ws: websocket.WebSocketApp
my_info: Selfinfo


def handle_response(ws_t, j: json):
    global ws
    ws = ws_t
    resp_type = j['type']

    # switch
    action = {
        RECV_SERVER_HINT: print,
        RECV_TXT_MSG: handle_recv_txt_msg,
        RECV_PIC_MSG: handle_recv_pic_msg,
        # RECV_GZH_MSG: print,
        RECV_SNS_MSG: print,
        RECV_HISTORY_MSG: print,
        RECV_APP_MSG: print,
        RECV_FRIEND_REQUEST: print,
        # RECV_STICKER_MSG: print,
        RECV_XML_MSG: handle_recv_xml_txt,
        # RECV_DVC_MSG: print,
        RECV_VIDEO_MSG: print,
        RECV_MUSIC_MSG: print,
        RECV_CITE_MSG: print,
        RECV_APPAUDIO_MSG: print,
        RECV_HOOK_SNS: print,
        RECV_OTHER_MSG: print,
        # OP_READ_MSG_WHILE_OPEN_DVC: print,
        # OP_OPEN_CHAT_DVC: print,
        # OP_REFRESH_LIST_DVC: print,
        # OP_SNS_CHECK_UNREAD_DVC: print,
        # OP_SNS_SELF_ACTION_DVC: print,
        # OP_REFRESH_MSG_DVC: print,
        # OP_DELETE_CHATROOM_MSG_DVC: print,
        ADD_MEMBER_CHATROOM: print,
        DEL_MEMBER_CHATROOM: print,
        INVITE_MEMBER_CHATROOM: print,
        MODIFY_SELF_NAME: print,
        CREATE_CHATROOM: print,
        QUIT_CHATROOM: print,
        ADD_TOP_MSG: print,
        DEL_TOP_MSG: print,
        SEND_PIC_MSG: print,
        SEND_TXT_MSG: print,
        SEND_FORWARD_MSG: print,
        SEND_FORWARD_GZH_MSG: print,
        SEND_FORWARD_GZH_ID_MSG: print,
        SEND_TXT_AT_MSG: print,
        SEND_PAT_MSG: print,
        SEND_APPLET_MSG: print,
        SEND_ATTACH_FILE: print,
        SEND_CUSTOM_EMJ: print,
        DECODE_IMG_FILE: print,
        OCR_IMG_FILE: print,
        DW_ATTACH_FILE: print,
        DW_VOICE_FILE: print,
        ADD_MSG_FAVOUR: print,
        ADD_IMG_FAVOUR: print,
        GET_SNS_FIRST: print,
        GET_SNS_NEXT: print,
        GET_USER_LIST: handle_wxuser_list,
        GET_CHATROOM_INFO: print,
        GET_CHATROOM_MEMBER: hanle_memberlist,
        CHECK_LOGIN: print,
        CHECK_SELF_INFO: handle_self_info,
        CHECK_DB_INFO: print,
        CHECK_PERSON_INFO: print,
        EXEC_SQL: print,
        ENABLE_WECHAT_LOG: print,
        DISABLE_WECHAT_LOG: print
    }
    func = action.get(resp_type)
    if func is not None:
        func(j)


def handle_nick(j):
    data = json.loads(j['content'])
    print('测试群成员昵称：' + data['nick'])


def hanle_memberlist(j):
    data = j['content']
    print(data)
    # for d in data:
    #     print(d['room_id'])


def handle_wxuser_list(j):
    content = j['content']
    i = 0
    # 微信群
    for item in content:
        i += 1
        id = item['wxid']
        m = id.find('@')
        if m != -1:
            print(i, '群聊', id, item['name'])

    # 微信其他好友，公众号等
    for item in content:
        i += 1
        id = item['wxid']
        m = id.find('@')
        if m == -1:
            print(i, '个体', id, item['name'], item['wxcode'])


def handle_recv_txt_msg(j):
    if j['fromUser'] == my_info.wx_id:
        wx_id = j['toUser']
    else:
        wx_id = j['fromUser']
    room_id = ''
    content: str = j['content'].strip()

    access_internet: bool = False
    is_room: bool
    chatbot: Chatbot

    if len(wx_id) < 9 or wx_id[-9] != '@':
        is_room = False
    else:
        is_room = True
        room_id = wx_id
        pos = content.find(':\n', 0)
        if pos != -1:
            wx_id = content[:pos]
            content = content[pos + 2:].lstrip()
        else:
            wx_id = my_info.wx_id

    print(content +
          '  From: ' + j['fromUser'] +
          '  To: ' + j['toUser'] +
          '  \'type\': ' + str(j['type']))

    chatbot = global_dict.get((wx_id, room_id))

    is_citation = (grpCitationMode and is_room) or (prvCitationMode and not is_room)

    if autoReply and ((not is_room and prvReplyMode) or (is_room and grpReplyMode)):
        if content.startswith(helpKey):
            reply = str(
                b'\xe6\xac\xa2\xe8\xbf\x8e\xe4\xbd\xbf\xe7\x94\xa8 ChatGPT-weBot \xef\xbc\x8c\xe6\x9c\xac\xe9'
                b'\xa1\xb9\xe7\x9b\xae\xe5\x9c\xa8 github \xe5\x90\x8c\xe5\x90\x8d\xe5\xbc\x80\xe6\xba\x90\n',
                'utf-8') + helpKey + ' 查看可用命令帮助\n' + \
                    ((groupImgKey + ' 提问群AI画图机器人(仅英语) ') if is_room else (
                            privateImgKey + ' 提问AI画图机器人(仅英语) ')) + \
                    negativePromptKey + '可选负面提示\n' + \
                    ((groupChatKey + ' 提问群聊天机器人 ') if is_room else (privateChatKey + ' 提问聊天机器人 ')) + \
                    internetKey + '可联网\n' + \
                    resetChatKey + ' 重置上下文\n' + \
                    regenerateKey + ' 重新生成答案\n' + \
                    rollbackKey + ' +数字n 回滚到倒数第n个问题\n' + \
                    characterKey + '更改机器人角色设定\n' + \
                    conclusionKey + '总结对话'

            nm = NormalTask(ws, content, reply, wx_id, room_id, is_room, False)
            nrm_que.put(nm)

        elif content.startswith(resetChatKey):
            ct = ChatTask(ws, content, access_internet, chatbot, wx_id, room_id, is_room, is_citation, 'rs')
            chat_que.put(ct)

        elif content.startswith(regenerateKey):
            ct = ChatTask(ws, content, access_internet, chatbot, wx_id, room_id, is_room, is_citation, 'rg')
            chat_que.put(ct)

        elif content.startswith(rollbackKey):
            if chatbot is None or chatbot.question_num == 0:
                reply = '您还没有问过问题'

            else:
                num = re.sub('^' + rollbackKey, '', content, 1).lstrip()
                if num.isdigit():
                    if chatbot.question_num < int(num):
                        reply = '无法回滚到' + num + '个问题之前'

                    else:
                        chatbot.rollback_conversation(int(num))
                        reply = '已回滚到' + num + '个问题之前'
                else:
                    reply = '请在回滚指令后输入有效数字'

            nm = NormalTask(ws, content, reply, wx_id, room_id, is_room, is_citation)
            nrm_que.put(nm)

        elif content.startswith(characterKey):
            content = re.sub('^' + characterKey, '', content, 1).lstrip()
            if chatbot is None:
                chatbot = Chatbot(
                    api_config,
                )
                if is_room:
                    global_dict[(wx_id, room_id)] = chatbot
                else:
                    global_dict[(wx_id, '')] = chatbot

            ct = ChatTask(ws, content, access_internet, chatbot, wx_id, room_id, is_room, is_citation, 'p')
            chat_que.put(ct)

        elif content.startswith(conclusionKey):
            ct = ChatTask(ws, content, access_internet, chatbot, wx_id, room_id, is_room, is_citation, 'z')
            chat_que.put(ct)

        elif stableDiffRly and (
                (content.startswith(privateImgKey) and not is_room) or (content.startswith(groupImgKey) and is_room)):
            content = re.sub('^' + (groupImgKey if is_room else privateImgKey), '', content, 1).lstrip()
            prompt_list = re.split(negativePromptKey, content)

            ig = ImgTask(ws, prompt_list, wx_id, room_id, is_room, '2.1')
            img_que.put(ig)

        elif (content.startswith(privateChatKey) and not is_room) or (content.startswith(groupChatKey) and is_room):
            content = re.sub('^' + (groupChatKey if is_room else privateChatKey), '',
                             content, 1).lstrip()
            if content.startswith(internetKey):
                content = re.sub('^' + internetKey, '', content, 1).lstrip()
                access_internet = True
            if chatbot is None:
                chatbot = Chatbot(
                    api_config,
                )
                if is_room:
                    global_dict[(wx_id, room_id)] = chatbot
                else:
                    global_dict[(wx_id, '')] = chatbot

            ct = ChatTask(ws, content, access_internet, chatbot, wx_id, room_id, is_room, is_citation, 'c')
            chat_que.put(ct)


def handle_recv_pic_msg(j):
    print(j)


def handle_recv_xml_txt(j):
    print(j)


def handle_self_info(j):
    print(j)
    data = j['data']

    global my_info
    my_info = Selfinfo(data['wxid'], data['name'], data['account'],
                       data['currentDataPath'], data['dataSavePath'],
                       data['dbKey'])
