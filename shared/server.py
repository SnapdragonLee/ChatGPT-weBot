# -*- coding: utf-8 -*-

import json

# ws server config
with open('.config/server_config.json', encoding='utf-8') as f:
    config = json.load(f)
f.close()
server_host = config['server_host']

# stable_diff server config
API_URL_v21 = 'stabilityai-stable-diffusion.hf.space/queue/join'
API_URL_v15 = ''
cache_dir = '.cache/'
