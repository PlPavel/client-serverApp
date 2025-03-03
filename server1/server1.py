import socket
import threading
import os
import time
import signal
from screeninfo import get_monitors

PID_FILE = "/tmp/server1.pid"

def log_event(message):
    try:
        log_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        log_socket.connect("/tmp/server_log")
        log_socket.send(message.encode())
        log_socket.close()
    except FileNotFoundError:
        pass
        # print("Логгер не запущен. Сообщение не записано:", message)

def write_pid_file():
    """Создает PID-файл и записывает туда PID текущего процесса."""
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def remove_pid_file():
    """Удаляет PID-файл."""
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def check_existing_server():
    """Проверяет, запущен ли уже сервер."""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)  # Проверка, работает ли процесс с таким PID
            print(f"Сервер уже запущен с PID {pid}.")
            return True
        except (ProcessLookupError, ValueError):
            # Если процесс не существует, удалить устаревший PID-файл
            remove_pid_file()
    return False

def server1_handler(client_socket):
    try:
        log_event("[Server1] Подключение клиента")
        window_size = os.get_terminal_size() 
        monitor_count = len(get_monitors())  # Фиксированное количество мониторов
        response = (
            f"Размер окна серверного процесса: {window_size.columns}x{window_size.lines}\n"
            f"Количество мониторов: {monitor_count}\n"
            f"Время: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        client_socket.send(response.encode())
        log_event(f"[Server1] Данные отправлены:\n{response}")
    except Exception as e:
        error_message = f"[Server1] Ошибка: {str(e)}"
        client_socket.send(error_message.encode())
        log_event(error_message)
    finally:
        client_socket.close()

def start_server1():
    if check_existing_server():
        return

    write_pid_file()

    host = "127.0.0.1"
    port = 5001
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    log_event("[Server1] Сервер запущен")
    print(f"Сервер 1 запущен на {host}:{port}")

    def shutdown_server():
        """Обработчик сигнала завершения."""
        log_event("[Server1] Сервер остановлен")
        print("\nСервер 1 остановлен")
        server.close()
        remove_pid_file()
        exit(0)

    signal.signal(signal.SIGTERM, shutdown_server)  # Для системных сигналов

    try:
        while True:
            client_socket, addr = server.accept()
            log_event(f"[Server1] Подключение от {addr}")
            threading.Thread(target=server1_handler, args=(client_socket,)).start()
    except Exception as e:
        log_event(f"[Server1] Ошибка сервера: {e}")
    finally:
        shutdown_server()

if __name__ == "__main__":
    start_server1()
