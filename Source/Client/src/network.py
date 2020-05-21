import socket
import os


class Client(socket.socket):
    # Реализация клиентской части
    def __init__(self, ip=None, port=None):
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)

        self.client_path = os.getcwd().rsplit("\\", maxsplit=1)[0]
        settings_inf = self.client_path + '\\settings\\settings.inf'
        if ip is None and port is None:
            with open(settings_inf) as f:
                self.main_server = [line.replace("\n", '').split()[1] for line in f.readlines()]
        else:
            self.main_server = [ip, port]
        self.main_server = (self.main_server[0], int(self.main_server[1]))
        self.bind((socket.gethostbyname(socket.gethostname()), 0))

    def command_send(self, command):
        # отправка комманда на сервер
        self.sendto(command.encode(), self.main_server)
        data, addr = self.recvfrom(1024)
        data = data.decode()
        print(addr, data)
        return data
