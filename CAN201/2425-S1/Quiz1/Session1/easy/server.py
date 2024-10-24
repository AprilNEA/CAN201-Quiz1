import socket
import argparse
import random
import json

clients = []  # [(address, name)]
target_number = None
current_player = 0
server_socket = None

def broadcast(message):
    """向所有客户端广播消息"""
    for client in clients:
        server_socket.sendto(json.dumps(message).encode(), client[0])

def handle_new_client(address, data):
    """处理新客户端连接"""
    name = data.get('name')
    clients.append((address, name))
    print(f"Received name: {name}")

    # 通知所有客户端新玩家加入
    broadcast({
        'type': 'player_joined',
        'name': name,
        'message': f"{name} has joined the game!"
    })

    # 如果有两个玩家，开始游戏
    if len(clients) == 2:
        start_game()

def start_game():
    """开始游戏"""
    global target_number
    target_number = random.randint(1, 100)
    print(f"Random number generated: {target_number}")

    broadcast({
        'type': 'game_start',
        'message': "Game started!"
    })

    # 提示第一个玩家猜数字
    prompt_next_player()

def prompt_next_player():
    """提示下一个玩家"""
    current_client = clients[current_player]
    server_socket.sendto(
        json.dumps({
            'type': 'your_turn',
            'message': "Your turn to guess!"
        }).encode(),
        current_client[0]
    )

def handle_guess(address, data):
    """处理玩家的猜测"""
    global current_player
    guess = int(data.get('guess'))
    current_player_name = clients[current_player][1]

    if guess == target_number:
        # 赢家产生
        broadcast({
            'type': 'game_over',
            'winner': current_player_name,
            'message': f"{current_player_name} wins! The number was {target_number}"
        })
    else:
        # 猜错了，广播结果并切换到下一个玩家
        result = "too high" if guess > target_number else "too low"
        broadcast({
            'type': 'guess_result',
            'player': current_player_name,
            'guess': guess,
            'result': result
        })

        current_player = (current_player + 1) % len(clients)
        prompt_next_player()

def run_server(host, port):
    """运行服务器主循环"""
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"Server started on {host}:{port}")

    while True:
        try:
            data, address = server_socket.recvfrom(1024)
            data = json.loads(data.decode())

            if data.get('type') == 'join':
                handle_new_client(address, data)
            elif data.get('type') == 'guess':
                handle_guess(address, data)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', required=True)
    parser.add_argument('--port', type=int, required=True)
    args = parser.parse_args()

    run_server(args.ip, args.port)
