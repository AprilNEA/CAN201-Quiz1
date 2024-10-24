import socket
import argparse
import random
import json


class GameServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
        self.clients = []  # [(address, name)]
        self.target_number = None
        self.current_player = 0

    def broadcast(self, message):
        """向所有客户端广播消息"""
        for client in self.clients:
            self.socket.sendto(json.dumps(message).encode(), client[0])

    def handle_new_client(self, address, data):
        """处理新客户端连接"""
        name = data.get('name')
        self.clients.append((address, name))
        print(f"Received name: {name}")

        # 通知所有客户端新玩家加入
        self.broadcast({
            'type': 'player_joined',
            'name': name,
            'message': f"{name} has joined the game!"
        })

        # 如果有两个玩家，开始游戏
        if len(self.clients) == 2:
            self.start_game()

    def start_game(self):
        """开始游戏"""
        self.target_number = random.randint(1, 100)
        print(f"Random number generated: {self.target_number}")

        self.broadcast({
            'type': 'game_start',
            'message': "Game started!"
        })

        # 提示第一个玩家猜数字
        self.prompt_next_player()

    def prompt_next_player(self):
        """提示下一个玩家"""
        current_client = self.clients[self.current_player]
        self.socket.sendto(
            json.dumps({
                'type': 'your_turn',
                'message': "Your turn to guess!"
            }).encode(),
            current_client[0]
        )

    def handle_guess(self, address, data):
        """处理玩家的猜测"""
        guess = int(data.get('guess'))
        current_player = self.clients[self.current_player][1]

        if guess == self.target_number:
            # 赢家产生
            self.broadcast({
                'type': 'game_over',
                'winner': current_player,
                'message': f"{current_player} wins! The number was {self.target_number}"
            })
        else:
            # 猜错了，广播结果并切换到下一个玩家
            result = "too high" if guess > self.target_number else "too low"
            self.broadcast({
                'type': 'guess_result',
                'player': current_player,
                'guess': guess,
                'result': result
            })

            self.current_player = (self.current_player + 1) % len(self.clients)
            self.prompt_next_player()

    def run(self):
        """运行服务器主循环"""
        print(f"Server started on {self.host}:{self.port}")

        while True:
            try:
                data, address = self.socket.recvfrom(1024)
                data = json.loads(data.decode())

                if data.get('type') == 'join':
                    self.handle_new_client(address, data)
                elif data.get('type') == 'guess':
                    self.handle_guess(address, data)
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', required=True)
    parser.add_argument('--port', type=int, required=True)
    args = parser.parse_args()

    server = GameServer(args.ip, args.port)
    server.run()
