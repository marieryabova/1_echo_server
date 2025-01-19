DEFAULT_PORT = 5050

def ask_port():
    while True:
        answer = input('Введите порт сервера (-1 для значения по умолчанию): ')
        if answer == '-1':
            return DEFAULT_PORT
        try:
            port = int(answer)
            if 1024 <= port <= 65535:
                return port
            else:
                print('Порт должен быть в диапазоне от 1024 до 65535.')
        except ValueError:
            print('Некорректное значение порта. Введите число.')