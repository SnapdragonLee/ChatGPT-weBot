# -*- coding: utf-8 -*-
import json
import time

from apibase.revChatGPT import configure

# api model check
with open(".config/api_config.json", encoding="utf-8") as f:
    api_config = json.load(f)
f.close()

if api_config["engine"] not in [
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0301",
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-32k",
    "gpt-4-32k-0314",
]:
    error = NotImplementedError("Unsupported engine {self.engine}")
    raise error

# server config
with open(".config/server_config.json", encoding="utf-8") as f:
    config = json.load(f)
f.close()
server_host = config["server_host"]

# general config
with open(".config/config.json", encoding="utf-8") as f:
    config = json.load(f)
f.close()

autoReply = config["autoReply"]

internetKey = config["internetKey"]
internetResult = config["internetResult"]

groupChatKey = config["groupChatKey"]
grpReplyMode = config["grpReplyMode"]
grpCitationMode = config["grpCitationMode"]
privateChatKey = config["privateChatKey"]
prvReplyMode = config["prvReplyMode"]
prvCitationMode = config["prvCitationMode"]
characterKey = config["characterKey"]
conclusionKey = config["conclusionKey"]

stableDiffRly = config["stableDiffRly"]
groupImgKey = config["groupImgKey"]
privateImgKey = config["privateImgKey"]
negativePromptKey = config["negativePromptKey"]
isCached = config["isCached"]

helpKey = config["helpKey"]
resetChatKey = config["resetChatKey"]
regenerateKey = config["regenerateKey"]
rollbackKey = config["rollbackKey"]

# apibase config
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
GET_USER_LIST_SUCCESS = 5001
GET_USER_LIST_FAIL = 5002
ATTACH_FILE = 5003
CHATROOM_MEMBER = 5010
CHATROOM_MEMBER_NICK = 5020

DEBUG_SWITCH = 6000
PERSONAL_INFO = 6500
PERSONAL_DETAIL = 6550

DESTROY_ALL = 9999
OTHER_REQUEST = 10000

# stable_diff config
API_URL_v21 = "stabilityai-stable-diffusion.hf.space/queue/join"
API_URL_v15 = ""
cache_dir = ".cache/"


def getid():
    id = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    return id
