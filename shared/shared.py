# -*- coding: utf-8 -*-

from .signal import *
from .config import *
from .server import *

import time


def get_time():
    t = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    return t
