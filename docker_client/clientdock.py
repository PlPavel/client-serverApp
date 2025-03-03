import socket
import sys
import time

def client(host, port, server_label):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            print(f"Подключено к {server_label} ({host}:{port})\n")

            data = s.recv(1024).decode()
            print(f"Полученные данные от {server_label}:\n{data}\n")
    except Exception as e:
        error_message = f"[Client] Ошибка при подключении к {server_label}: {str(e)}"
        print(error_message)

def main():
    try:
        while True:
            print("\nВыберите опцию:")
            print("1 - Подключиться к серверу 1")
            print("2 - Подключиться к серверу 2")
            print("3 - Подключиться ко всем серверам")
            print("4 - Выход")

            choice = input("Введите номер: ")

            if choice == "1":
                client("host.docker.internal", 5001, "Сервер 1")
            elif choice == "2":
                client("host.docker.internal", 5002, "Сервер 2")
            elif choice == "3":
                print("Получение данных от обоих серверов...\n")
                client("host.docker.internal", 5001, "Сервер 1")
                client("host.docker.internal", 5002, "Сервер 2")
            elif choice == "4":
                print("Выход...")
                sys.exit(0)
            else:
                print("Неверный выбор, попробуйте снова.")
    except KeyboardInterrupt:
            print("\nЗавершение работы клиента...")
            print(f"Время: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            sys.exit(0)

if __name__ == "__main__":
    main()
