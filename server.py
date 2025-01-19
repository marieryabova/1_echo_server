import socket
import time
import logging
import json
from port import ask_port

def log_print(message, *kwargs):
    try:
        log_message = message.format(*kwargs)
        logging.info(log_message)
        print(log_message)
    except Exception as e:
        logging.exception(f"Ошибка при логировании: {e}")


logging.basicConfig(filename='server.log', encoding='utf-8', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

log_print('Сервер запущен')
port = ask_port()

server = socket.socket()
server.bind(('127.0.0.1', port))
log_print(f'Прослушивание порта {port}')

try:
    while True:
        server.listen(1)
        client_socket, address = server.accept()
        log_print(f"Подключение от {address}")

        class DataHandler:
            def __init__(self, filename):
                self.filename = filename

            def load(self):
                try:
                    with open(self.filename, 'r') as f:
                        return json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    return {}

            def save(self, data):
                try:
                    with open(self.filename, 'w') as f:
                        json.dump(data, f, indent=4)
                except Exception as e:
                    log_print(f"Ошибка при сохранении данных: {e}")


        class TextDataHandler:
            def __init__(self, filename):
                self.filename = filename

            def load(self):
                try:
                    with open(self.filename, 'r') as f:
                        return f.readlines()
                except FileNotFoundError:
                    return []

            def append(self, line):
                try:
                    with open(self.filename, 'a') as f:
                        f.write(line + '\n')
                except Exception as e:
                    log_print(f"Ошибка при записи в файл: {e}")


        stata_handler = DataHandler('stata.json')
        book_handler = TextDataHandler('book.txt')

        found_user = False
        for line in book_handler.load():
            parts = line.strip().split(', ')
            if len(parts) >= 3 and parts[2] == address[0]:
                found_user = True
                login = parts[0]
                break

        client_socket.send(str(found_user).encode())

        if found_user:
            stored_password = stata_handler.load().get(login)
            if stored_password is None:
                log_print(f"Ошибка: Пароль не найден для пользователя {login}")
                client_socket.send('Ошибка: Пароль не найден'.encode())
                client_socket.close()
                continue

            received_password = client_socket.recv(1024).decode()
            if stored_password == received_password:
                client_socket.send('Пароль верен'.encode())
                log_print(f"{address} авторизовался как {login}")
            else:
                client_socket.send('Пароль не верен'.encode())
                log_print(f"Неудачная попытка входа: {login}")
                client_socket.close()
                continue

        else:
            try:
                login = client_socket.recv(1024).decode()
                password = client_socket.recv(1024).decode()
                stata_handler.save({**stata_handler.load(), login: password})
                book_handler.append(f"{login}, {port}, {address[0]}, {address[1]}")
                log_print(f"{address} зарегистрировался как {login}")
            except Exception as e:
                log_print(f"Ошибка во время регистрации: {e}")
                client_socket.close()
                continue


        while True:
            client_socket.send('Вы подключены!'.encode())
            try:
                data = client_socket.recv(2048).decode()
                if data:
                    log_print(f"\nПолучаем данные от клиента: {data}")
                    if data.lower() == 'exit':
                        log_print('Клиент отключился')
                        break
                    msg = input('\nВвод текста для клиента:\n').encode()
                    client_socket.send(msg)
                    if msg == b'exit':
                        log_print('exit команда получена')
                        break

            except (OSError, ConnectionResetError) as e:
                log_print(f"Ошибка связи с клиентом: {e}")
                break
            except Exception as e:
                log_print(f"Произошла непредвиденная ошибка: {e}")


        client_socket.close()

except KeyboardInterrupt:
    log_print('Сервер отключен')
finally:
    server.close()