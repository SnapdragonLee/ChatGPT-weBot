# Detailed Configs Guide



###### api_config.json

```json
{
  // OpenAI Account API_KEY
  "api_key": "",
  // ID of the model to use
  "engine": "gpt-3.5-turbo",
  // The maximum number of tokens to generate in the completion (1~4096)
  "max_tokens": 3600,
  // Control the randomness of the result (0.0~2.0), Higher values will make the output more random, while lower values will make it more focused and deterministic
  "temperature": 0.7,
  // An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass
  "top_p": 1.0,
  // Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics (-2.0~2.0)
  "presence_penalty": 0.0,
  // Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim (-2.0~2.0)
  "frequency_penalty": 0.0,
  // How many reply to generate for each prompt
  "reply_count": 1,
  // The character played by bot by default
  "system_character": "You are ChatGPT, a large language model trained by OpenAI. Respond conversationally",

  // Optional proxy of http or https
  "proxy": ""
}
```

***1. `engine` corresponding to one of the value from：`gpt-3.5-turbo`, `gpt-3.5-turbo-0301`, `gpt-4`,  `gpt-4-0314`, `gpt-4-32k`, `gpt-4-32k-0314` 。***

***2. Please do not modify `reply_count`。***



------

###### config.json

```json
{
  // Whether to enable ChatGPT auto-reply function
  "autoReply": true,
    
  // Setting keyword to start up WebChatGPT
  "internetKey": "-o",
  // The number of searching result (1~10)
  "internetResult": 3,
    
  // Setting keyword to wake up bot in group chat
  "groupChatKey": "-c",
  // Using reply mode in group chat
  "grpReplyMode": false,
  // Origin question quote on head of answer in group chat
  "grpCitationMode": true,
  // Setting keyword to wake up bot in private chat
  "privateChatKey": "-c",
  // Using reply mode in private chat
  "prvReplyMode": true,
  // Origin question quote on head of answer in private chat
  "prvCitationMode": false,
  // Setting keyword to activate the role-playing of bot
  "characterKey": "-p",
  // Conclude and reduce token
  "conclusionKey": "-z",
  
  // Whether to enable Stable Diffusion AI drawing function (English Only)
  "stableDiffRly": true,
  // Setting keyword to wake up AI drawing function in group chat
  "groupImgKey": "-i",
  // Setting keyword to wake up AI drawing function in private chat
  "privateImgKey": "-i",
  // SSetting keyword to add negative prompt
  "negativePromptKey": "-n",
  // Whether to enable image caching (it will be cached in .cache folder)
  "isCached": true,

  // View available command help
  "helpKey": "-h",
  // Setting keyword to reset context
  "resetChatKey": "-rs",
  // Setting keyword to regenerate previous answer
  "regenerateKey": "-rg",
  // Setting keyword to roll back to previous n questions
  "rollbackKey": "-rb"
}
```

***1. The example of the WebChatGPT is: `-c -o Wandering Earth 2 story introduction`, which can trigger the online information to assist the answer.***

***2. The example of the function of accessing negative prompt sentences is: `-i skylines, 4k, concept arts -n no girl, no body`, which can use `skylines, 4k, concept arts` as a positive prompt, and `no girl, no body` as a negative prompt to stable Diffusion.***



------

###### rev_config.json

Temporarily deprecated.



------

###### server_config.json

```json
{
  // Setting host running locally (local only)
  "server_host": "127.0.0.1:5555",
}
```



------

###### sys_character.json

```json
{
  // "Key": "Value", (Format needs to match)
  "Linux Terminal": "I want you to act as a linux terminal. I will type commands and you will reply with what the terminal should show. I want you to only reply with the terminal output inside one unique code block, and nothing else. do not write explanations. do not type commands unless I instruct you to do so. when i need to tell you something in english, i will do so by putting text inside curly brackets {like this}. my first command is pwd",
  .
  .
  .
}
```

This file is used to store all the custom characters that the bot can play (note that the custom character name does not allow empty characters on both sides, and there can be empty characters on both sides of the character name when activated). 

Notice! If you want to activate it, you need to use a custom order, and the activated character exists in the configuration file. For example, according to the default configuration, use the command "-pLinux Terminal" or "-p Linux Terminal  	" in chat to activate the value corresponding to `Linux Terminal` as the role played by bot.

