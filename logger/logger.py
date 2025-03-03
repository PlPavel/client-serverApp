import socket
import os

def start_logger():
    log_file_server1 = "../server1/server1.log"
    log_file_server2 = "../server2/server2.log"

    if os.path.exists("/tmp/server_log"):
        os.unlink("/tmp/server_log")

    server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    server.bind("/tmp/server_log")

    print("Логгер запущен")
    try:
        while True:
            message = server.recv(1024).decode()
            if "[Server1]" in message:
                with open(log_file_server1, "a") as log_file:
                    log_file.write(message + "\n")
            elif "[Server2]" in message:
                with open(log_file_server2, "a") as log_file:
                    log_file.write(message + "\n")
            else:
                print("Неизвестное сообщение: ", message)
    except KeyboardInterrupt:
        print("\nЛоггер остановлен")
    finally:
        server.close()
        if os.path.exists("/tmp/server_log"):
            os.unlink("/tmp/server_log")

if __name__ == "__main__":
    start_logger()
