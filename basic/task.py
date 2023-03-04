# -*- coding: utf-8 -*-

import base64
import os.path
import string
import random
import websocket

from .send import send_txt_msg, send_pic_msg
from shared.shared import *

global_dict = dict()


class ChatTask:
    def __init__(self, ws, prompt, chatbot, wx_id, room_id, is_room, is_citation, type):
        self.ws = ws
        self.prompt = prompt
        self.bot = chatbot
        self.wx_id = wx_id
        self.room_id = room_id
        self.is_room = is_room
        self.is_citation = is_citation
        self.type = type
        self.reply = ""

    def play(self):
        if self.type == "rs":
            if self.bot is not None:
                self.bot.clear_conversations()
                del (global_dict[(self.wx_id, self.room_id)])
                self.reply = "重置完成"
            else:
                self.reply = "您还没有开始第一次对话"
                time.sleep(0.5)

        elif self.type == "rg":
            if self.bot is None or self.bot.prompt is None:
                self.reply = "您还没有问过问题"
                time.sleep(0.5)
            else:
                print("ask:" + self.bot.prompt)
                for data in self.bot.ask(
                        prompt=None,
                ):
                    self.reply += data["message"][len(self.reply):]


        elif self.type == "c":
            print("ask:" + self.prompt)
            for data in self.bot.ask(
                    prompt=self.prompt,
            ):
                self.reply += data["message"][len(self.reply):]

        print("reply: " + self.reply)
        if self.is_citation:
            self.reply = (
                             self.bot.prompt if self.type == "rg" else self.prompt) + "\n- - - - - - - - - -\n" + self.reply.strip()
        self.ws.send(send_txt_msg(text_string=self.reply.strip(), wx_id=self.room_id if self.is_room else self.wx_id))


class NormalTask:
    def __init__(self, ws, prompt, reply, wx_id, room_id, is_room, is_citation):
        self.ws = ws
        self.prompt = prompt
        self.reply = reply
        self.wx_id = wx_id
        self.room_id = room_id
        self.is_room = is_room
        self.is_citation = is_citation

    def play(self):
        time.sleep(0.5)
        print("reply: " + self.reply)

        if self.is_citation:
            self.reply = self.prompt + "\n- - - - - - - - - -\n" + self.reply.strip()
        self.ws.send(send_txt_msg(text_string=self.reply.strip(), wx_id=self.room_id if self.is_room else self.wx_id))


class ImgTask:
    def __init__(self, ws, prompt, wx_id, room_id, is_room, version):
        self.ws = ws
        self.prompt = prompt
        self.wx_id = wx_id
        self.room_id = room_id
        self.is_room = is_room
        self.version = version
        self.img_ws = None

        if version == "2.1":
            self.img_host = "wss://" + API_URL_v21
        elif version == "1.5":
            self.img_host = "wss://" + API_URL_v15

    def on_open(self, img_ws):
        wssRq = {
            "session_hash": "".join(random.sample(string.ascii_lowercase + string.digits, 11)),
            "fn_index": 3
        }
        img_ws.send(json.dumps(wssRq))

    def on_message(self, img_ws, message):
        msg = json.loads(message)
        if msg["msg"] == "send_data":
            process = {
                "data": [self.prompt, "", 9],
                "fn_index": 3
            }
            img_ws.send(json.dumps(process))

        elif msg["msg"] == "process_starts":
            print(message)

        elif msg["msg"] == "process_completed":
            for item in msg["output"]["data"][0]:
                source_str = base64.urlsafe_b64decode(item[23:])
                filename = self.wx_id + "_" + self.room_id + "_" + getid() + ".jpg"
                if not os.path.exists(".cache/"):
                    os.makedirs(cache_dir)
                with open(cache_dir + filename, "wb") as file_object:
                    file_object.write(source_str)
                file_object.close()

                self.ws.send(send_pic_msg(wx_id=self.room_id if self.is_room else self.wx_id, content=os.path.join(os.path.abspath(cache_dir), filename)))
                time.sleep(1.0)
                if isCached:
                    print("Image cached! Name: " + cache_dir + filename)
                else:
                    os.remove(cache_dir + filename)

    def on_error(self, img_ws, error):
        print(error)

    def on_close(self, img_ws):
        print("Stable Diffusion V" + self.version + " arts are done!")

    def play(self):
        self.img_ws = websocket.WebSocketApp(self.img_host,
                                             on_open=self.on_open,
                                             on_message=self.on_message,
                                             on_error=self.on_error,
                                             on_close=self.on_close,
                                             )
        self.img_ws.keep_running = False
        self.img_ws.run_forever()
