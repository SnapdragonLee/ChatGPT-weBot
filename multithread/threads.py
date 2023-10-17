# -*- coding: utf-8 -*-

import threading
import queue

chat_que = queue.Queue()
nrm_que = queue.Queue()
img_que = queue.Queue()


class Processor(threading.Thread):

    def __init__(self, que):
        super(Processor, self).__init__()
        self.que: queue.Queue = que
        self.daemon = True
        self.start()

    def run(self):
        while True:
            item = self.que.get()

            item.play()
            del item
