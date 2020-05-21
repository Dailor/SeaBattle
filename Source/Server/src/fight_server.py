import json
import random
from SeaMap import SeaMap
from check_alive import Alive_checker
import threading
import time
import sys
import copy


class Fighting_server(threading.Thread):
    """тут серв на котором батлятся"""
    TIME_WAIT = 5

    def __init__(self, sock, addr_1, addr_2, checker_1, checker_2, nick_1, nick_2):
        threading.Thread.__init__(self)
        self.sock = sock
        self.sock.settimeout(5)
        self.nick_1, self.nick_2 = nick_1, nick_2
        print(nick_1, nick_2)
        self.addr_1, self.addr_2 = addr_1, addr_2
        self.check_addrs = [checker_1, checker_2]
        self.sock.settimeout(45)
        self.checker = Alive_checker()

        self.field_1, self.field_2 = list(), list()
        self.seamap_1, self.seamap_2 = SeaMap(), SeaMap()

        self.status_thread = True



    def check_players(self):
        # проверка подключения игроков
        now = time.time()
        while self.status_thread:
            if time.time() - now > Fighting_server.TIME_WAIT:
                now = time.time()
                for i in range(2):
                    if self.checker.check(self.check_addrs[i]) is True:
                        data = {"error": '2nd player left'}
                        data = json.dumps(data)
                        try:
                            self.sock.sendto(data.encode(), [self.addr_1, self.addr_2][i - 1])
                            self.status_thread = False
                        except:
                            self.status_thread = False
                        break

    def run(self):
        self.tr_check_players = threading.Thread(target=self.check_players)
        self.tr_check_players.start()

        while (len(self.field_1) == 0 or len(self.field_2) == 0) and self.status_thread is True:
            try:
                data, addr = self.sock.recvfrom(10000)
            except:
                print(self.status_thread)
                continue
            data = json.loads(data.decode())
            print(data, addr)
            if addr == self.addr_1:
                self.field_1 = data['field']
                self.ships_1 = data['ships']
            else:
                self.field_2 = data['field']
                self.ships_2 = data['ships']
        if self.status_thread is not True:
            return None

        self.move = random.choice([self.addr_1, self.addr_2])
        for addr, enemy in zip([self.addr_1, self.addr_2], [self.nick_2, self.nick_1]):
            data = f"game_start={self.move[0]}:{self.move[1]}={enemy}"
            self.sock.sendto(data.encode(), addr)

        while self.status_thread:
            if self.status_thread is False:
                sys.exit()
            try:
                data, addr = self.sock.recvfrom(512)
            except:
                continue

            if addr != self.move:
                continue

            data = data.decode()
            command, request = data.split('?')
            request = dict(([param.split('=') for param in request.split('&')]))
            if command == 'turn':
                data = self.done_turn(addr, request)
                for addr_ in [self.addr_1, self.addr_2]:
                    self.sock.sendto(data.encode(), addr_)

    def ship_counter(self, ship):
        counter = {1: 0, 2: 0, 3: 0, 4: 0}
        for key, value in ship.items():
            for key_, value_ in value.items():
                if value_[-1] != 0:
                    counter[int(key)] += 1
        return counter

    def _done_turn(self, row, col, field, seamap, ship, addr_moved, rest):
        before = copy.deepcopy(seamap.battle_map())
        if field[row][col] == '■':
            seamap.shoot(row, col, 'hit')
            clause = False
            for key, value in ship.items():
                for key_, value_ in value.items():
                    if [row, col] in value_:
                        need = ship[key][key_]
                        need[-1] -= 1
                        clause = True
                        break
                if clause is True:
                    break
            if need[-1] == 0:
                seamap.shoot(row, col, 'sink')
            won = None

            if all(x[-1] == 0 for values_ in ship.values() for x in values_.values()):
                won = addr_moved

            return seamap.show_difference(before), addr_moved, won, self.ship_counter(ship)
        else:
            seamap.shoot(row, col, 'miss')
            self.move = rest
            return seamap.show_difference(before), rest, None, self.ship_counter(ship)

    def done_turn(self, addr, request):
        row = int(request['row'])
        col = int(request['col'])
        if addr == self.addr_2:
            data, move, won, left_ships = self._done_turn(row, col, self.field_1, self.seamap_1, self.ships_1, addr,
                                                          self.addr_1)
        elif addr == self.addr_1:
            data, move, won, left_ships = self._done_turn(row, col, self.field_2, self.seamap_2, self.ships_2, addr,
                                                          self.addr_2)
            if won != None:
                self.status_thread = False
        result = {"moved": addr, "move": move, "moves": data, 'won': won, "left_ships": left_ships}
        return json.dumps(result)
