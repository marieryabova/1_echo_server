import socket
import time
from port import ask_port

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 5050

def connect_to_server(host, port):
    client = socket.socket()
    try:
        client.connect((host, port))
        return client
    except (ConnectionRefusedError, socket.gaierror) as e:
        print(f"Ошибка подключения: {e}")
        return None

def handle_auth(client):
    nal = client.recv(1024).decode()
    if nal == 'YES':
        password = input('Введите пароль: ')
        client.send(password.encode())
        response = client.recv(1024).decode()
        if response == 'Пароль верен':
            print('Пароль верен')
            return True
        else:
            print('Пароль не верен')
            return False
    else:
        login = input('Введите логин: ')
        client.send(login.encode())
        password = input('Введите пароль: ')
        client.send(password.encode())
        return True


port = ask_port()
host = input('Введите имя хоста (по умолчанию localhost): ') or DEFAULT_HOST

client = connect_to_server(host, port)

if client is None:
    print('Подключение не удалось.')
    exit()


if not handle_auth(client):
    client.close()
    exit()


print(client.recv(2048).decode())

try:
    while True:
        cl_msg = input('Введите текст для сервера (exit для выхода):\n').encode()
        client.send(cl_msg)
        if cl_msg.lower() == b'exit':
            break

        data = client.recv(2048).decode()
        time.sleep(3)

        if data.lower() == 'exit':
            break
        if data:
            print(f'\nТекст с сервера: {data}\n')

except KeyboardInterrupt:
    print('Подключение прервано пользователем.')
except Exception as e:
    print(f"Произошла ошибка: {e}")
finally:
    client.send('Клиент отсоединился'.encode())
    client.shutdown(socket.SHUT_WR)
    client.close()
    print('Разрыв соединения с сервером.')