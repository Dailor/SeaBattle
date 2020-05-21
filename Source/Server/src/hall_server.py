import socket
import sqlite3
import os
from threading import Thread
from fight_server import Fighting_server
from check_alive import Alive_checker


class Server(socket.socket):
    """типа тут сокет серва, серва обработчика всего кроме драк"""

    def __init__(self):
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)

        self.script_path = os.getcwd().rsplit("\\", maxsplit=1)[0]

        self.server_ip = socket.gethostbyname(socket.gethostname())
        self.server_port = 0

        self.checker = Alive_checker()

        self.database_conn()
        self.run_server()

    def database_conn(self):
        # подключенеи к бд
        if not os.path.exists(self.script_path + "\\accounts.db"):
            self.database = sqlite3.connect(self.script_path + "\\accounts.db")
            self.database_cursor = self.database.cursor()
            self.database_cursor.execute(
                """CREATE TABLE accounts("login" TEXT,"password" TEXT,"secret_key" TEXT,"win" INTEGER,"lose" INTEGER,"draw" INTEGER)""")
        else:
            self.database = sqlite3.connect(self.script_path + "\\accounts.db")
            self.database_cursor = self.database.cursor()

    def database_execute(self, command, args=None):
        # исполнение комманд в бд
        if args is not None:
            self.database_cursor.execute(command, args)
        else:
            self.database_cursor.execute(command)
        self.database.commit()
        return self.database_cursor.fetchall()

    def run_server(self):
        # Запуск сервера

        self.bind((self.server_ip, self.server_port))

        self.server_port = self.getsockname()[1]

        with open(self.script_path + '\\settings.inf', 'w') as f:
            f.write(f"ip {self.server_ip}\n")
            f.write(f"port {self.server_port}")

        self.peoples_status = dict()

        # получение и обрабатывание комманд
        while True:
            try:
                data, addr = self.recvfrom(1024)
            except:
                continue
            data = data.decode()
            command, request = data.split('?')  # example auth?login=ex&password=pass
            request = dict([expression.split('=') for expression in request.split('&')])
            print(command, request)
            if command.lower() == "auth":
                data = self.auth_sign_in(request, addr).encode()
                self.sendto(data, addr)
            elif command.lower() == "sign_up":
                data = self.auth_sign_up(request).encode()
                self.sendto(data, addr)
            elif command.lower() == "password_reset":
                data = self.auth_pass_reset(request).encode()
                self.sendto(data, addr)
            elif command.lower() == "get_info":
                data = self.get_acc_info(request).encode()
                self.sendto(data, addr)
            elif command.lower() == "play":
                data = self.fight_server_send(addr, request).encode()
                self.sendto(data, addr)
            elif command.lower() == "info_correct":
                data = self.data_correcter(request).encode()
                self.sendto(data, addr)

    def data_correcter(self, request):
        sql_command = """UPDATE accounts SET win=?, lose=? WHERE login=?"""
        self.database_execute(sql_command, [request['win'], request['lose'], request['login']])
        return 'done'

    def auth_sign_in(self, request, addr):
        sql_command = """SELECT * FROM accounts WHERE login=?"""
        data = self.database_execute(sql_command, [request["login"]])
        if len(data) == 0:
            return "False?Incorrect login !"
        if data[0][1] != request["password"]:
            return "False?Incorrect password !"
        if data[0][0] not in self.peoples_status:
            checkers_ip, port = request["ip_port"].split(':')
            port = int(port)
            self.peoples_status[data[0][0]] = [addr, (checkers_ip, port), "in_main_menu"]
        else:
            check = self.peoples_status[data[0][0]][1]
            if self.checker.check(check):
                checkers_ip, port = request["ip_port"].split(':')
                port = int(port)
                self.peoples_status[data[0][0]] = [addr, (checkers_ip, port), "in_main_menu"]
            else:
                return "False?That login is already using!"
        return "True?login={}&password={}&win={}&lose={}&draw={}".format(*data[0][:2], *data[0][3:])

    def auth_sign_up(self, request):
        # login, password, secret,
        sql_command = """SELECT * FROM accounts WHERE login=?"""
        data = self.database_execute(sql_command, [request["login"]])
        if len(data) != 0:
            return "False?Under this login already registered"
        sql_command = """INSERT INTO accounts
        VALUES (?, ?, ?, ?, ?, ?)"""
        data = self.database_execute(sql_command, [request["login"], request["password"], request["secret"], 0, 0, 0])
        return "True"

    def auth_pass_reset(self, request):
        sql_command = """SELECT password, secret_key FROM accounts WHERE login=?"""
        data = self.database_execute(sql_command, [request["login"]])
        if len(data) == 0:
            return "False?Incorrect login !"
        if request["secret"] != data[0][1]:
            return "False?Incorrect secret!"
        return f"True?Your password is '{data[0][0]}'"

    def get_acc_info(self, request):
        sql_command = """SELECT * FROM accounts WHERE login=?"""
        data = self.database_execute(sql_command, [request["login"]])[0]
        return '&'.join(str(x) for x in data)

    def change_acc_info(self, request):
        sql_command = f"""UPDATE accounts SET win=?, lose=? WHERE login=?"""
        data = self.database_execute(sql_command, [request['win'], request['lose'], request['login']])

    def fight_server_send(self, addr_client, request):
        self.peoples_status[request["login"]][2] = "finding_game"
        while True:
            try:
                for key, addr in map(lambda values: (values[0], values[1][1]), self.peoples_status.items()):
                    if self.checker.check(addr) is True:
                        del self.peoples_status[key]
            except:
                continue
            break
        for login, (ip_client, ip_checker, status) in self.peoples_status.items():
            if login == request["login"]:
                continue
            if status == 'finding_game':
                self.peoples_status[request["login"]][2] = 'in_fight'
                self.peoples_status[login][2] = 'in_fight'

                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind((self.server_ip, 0))
                port = sock.getsockname()[1]

                tr = Fighting_server(
                    sock, ip_client, addr_client, ip_checker,
                    self.peoples_status[request["login"]][1], request["login"], login)
                tr.start()

                on_return = f'game_found?ip_port={self.server_ip}:{port}'
                self.sendto(on_return.encode(), self.peoples_status[login][0])
                return on_return
        return "finding_player"


if __name__ == '__main__':
    ex = Server()
