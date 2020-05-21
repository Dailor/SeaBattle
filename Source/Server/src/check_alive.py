import socket


class Alive_checker(socket.socket):
    def __init__(self):
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self.settimeout(5)

    def check(self, addr):
        data_for_check = 'True'
        try:
            self.sendto(data_for_check.encode(), addr)
            if self.recvfrom(1024)[0].decode() == data_for_check:
                return False
        except Exception as e:
            return True
