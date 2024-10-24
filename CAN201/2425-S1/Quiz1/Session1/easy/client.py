import socket
import argparse
import json
import threading

def send_to_server(socket, message, server_address):
    """发送消息到服务器"""
    socket.sendto(json.dumps(message).encode(), server_address)

def receive_messages(socket, server_address, name):
    """接收服务器消息的线程"""
    while True:
        try:
            data, _ = socket.recvfrom(1024)
            message = json.loads(data.decode())

            if message.get('type') == 'player_joined':
                print(message['message'])
                
            elif message.get('type') == 'game_start':
                print("Game started!")
                
            elif message.get('type') == 'your_turn':
                print("\nYour turn to guess!")
                guess = input("Enter your guess (1-100): ")
                send_to_server(socket, {
                    'type': 'guess',
                    'guess': int(guess)
                }, server_address)
                
            elif message.get('type') == 'guess_result':
                player = message['player']
                guess = message['guess']
                result = message['result']
                if player != name:
                    print(f"\n{player} guessed {guess}. The guess was {result}.")
                else:
                    print(f"\nYour guess was {result}.")
                    
            elif message.get('type') == 'game_over':
                print(f"\n{message['message']}")
                return
                
        except Exception as e:
            print(f"Error: {e}")
            break

def start_client(server_host, server_port):
    """启动客户端"""
    server_address = (server_host, server_port)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print(f"Connecting to server at {server_host}:{server_port}")
    
    # 获取玩家名称
    name = input("Enter your name: ")
    
    # 发送加入游戏请求
    send_to_server(client_socket, {
        'type': 'join',
        'name': name
    }, server_address)
    
    # 启动接收消息的线程
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, server_address, name))
    receive_thread.start()
    
    print("Waiting for other players...")
    receive_thread.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', required=True)
    parser.add_argument('--port', type=int, required=True)
    args = parser.parse_args()
    
    start_client(args.ip, args.port)