### 配置详细指引



###### api_config.json

```json
{
  // OpenAI 账户构建的 API_KEY
  "api_key": "",
  // 需要的模型名称
  "engine": "gpt-3.5-turbo",
  // 最大可接受提问 token（1~4096）
  "max_tokens": 3600,
  // 控制结果随机性（0.0~2.0），0.0 表示结果固定，2.0 表示结果随机
  "temperature": 0.7,
  // 使用温度采样的替代方法称为核心采样，可以采取默认
  "top_p": 1.0,
  // 主题贴合度惩罚（-2.0~2.0），正值会根据到目前为止是否出现在文本中来惩罚新标记，从而增加模型谈论新主题的可能性
  "presence_penalty": 0.0,
  // 频率惩罚（-2.0~2.0），正值会根据新标记在文本中的现有频率对其进行惩罚，从而降低模型逐字重复同一行的可能性
  "frequency_penalty": 0.0,
  // 获得的回答数
  "reply_count": 1,
  // 机器人默认扮演的角色
  "system_character": "You are ChatGPT, a large language model trained by OpenAI. Respond conversationally",

  // 可选填写 http 或 https 代理
  "proxy": ""
}
```

***1. `engine` 对应的值需要为其中之一：`gpt-3.5-turbo`, `gpt-3.5-turbo-0301`, `gpt-4`,  `gpt-4-0314`, `gpt-4-32k`, `gpt-4-32k-0314` 。***

***2. 请不要更改 `reply_count`。***



------

###### config.json

```json
{
  // 是否开启 ChatGPT 自动回复
  "autoReply": true,
    
  // 在回复时，查询联网信息 (WebChatGPT) 辅助回答
  "internetKey": "-o",
  // 联网信息条数 (1~10)
  "internetResult": 3,
  
  // 在群聊中设置唤醒机器人关键词
  "groupChatKey": "-c",
  // 在群聊中响应回复
  "grpReplyMode": true,
  // 在群聊回答前添加源问题格式
  "grpCitationMode": true,
  // 在私聊中设置唤醒机器人关键词
  "privateChatKey": "-c",
  // 在私聊中响应回复
  "prvReplyMode": true,
  // 在私聊回答前添加源问题格式
  "prvCitationMode": false,
  // 激活机器人扮演角色关键词
  "characterKey": "-p",
  // 总结对话并缩减 token
  "conclusionKey": "-z",

  // 是否开启 Stable Diffusion 图片回复（仅英语）
  "stableDiffRly": true,
  // 在群聊中设置唤醒 AI画图功能关键词
  "groupImgKey": "-i",
  // 在私聊中设置唤醒 AI画图功能关键词
  "privateImgKey": "-i",
  // 接入负语句关键词
  "negativePromptKey": "-n",
  // 是否开启图片缓存（开启后会在 .cache 文件夹中缓存）
  "isCached": true,

  // 查看可用命令帮助
  "helpKey": "-h",
  // 设置重置上下文关键词
  "resetChatKey": "-rs",
  // 设置重新生成答案关键词
  "regenerateKey": "-rg",
  // 设置回滚到以前的n个问题关键词
  "rollbackKey": "-rb"
}
```

***1. 联网查询信息功能（WebChatGPT）示例为：`-c -o 流浪地球2故事简介` 即可触发联网信息辅助问答。***

***2. 接入负反馈语句关键词功能示例为：`-i skylines, 4k, concept arts -n no girl, no body` 即可将 `skylines, 4k, concept arts` 作为正提示， `no girl, no body` 作为负提示输入给 stable Diffusion。***



------

###### rev_config.json

暂时弃用，无需设置



------

###### server_config.json

```json
{
  // 本地host运行地址（仅本地）
  "server_host": "127.0.0.1:5555",
}
```



------

###### sys_character.json

```json
{
  // "键": "值", (格式需匹配)
  "Linux Terminal": "I want you to act as a linux terminal. I will type commands and you will reply with what the terminal should show. I want you to only reply with the terminal output inside one unique code block, and nothing else. do not write explanations. do not type commands unless I instruct you to do so. when i need to tell you something in english, i will do so by putting text inside curly brackets {like this}. my first command is pwd",
  .
  .
  .
}
```

这个文件用于存放自定义机器人可扮演的所有角色（注意自定义角色名不允许两侧包含空字符，激活时角色名两侧可以有空字符）。

注意！如果想要激活它，需要用自定义指令，且激活的角色在该配置文件中存在。例如按照默认配置，在聊天框中使用命令 "-pLinux Terminal" 或 "-p  Linux Terminal   	"，均可激活 `Linux Terminal` 对应的值作为机器人扮演的角色。

