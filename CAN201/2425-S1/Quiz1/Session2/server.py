import socket
import argparse
import random
import json
from typing import Dict, Tuple, List

class ProximityGameServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
        
        # 游戏状态
        self.target_number = None
        self.clients: List[Tuple] = []  # [(address, name)]
        self.guesses: Dict[str, int] = {}  # {name: last_guess}
        self.differences: Dict[str, int] = {}  # {name: difference}
        self.current_closest = None  # 当前最接近的玩家名字
        self.game_started = False
        self.first_round = True
        self.received_first_guesses = 0
        
    def calculate_difference(self, guess: int) -> int:
        """计算猜测值与目标值的差值"""
        return abs(guess - self.target_number)
    
    def find_closest_player(self) -> str:
        """找出猜测最接近的玩家"""
        return min(self.differences.items(), key=lambda x: x[1])[0]
    
    def broadcast(self, message: Dict):
        """向所有客户端广播消息"""
        for client in self.clients:
            self.socket.sendto(json.dumps(message).encode(), client[0])
            
    def handle_new_client(self, address: Tuple, data: Dict):
        """处理新客户端连接"""
        name = data.get('name')
        self.clients.append((address, name))
        print(f"Received name: {name}")
        
        self.broadcast({
            'type': 'player_joined',
            'name': name,
            'message': f"{name} has joined the game!"
        })
        
        # 当有两个玩家时开始游戏
        if len(self.clients) == 2:
            self.start_game()
            
    def start_game(self):
        """开始游戏"""
        self.target_number = random.randint(1, 100)
        self.game_started = True
        print(f"Random number generated: {self.target_number}")
        
        # 请求所有玩家进行首次猜测
        self.broadcast({
            'type': 'game_start',
            'message': "Game started! Everyone make your first guess!"
        })
        
    def handle_guess(self, address: Tuple, data: Dict):
        """处理玩家的猜测"""
        guess = int(data.get('guess'))
        current_player = next(name for addr, name in self.clients if addr == address)
        
        # 记录猜测
        self.guesses[current_player] = guess
        difference = self.calculate_difference(guess)
        self.differences[current_player] = difference
        
        if self.first_round:
            self.received_first_guesses += 1
            if self.received_first_guesses == len(self.clients):
                self.first_round = False
                self.current_closest = self.find_closest_player()
                
        # 检查是否猜中
        if guess == self.target_number:
            self.broadcast({
                'type': 'game_over',
                'winner': current_player,
                'message': f"{current_player} wins! The number was {self.target_number}"
            })
            return
            
        # 广播猜测结果
        self.broadcast({
            'type': 'guess_result',
            'player': current_player,
            'guess': guess,
            'difference': difference,
            'message': f"{current_player} guessed {guess}, which is {'too high' if guess > self.target_number else 'too low'}"
        })
        
        if not self.first_round:
            # 判断是否应该保持猜测权
            if current_player == self.current_closest:
                # 如果当前玩家没有比之前更接近，切换玩家
                prev_difference = min(self.differences.values())
                if difference > prev_difference:
                    other_player = next(name for name in self.differences.keys() if name != current_player)
                    self.current_closest = other_player
                    
            # 通知下一个猜测的玩家
            next_player = self.current_closest
            self.socket.sendto(
                json.dumps({
                    'type': 'your_turn',
                    'message': "Your turn to guess!"
                }).encode(),
                next(addr for addr, name in self.clients if name == next_player)
            )
            
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
    
    server = ProximityGameServer(args.ip, args.port)
    server.run()