from client.wxclient import ws

if __name__ == "__main__":
    ws.run_forever(ping_interval=10)
