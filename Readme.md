<h1 align="center">ChatGPT-weBot</h1>



Using ChatGPT-weBot based on ChatGPT(Non-API key call) and official WeChat hook interface. [中文文档](./Readme_ZH.md) | English

<div align="center"> <img src="assets/DALL·E  - A robot is working hard to transform, modify, and revolutionize the WeChat software.png" width="50%"> </div>

###### Author

[Snapdragon Lee (github.com)](https://github.com/SnapdragonLee) 

*cover created from [DALL·E2 (openai.com)](https://labs.openai.com/)*



## Support & Features

- [x] Support conversation.
- [x] Support context-aware question answering
- [x] **Never get banned by using official WeChat execution.**
- [x] Set the keywords to wake up the WeChat robot in private.
- [x] Set the keywords to wake up the WeChat robot in the group. **(have bugs)**
- [x] Support replying message when mentioning your bot in the group. **(have bugs)**
- [ ] Get help doc in line. **(need work)**
- [ ] Can set keywords to reset the previous conversation. **(need work)**
- [ ] Regenerate to get another answer. **(need work)**
- [ ] Rollback conversation. **(need work)**
- [ ] Other





## Default configs

```
{
  // Setting host running locally (only local)
  "server_host": "127.0.0.1:5555",

  // Whether to enable ChatGPT auto-reply function
  "autoReply": true,
  // Setting keyword to wake up bot in group chat
  "groupChatKey": "-c",
  // Using reply mode in group chat
  "groupReplyMode": false,
  // Setting keyword to wake up bot in private chat
  "privateChatKey": "-c",
  // Using reply mode in private chat
  "privateReplyMode": true,

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





## Step to Start

1. Install all packages listed in `requirements.txt` , use the command like:

   ```
   pip install -r ./requirements.txt
   ```

   

2. Download package from Github Releases.

3. Install `WeChat-3.6.0.18.exe` on your computer, **if your version is higher than 3.6.0.18, you can downgrade instantly.** Then get your account online.

   

4. Monitoring WeChat message by running a server. Here are two methods to achieve this, **please *choose 1 method*** :

   - Using injector named `DLLinjector_V1.0.3.exe`, then choose file named `3.6.0.18-0.0.0.008.dll` to inject.

     ![image-20230221044543472](assets/image-20230221044543472.png)

     

   - Running `funtool_3.6.0.18-1.0.0013.exe` , and press `Start` .

     ![image-20230221044609319](assets/image-20230221044609319.png)

   

5. The last step is fill json files listed in `.config/` . 

   - In `config.json` ,  you need to configure your custom options based on your preferences.

   - In `rev_config.json` , you need to fill your ChatGPT login information by *choosing 1 method*: 

     - Email/Password **(Not supported for Google/Microsoft accounts)**

     - session_token **(supported for Google/Microsoft accounts)**

       > 1. Go to [`chat.openai.com/chat`](https://chat.openai.com/chat) and log in or sign up.
       > 2. Press `F12` to open dev tools.
       > 3. Copy cookies as `__Secure-next-auth.session-token` .

     

6. Run `main.py` by using command:

   ```
   python main.py
   ```

   **Everything is ready, feel free to go online with your ChatGPT-weBot !** 
   
   No limitation, No usage counting, and no payment needed.





## Q&A

1. How to get all response? You can say "continue" in your language.
2. Have problems? Feel free to create an issue.



###### Reference

- [AutumnWhj/ChatGPT-wechat-bot: ChatGPT for wechat](https://github.com/AutumnWhj/ChatGPT-wechat-bot)
- [cixingguangming55555/wechat-bot: 带二次开发接口的PC微信聊天机器人](https://github.com/cixingguangming55555/wechat-bot)