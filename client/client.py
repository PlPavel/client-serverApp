import socket
import os
import tkinter as tk
from tkinter import scrolledtext
import sys
import time
import threading

def log_event(message, server_label=None):
    """
    Логирует событие, добавляя метку сервера (например, [Server1]).
    """
    socket_path = "/tmp/server_log"
    if os.path.exists(socket_path):
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as log_socket:
                if server_label:
                    message = f"[{server_label}] {message}"
                log_socket.connect(socket_path)
                log_socket.send(message.encode())
        except Exception as e:
            print(f"Не удалось записать лог: {str(e)}")
    else:
        print(f"Сообщение: {message}")

def client(host, port, output_text=None, server_label=None, current_state=None):
    """
    Подключается к серверу, логирует события и ошибки с указанием метки сервера.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            message = f"\nПодключено к {host}:{port}\n"
            if output_text:
                output_text.insert(tk.END, message)
            else:
                print(message)

            # Отправка состояния клиента
            state_message = current_state or "initial"
            s.send(state_message.encode())

            data = s.recv(1024).decode()
            if output_text:
                output_text.insert(tk.END, f"[{server_label}] {data}\n")
            log_event(f"Полученные данные: {data}", server_label)

            return data
    except (ConnectionRefusedError, socket.error):
        error_message = f"[{server_label}] Сервер {host}:{port} недоступен."
        if output_text:
            output_text.insert(tk.END, error_message + "\n")
        log_event(error_message, server_label)
        return None
    except Exception as e:
        error_message = f"[{server_label}] Ошибка: {str(e)}"
        if output_text:
            output_text.insert(tk.END, error_message + "\n")
        log_event(error_message, server_label)
        return None

def periodic_client(host, port, output_text=None, server_label=None, current_state=None, interval=5):
    """
    Периодический клиент, который запрашивает данные и выводит только в случае изменений.
    """
    unavailable_count = 0
    max_unavailable = 3

    while unavailable_count < max_unavailable:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                
                # Отправка состояния клиента
                state_message = current_state or "initial"
                s.send(state_message.encode())

                data = s.recv(1024).decode()

                if data != current_state:  # Проверяем на изменения
                    current_state = data
                    if output_text:  # Выводим только при изменении данных
                        message = f"[{server_label}] Полученные данные: {data}\n"
                        output_text.insert(tk.END, message)
                    log_event(f"[{server_label}] Полученные данные: {data}", server_label)


                unavailable_count = 0  # Сброс счетчика, если сервер доступен

        except (ConnectionRefusedError, socket.error):
            error_message = f"[{server_label}] Сервер {host}:{port} недоступен."
            if output_text:
                output_text.insert(tk.END, error_message + "\n")
            log_event(error_message, server_label)
            unavailable_count += 1

        except Exception as e:
            error_message = f"[{server_label}] Ошибка: {str(e)}"
            if output_text:
                output_text.insert(tk.END, error_message + "\n")
            log_event(error_message, server_label)
            unavailable_count += 1

        time.sleep(interval)

    # Если сервер остается недоступным
    error_message = f"[{server_label}] Сервер {host}:{port} остается недоступным. Остановка обновлений."
    if output_text:
        output_text.insert(tk.END, error_message + "\n")
    log_event(error_message, server_label)

def start_periodic_updates(output_text=None):
    """
    Запускает режим периодических запросов к серверам.
    """
    servers = [("127.0.0.1", 5001, "Server1"), ("127.0.0.1", 5002, "Server2")]
    threads = []
    
    for host, port, label in servers:
        thread = threading.Thread(
            target=periodic_client, 
            args=(host, port, output_text, label, None, 5), 
            daemon=True
        )
        threads.append(thread)
        thread.start()

    # Ожидание завершения всех потоков
    for thread in threads:
        thread.join()

def terminate_client():
    """
    Завершает работу клиента.
    """
    print("Оба сервера недоступны. Завершается работа клиента.")
    sys.exit(0)

def client_both_servers(output_text=None):
    """
    Подключается к двум серверам одновременно и выводит их данные.
    """
    servers = [("127.0.0.1", 5001, "Server1"), ("127.0.0.1", 5002, "Server2")]
    for host, port, label in servers:
        client(host, port, output_text, server_label=label)

def on_exit(root):
    log_event("[Client] Клиент завершил работу")
    root.destroy()
    sys.exit(0)

def create_gui():
    root = tk.Tk()
    root.title("Клиент")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    server1_button = tk.Button(frame, text="Подключиться к серверу 1", command=lambda: client("127.0.0.1", 5001, output_text, server_label="Server1"))
    server1_button.pack(side=tk.LEFT, padx=5)

    server2_button = tk.Button(frame, text="Подключиться к серверу 2", command=lambda: client("127.0.0.1", 5002, output_text, server_label="Server2"))
    server2_button.pack(side=tk.LEFT, padx=5)

    both_servers_button = tk.Button(frame, text="Подключиться ко всем серверам", command=lambda: client_both_servers(output_text))
    both_servers_button.pack(side=tk.LEFT, padx=5)

    output_text = scrolledtext.ScrolledText(root, width=50, height=15)
    output_text.pack(pady=10)

    exit_button = tk.Button(root, text="Выход", command=lambda: on_exit(root))
    exit_button.pack(pady=10)

    root.protocol("WM_DELETE_WINDOW", lambda: on_exit(root))

    root.mainloop()

def create_console():
    while True:
        try:
            print("\nВыберите опцию:")
            print("1 - Подключиться к серверу 1")
            print("2 - Подключиться к серверу 2")
            print("3 - Подключиться ко всем серверам")
            print("4 - Периодическое обновление")
            print("5 - Запустить графический интерфейс")
            print("6 - Выход")

            choice = input("Введите номер: ")

            if choice == "1":
                client("127.0.0.1", 5001, server_label="Server1")
            elif choice == "2":
                client("127.0.0.1", 5002, server_label="Server2")
            elif choice == "3":
                print("Подключение ко всем серверам...")
                client_both_servers()
            elif choice == "4":
                print("Запуск периодического обновления...")
                start_periodic_updates()
            elif choice == "5":
                create_gui()
            elif choice == "6":
                print("Выход...")
                sys.exit(0)
            else:
                print("Неверный выбор, попробуйте снова.")
        except KeyboardInterrupt:
            print("\nЗавершение работы клиента...")
            print(f"Время: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            sys.exit(0)

if __name__ == "__main__":
    try:
        create_console()
    except KeyboardInterrupt:
        print("\nЗавершение работы клиента...")
