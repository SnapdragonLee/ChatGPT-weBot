import json
import websocket

from client.wxclient import on_open, on_message, on_error, on_close, config

SERVER = "ws://" + config["server_host"]

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(SERVER,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever(ping_interval=60)
