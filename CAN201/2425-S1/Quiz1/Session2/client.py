import socket
import argparse
import json
import threading

class ProximityGameClient:
    def __init__(self, server_host: str, server_port: int):
        self.server_address = (server_host, server_port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.name = None
        self.last_guess = None
        
    def send_to_server(self, message: dict):
        """发送消息到服务器"""
        self.socket.sendto(json.dumps(message).encode(), self.server_address)
        
    def receive_messages(self):
        """接收服务器消息的线程"""
        while True:
            try:
                data, _ = self.socket.recvfrom(1024)
                message = json.loads(data.decode())
                
                if message.get('type') == 'player_joined':
                    print(message['message'])
                    
                elif message.get('type') == 'game_start':
                    print("\nGame started!")
                    guess = input("Enter your first guess (1-100): ")
                    self.last_guess = int(guess)
                    self.send_to_server({
                        'type': 'guess',
                        'guess': int(guess)
                    })
                    
                elif message.get('type') == 'your_turn':
                    print("\nYour turn to guess!")
                    print(f"Your last guess was: {self.last_guess}")
                    guess = input("Enter your guess (1-100): ")
                    self.last_guess = int(guess)
                    self.send_to_server({
                        'type': 'guess',
                        'guess': int(guess)
                    })
                    
                elif message.get('type') == 'guess_result':
                    player = message['player']
                    guess = message['guess']
                    difference = message['difference']
                    if player != self.name:
                        print(f"\n{player} guessed {guess}. Difference: {difference}")
                    else:
                        print(f"\nYour guess was {guess}. Difference: {difference}")
                        
                elif message.get('type') == 'game_over':
                    print(f"\n{message['message']}")
                    return
                    
            except Exception as e:
                print(f"Error: {e}")
                break
                
    def start(self):
        """启动客户端"""
        print(f"Connecting to server at {self.server_address[0]}:{self.server_address[1]}")
        
        # 获取玩家名称
        self.name = input("Enter your name: ")
        
        # 发送加入游戏请求
        self.send_to_server({
            'type': 'join',
            'name': self.name
        })
        
        # 启动接收消息的线程
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()
        
        print("Waiting for other players...")
        receive_thread.join()
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', required=True)
    parser.add_argument('--port', type=int, required=True)
    args = parser.parse_args()
    
    client = ProximityGameClient(args.ip, args.port)
    client.start()