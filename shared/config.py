# -*- coding: utf-8 -*-

import json

# api model check
with open('.config/api_config.json', encoding='utf-8') as f:
    api_config = json.load(f)
f.close()

if api_config['engine'] not in [
    'gpt-3.5-turbo',
    'gpt-3.5-turbo-0301',
    'gpt-3.5-turbo-16k',
    'gpt-3.5-turbo-0613',
    'gpt-3.5-turbo-16k-0613',
    'gpt-4',
    'gpt-4-0314',
    'gpt-4-32k',
    'gpt-4-32k-0314',
    'gpt-4-0613',
    'gpt-4-32k-0613',
]:
    error = NotImplementedError('Unsupported engine {self.engine}')
    raise error

# general config
with open('.config/config.json', encoding='utf-8') as f:
    config = json.load(f)
f.close()

autoReply = config['autoReply']

internetKey = config['internetKey']
internetResult = config['internetResult']

groupChatKey = config['groupChatKey']
grpReplyMode = config['grpReplyMode']
grpCitationMode = config['grpCitationMode']
privateChatKey = config['privateChatKey']
prvReplyMode = config['prvReplyMode']
prvCitationMode = config['prvCitationMode']
characterKey = config['characterKey']
conclusionKey = config['conclusionKey']

stableDiffRly = config['stableDiffRly']
groupImgKey = config['groupImgKey']
privateImgKey = config['privateImgKey']
negativePromptKey = config['negativePromptKey']
isCached = config['isCached']

helpKey = config['helpKey']
resetChatKey = config['resetChatKey']
regenerateKey = config['regenerateKey']
rollbackKey = config['rollbackKey']