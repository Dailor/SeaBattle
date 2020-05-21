import socket
import os
import threading

class Check_alive(socket.socket, threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self.daemon = True


    def run(self):
        # Подключение к серверу
        self.clients_path = os.getcwd().rsplit("\\", maxsplit=1)[0]
        self.server_ip = socket.gethostbyname(socket.gethostname())
        self.bind((self.server_ip, 0))

        self.server_port = self.getsockname()[1]

        with open(self.clients_path + '\\settings\\checker_ip.inf', 'w') as f:
            f.write(f'ip {self.server_ip}\n')
            f.write(f'port {self.server_port}')


        # Подтверждение что клиент в сети
        while True:
            try:
                data, addr = self.recvfrom(512)
                print(data.decode())
                self.sendto(data, addr)
            except Exception as e:
                print(e)
