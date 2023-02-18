import json
import websocket

from client.wxclient import on_open, on_message, on_error, on_close


with open('.config/rev_config.json', encoding="utf-8") as f:
    revConfig = json.load(f)

with open('.config/oth_config.json', encoding="utf-8") as f:
    serverConfig = json.load(f)

SERVER = "ws://" + serverConfig["server_host"]

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(SERVER,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()
