"""
Standard ChatGPT
"""

from __future__ import annotations

import base64
import json
import time
import uuid

import os

import requests

from os.path import exists
from OpenAIAuth import Authenticator, Error as AuthError

# BASE_URL = "https://chatgpt.duti.tech/"
# BASE_URL = "https://apps.openai.com/"
BASE_URL = "https://bypass.duti.tech/"


class ErrorType:
    # define consts for the error codes
    USER_ERROR = -1
    UNKNOWN_ERROR = 0
    SERVER_ERROR = 1
    RATE_LIMIT_ERROR = 2
    INVALID_REQUEST_ERROR = 3
    EXPIRED_ACCESS_TOKEN_ERROR = 4
    INVALID_ACCESS_TOKEN_ERROR = 5
    PROHIBITED_CONCURRENT_QUERY_ERROR = 6
    AUTHENTICATION_ERROR = 7
    CLOUDFLARE_ERROR = 8


class Error(Exception):
    """
    Base class for exceptions in this module.
    Error codes:
    -1: User error
    0: Unknown error
    1: Server error
    2: Rate limit error
    3: Invalid request error
    4: Expired access token error
    5: Invalid access token error
    6: Prohibited concurrent query error
    """

    source: str
    message: str
    code: int

    def __init__(self, source: str, message: str, code: int = 0) -> None:
        self.source = source
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return f"{self.source}: {self.message} (code: {self.code})"

    def __repr__(self) -> str:
        return f"{self.source}: {self.message} (code: {self.code})"


class Chatbot:
    """
    Chatbot class for ChatGPT
    """

    def __init__(
            self,
            config,
            conversation_id=None,
            parent_id=None,
            session_client=None,
    ) -> None:

        """Initialize a chatbot
        Args:
            config (dict[str, str]): Login and proxy info. Example:
                {
                    "email": "OpenAI account email",
                    "password": "OpenAI account password",
                    "session_token": "<session_token>"
                    "access_token": "<access_token>"
                    "proxy": "<proxy_url_string>",
                    "paid": True/False, # whether this is a plus account
                }
                More details on these are available at https://github.com/acheong08/ChatGPT#configuration
            conversation_id (str | None, optional): Id of the conversation to continue on. Defaults to None.
            parent_id (str | None, optional): Id of the previous response message to continue on. Defaults to None.
            session_client (_type_, optional): _description_. Defaults to None.
        Raises:
            Exception: _description_
        """
        self.prompt = None
        self.config = config
        self.session = session_client() if session_client else requests.Session()

        if "proxy" in config:
            if isinstance(config["proxy"], str) is False:
                raise Exception("Proxy must be a string!")
            proxies = {
                "http": config["proxy"],
                "https": config["proxy"],
            }

            self.session.proxies.update(proxies)
        self.conversation_id = conversation_id
        self.parent_id = parent_id
        self.conversation_mapping = {}
        self.conversation_id_prev_queue = []
        self.parent_id_prev_queue = []
        self.prompt_prev_queue = []

        self.__check_credentials()

    def __check_credentials(self) -> None:
        """Check login info and perform login
        Any one of the following is sufficient for login. Multiple login info can be provided at the same time, and they
        will be used in the order listed below.
            - access_token
            - session_token
            - email + password
        Raises:
            Exception: _description_
            AuthError: _description_
        """
        if "access_token" in self.config:
            self.__set_access_token(self.config["access_token"])
        elif "session_token" in self.config:
            pass
        elif "email" not in self.config or "password" not in self.config:
            raise Exception("Insufficient login details provided!")
        if "access_token" not in self.config:
            try:
                self.login()
            except AuthError as error:
                raise error

    def __set_access_token(self, access_token: str) -> None:
        """Set access token in request header and self.config, then cache it to file.
        Args:
            access_token (str): access_token
        """
        self.session.headers.clear()
        self.session.headers.update(
            {
                "Accept": "text/event-stream",
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-Openai-Assistant-App-Id": "",
                "Connection": "close",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://chat.openai.com/chat",
            },
        )
        self.session.cookies.update(
            {
                "library": "revChatGPT",
            },
        )

        self.config["access_token"] = access_token

        email = self.config.get("email", None)
        if email is not None:
            self.__cache_access_token(email, access_token)

    def __get_cached_access_token(self, email: str | None) -> str | None:
        """Read access token from cache
        Args:
            email (str | None): email of the account to get access token
        Raises:
            Error: _description_
            Error: _description_
            Error: _description_
        Returns:
            str | None: access token string or None if not found
        """
        email = email or "default"
        cache = self.__read_cache()
        access_token = cache.get("access_tokens", {}).get(email, None)

        # Parse access_token as JWT
        if access_token is not None:
            try:
                # Split access_token into 3 parts
                s_access_token = access_token.split(".")
                # Add padding to the middle part
                s_access_token[1] += "=" * ((4 - len(s_access_token[1]) % 4) % 4)
                d_access_token = base64.b64decode(s_access_token[1])
                d_access_token = json.loads(d_access_token)
            except base64.binascii.Error:
                raise Error(
                    source="__get_cached_access_token",
                    message="Invalid access token",
                    code=ErrorType.INVALID_ACCESS_TOKEN_ERROR,
                ) from None
            except json.JSONDecodeError:
                raise Error(
                    source="__get_cached_access_token",
                    message="Invalid access token",
                    code=ErrorType.INVALID_ACCESS_TOKEN_ERROR,
                ) from None

            exp = d_access_token.get("exp", None)
            if exp is not None and exp < time.time():
                raise Error(
                    source="__get_cached_access_token",
                    message="Access token expired",
                    code=ErrorType.EXPIRED_ACCESS_TOKEN_ERROR,
                )

        return access_token

    def __cache_access_token(self, email: str, access_token: str) -> None:
        """Write an access token to cache
        Args:
            email (str): account email
            access_token (str): account access token
        """
        email = email or "default"
        cache = self.__read_cache()
        if "access_tokens" not in cache:
            cache["access_tokens"] = {}
        cache["access_tokens"][email] = access_token
        self.__write_cache(cache)

    def __write_cache(self, info: dict) -> None:
        """Write cache info to file
        Args:
            info (dict): cache info, current format
            {
                "access_tokens":{"someone@example.com": 'this account's access token', }
            }
        """
        dirname = os.path.dirname(self.cache_path) or "."
        os.makedirs(dirname, exist_ok=True)
        json.dump(info, open(self.cache_path, "w", encoding="utf-8"), indent=4)

    def __read_cache(self):
        try:
            cached = json.load(open(self.cache_path, encoding="utf-8"))
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            cached = {}
        return cached

    def login(self):
        if (
                "email" not in self.config or "password" not in self.config
        ) and "session_token" not in self.config:
            raise Exception("Insufficient login details provided!")
        auth = Authenticator(
            email_address=self.config.get("email"),
            password=self.config.get("password"),
            proxy=self.config.get("proxy"),
        )
        if self.config.get("session_token"):
            auth.session_token = self.config["session_token"]
            auth.get_access_token()
            if auth.access_token is None:
                del self.config["session_token"]
                self.login()
                return
        else:
            auth.begin()
            self.config["session_token"] = auth.session_token
            auth.get_access_token()

        self.__set_access_token(auth.access_token)

    def ask(
            self,
            prompt: str,
            conversation_id: str | None = None,
            parent_id: str | None = None,
            timeout: float = 360,
    ):
        """Ask a question to the chatbot
        Args:
            prompt (str): The question
            conversation_id (str | None, optional): UUID for the conversation to continue on. Defaults to None.
            parent_id (str | None, optional): UUID for the message to continue on. Defaults to None.
            timeout (float, optional): Timeout for getting the full response, unit is second. Defaults to 360.
        Raises:
            Error: _description_
            Exception: _description_
            Error: _description_
            Error: _description_
            Error: _description_
        Yields:
            _type_: _description_
        """
        if prompt is not None:
            self.prompt = prompt
        if parent_id is not None and conversation_id is None:
            raise Error(
                source="User",
                message="conversation_id must be set once parent_id is set",
                code=ErrorType.USER_ERROR,
            )

        if conversation_id is not None and conversation_id != self.conversation_id:
            self.parent_id = None

        conversation_id = conversation_id or self.conversation_id
        parent_id = parent_id or self.parent_id
        if conversation_id is None and parent_id is None:
            parent_id = str(uuid.uuid4())

        if conversation_id is not None and parent_id is None:
            if conversation_id not in self.conversation_mapping:
                self.__map_conversations()
            parent_id = self.conversation_mapping[conversation_id]
        data = {
            "action": "next",
            "messages": [
                {
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": {"content_type": "text", "parts": [prompt]},
                },
            ],
            "conversation_id": conversation_id,
            "parent_message_id": parent_id,
            "model": "text-davinci-002-render-paid"
            if self.config.get("paid")
            else "text-davinci-002-render-sha",
        }

        self.conversation_id_prev_queue.append(data["conversation_id"], )
        self.parent_id_prev_queue.append(data["parent_message_id"])
        self.prompt_prev_queue.append(self.prompt)

        response = self.session.post(
            url=BASE_URL + "api/conversation",
            data=json.dumps(data),
            timeout=timeout,
        )
        self.__check_response(response)
        for line in response.iter_lines(chunk_size=4096):
            # remove b' and ' at the beginning and end and ignore case
            line = str(line)[2:-1]
            if line.lower() == "internal server error":
                raise Error(
                    source="ask",
                    message="Internal Server Error",
                    code=ErrorType.SERVER_ERROR,
                )
            if line == "" or line is None:
                continue
            if "data: " in line:
                line = line[6:]
            if line == "[DONE]":
                break

            line = line.replace('\\"', '"')
            line = line.replace("\\'", "'")
            line = line.replace("\\\\", "\\")

            try:
                line = json.loads(line)
            except json.decoder.JSONDecodeError:
                continue
            if not self.__check_fields(line) or response.status_code != 200:
                if response.status_code == 401:
                    raise Error(
                        source="ask",
                        message="Permission denied",
                        code=ErrorType.AUTHENTICATION_ERROR,
                    )
                if response.status_code == 403:
                    raise Error(
                        source="ask",
                        message="Cloudflare triggered a 403 error",
                        code=ErrorType.CLOUDFLARE_ERROR,
                    )
                if response.status_code == 429:
                    raise Error(
                        source="ask",
                        message="Rate limit exceeded",
                        code=ErrorType.RATE_LIMIT_ERROR,
                    )
                raise Error(
                    source="ask",
                    message=line,
                    code=ErrorType.SERVER_ERROR,
                )

            if line["message"]["author"]["role"] != "assistant":
                continue
            message = line["message"]["content"]["parts"][0]
            conversation_id = line["conversation_id"]
            parent_id = line["message"]["id"]
            try:
                model = line["message"]["metadata"]["model_slug"]
            except KeyError:
                model = None
            yield {
                "message": message,
                "conversation_id": conversation_id,
                "parent_id": parent_id,
                "model": model,
            }
        self.conversation_mapping[conversation_id] = parent_id
        if parent_id is not None:
            self.parent_id = parent_id
        if conversation_id is not None:
            self.conversation_id = conversation_id

    def __check_fields(self, data: dict) -> bool:
        try:
            data["message"]["content"]
        except (TypeError, KeyError):
            return False
        return True

    def __check_response(self, response: requests.Response) -> None:
        """Make sure response is success
        Args:
            response (_type_): _description_
        Raises:
            Error: _description_
        """
        if response.status_code != 200:
            print(response.text)
            raise Error(
                source="OpenAI",
                message=response.text,
                code=response.status_code,
            )

    def get_conversations(
            self,
            offset: int = 0,
            limit: int = 20,
            encoding: str | None = None,
    ):
        """
        Get conversations
        :param offset: Integer
        :param limit: Integer
        """
        url = BASE_URL + f"api/conversations?offset={offset}&limit={limit}"
        response = self.session.get(url)
        self.__check_response(response)
        if encoding is not None:
            response.encoding = encoding
        data = json.loads(response.text)
        return data["items"]

    def get_msg_history(self, convo_id: str, encoding: str | None = None):
        """
        Get message history
        :param convo_id: UUID of conversation
        :param encoding: String
        """
        url = BASE_URL + f"api/conversation/{convo_id}"
        response = self.session.get(url)
        self.__check_response(response)
        if encoding is not None:
            response.encoding = encoding
        return json.loads(response.text)

    def gen_title(self, convo_id: str, message_id: str) -> None:
        """
        Generate title for conversation
        """
        url = BASE_URL + f"api/conversation/gen_title/{convo_id}"
        response = self.session.post(
            url,
            data=json.dumps(
                {"message_id": message_id, "model": "text-davinci-002-render"},
            ),
        )
        self.__check_response(response)

    def change_title(self, convo_id: str, title: str) -> None:
        """
        Change title of conversation
        :param convo_id: UUID of conversation
        :param title: String
        """
        url = BASE_URL + f"api/conversation/{convo_id}"
        response = self.session.patch(url, data=json.dumps({"title": title}))
        self.__check_response(response)

    def delete_conversation(self, convo_id: str) -> None:
        """
        Delete conversation
        :param convo_id: UUID of conversation
        """
        url = BASE_URL + f"api/conversation/{convo_id}"
        response = self.session.patch(url, data='{"is_visible": false}')
        self.__check_response(response)

    def clear_conversations(self) -> None:
        """
        Delete all conversations
        """
        url = BASE_URL + "api/conversations"
        response = self.session.patch(url, data='{"is_visible": false}')
        self.__check_response(response)

    def __map_conversations(self):
        conversations = self.get_conversations()
        histories = [self.get_msg_history(x["id"]) for x in conversations]
        for x, y in zip(conversations, histories):
            self.conversation_mapping[x["id"]] = y["current_node"]

    def reset_chat(self) -> None:
        """
        Reset the conversation ID and parent ID.
        :return: None
        """
        self.conversation_id = None
        self.parent_id = str(uuid.uuid4())

    def rollback_conversation(self, num: int = 1) -> None:
        """
        Rollback the conversation.
        :param num: Integer. The number of messages to rollback
        :return: None
        """
        for _ in range(num):
            self.conversation_id = self.conversation_id_prev_queue.pop()
            self.parent_id = self.parent_id_prev_queue.pop()
            self.prompt_prev_queue.pop()

            self.prompt = self.prompt_prev_queue[-1] if len(self.prompt_prev_queue) > 0 else None


def get_input(prompt):
    """
    Multiline input function.
    """
    print(prompt, end="")

    lines = []

    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    user_input = "\n".join(lines)

    return user_input


def configure():
    """
    Looks for a config file in the following locations:
    """
    config_files = [f".config/rev_config.json"]

    config_file = next((f for f in config_files if exists(f)), None)
    if config_file:
        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)
    else:
        print("No config file found.")
        raise Exception("No config file found.")
    return config


def main(config: dict):
    """
    Main function for the chatGPT program.
    """
    print("Logging in...")
    chatbot = Chatbot(
        config,
        conversation_id=config.get("conversation_id"),
        parent_id=config.get("parent_id"),
    )

    def handle_commands(command: str) -> bool:
        if command == "!help":
            print(
                """
            !help - Show this message
            !reset - Forget the current conversation
            !config - Show the current configuration
            !rollback x - Rollback the conversation (x being the number of messages to rollback)
            !exit - Exit this program
            !setconversation - Changes the conversation
            """,
            )
        elif command == "!reset":
            chatbot.reset_chat()
            print("Chat session successfully reset.")
        elif command == "!config":
            print(json.dumps(chatbot.config, indent=4))
        elif command.startswith("!rollback"):
            try:
                rollback = int(command.split(" ")[1])
            except IndexError:
                rollback = 1
            chatbot.rollback_conversation(rollback)
            print(f"Rolled back {rollback} messages.")
        elif command.startswith("!setconversation"):
            try:
                chatbot.conversation_id = chatbot.config["conversation_id"] = command.split(" ")[1]
                print("Conversation has been changed")
            except IndexError:
                print("Please include conversation UUID in command")
        elif command == "!exit":
            exit(0)
        else:
            return False
        return True

    while True:
        prompt = get_input("\nYou:\n")
        if prompt.startswith("!"):
            if handle_commands(prompt):
                continue

        print("Chatbot: ")
        prev_text = ""
        for data in chatbot.ask(
                prompt,
        ):
            message = data["message"][len(prev_text):]
            print(message, end="", flush=True)
            prev_text = data["message"]
        print()
        # print(message["message"])


if __name__ == "__main__":
    print(
        """
        ChatGPT - A command-line interface to OpenAI's ChatGPT (https://chat.openai.com/chat)
        Repo: github.com/acheong08/ChatGPT
        """,
    )
    print("Type '!help' to show a full list of commands")
    print("Press enter twice to submit your question.\n")
    main(configure())
