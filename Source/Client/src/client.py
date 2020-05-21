from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog
from PyQt5.QtCore import QThread, pyqtSignal
import os
import traceback
from network import Client
import json


def errors_handler(func):
    """Декоратор, вызывающий диалоговое окно с исключением при исключениях"""
    def wrapper(self):
        try:
            func(self)
        except Exception as e:
            error = traceback.format_exc()
            try:
                msg = QMessageBox(self)
                msg.setText(error)
                msg.show()
            except:
                print(error)

    return wrapper


class SeeBattle_Auth(QMainWindow):
    """Окно для авторизации"""
    forbidden_chars = "?&="

    def __init__(self, *args):
        self.client_path = os.getcwd().rsplit("\\", maxsplit=1)[0]

        super().__init__()

        self.uic_auth = self.client_path + '\\ui files\\auth_form.ui'
        uic.loadUi(self.uic_auth, self)

        self.network = False

        self.widget_functions()

        with open(self.client_path + '\\settings\\checker_ip.inf', 'r') as f:
            data = [line.split()[1] for line in f.read().split('\n')]
            self.checkers_ip, self.checkers_port = data
        self.checkers_port = int(self.checkers_port)

    def widget_functions(self):
        self.btn_auth.clicked.connect(self.sign_in)
        self.btn_sign_up.clicked.connect(self.sign_up)

    def mousePressEvent(self, event):
        x, y = event.x(), event.y()
        if 40 <= x <= 121 and 210 <= y <= 226:
            self.recovery_pass()

    def my_errors(self, error):
        # Ошибки не свзянанные с ошибками исполнения программы
        msg = QMessageBox(self)
        msg.setText(error)
        msg.show()
        return False

    def login_and_password_checker(self, login, password):
        # Проверка пароля
        for word, type_ in zip([login, password], ['Логин', "Пароль"]):
            if len(word.replace(' ', '')) == 0:
                return self.my_errors(f"{type_} не может быть пустой!")
            if len(word) == 0:
                return self.my_errors(f"{type_} не может быть пустой!")
            if any(ch in self.forbidden_chars for ch in word):
                return self.my_errors(f"{type_} не может содержать символы '?&='")
        return True

    def networking_switcher(self):
        # включение клиентской части
        if self.network is False:
            self.network = Client()

    @errors_handler
    def sign_in(self):
        # авторизация
        login = self.edit_login.text()
        password = self.edit_pass.text()
        if not self.login_and_password_checker(login, password):
            return False
        self.networking_switcher()

        result, data = self.network.command_send(
            f"auth?login={login}&password={password}&ip_port={self.checkers_ip}:{self.checkers_port}").split('?')
        if result == "False":
            self.my_errors(data)
            return False

        self.close()
        self.main_menu = Game_menu(data, self)
        self.main_menu.show()

        return True

    @errors_handler
    def recovery_pass(self):
        self.pass_rec = Password_rec(self)
        self.pass_rec.show()

    @errors_handler
    def sign_up(self):
        self.sign_up = Sign_up(self)
        self.sign_up.show()
        self.close()


class Sign_up(QMainWindow):
    """"Окно регистрации"""
    forbidden_chars = "?&="

    def __init__(self, *args):
        super().__init__()

        self.network = False

        self.client_path = os.getcwd().rsplit("\\", maxsplit=1)[0]

        self.uic_sign_up = self.client_path + '\\ui files\\sign_up.ui'
        uic.loadUi(self.uic_sign_up, self)

        self.btn_su.clicked.connect(self.sign_up)

    def my_errors(self, error):
        msg = QMessageBox(self)
        msg.setText(error)
        msg.show()
        return False

    def part_checker(self, login, password, secret):
        for word, type_ in zip([login, password, secret], ['Логин', "Пароль", "Секретное слово"]):
            if len(word.replace(' ', '')) == 0:
                return self.my_errors(f"{type_} не может быть пустой!")
            if len(word) == 0:
                return self.my_errors(f"{type_} не может быть пустой!")
            if any(ch in self.forbidden_chars for ch in word):
                return self.my_errors(f"{type_} не может содержать символы '?&='")

        return True

    def sign_up(self):
        login, password, secret = [x.text() for x in [self.edit_login, self.edit_pass, self.edit_secret]]
        if not self.part_checker(login, password, secret):
            return False

        if self.network is False:
            self.network = Client()
        result = self.network.command_send(f"sign_up?login={login}&password={password}&secret={secret}").split('?')

        
        if len(result) == 1:
            result = result[0]
            self.auth_form = SeeBattle_Auth(self)
            self.auth_form.show()
            self.close()
            self.network.close()
            msg = QMessageBox(self.auth_form)
            msg.setText("You was success registred")
            msg.show()
            return True
        return self.my_errors(result[1])
            

    def mousePressEvent(self, event):
        x, y = event.x(), event.y()
        if 20 <= x <= 67 and 10 <= y <= 30:
            self.auth_form = SeeBattle_Auth(self)
            self.auth_form.show()
            self.close()


class Password_rec(QDialog):
    """диалоговое окно на случай если юзер забыл пароль"""
    forbidden_chars = "?&="

    def __init__(self, *args):
        super().__init__()

        self.client_path = os.getcwd().rsplit("\\", maxsplit=1)[0]
        self.uic_auth = self.client_path + "\\ui files\\pass_rec.ui"
        uic.loadUi(self.uic_auth, self)

        self.network = False

        self.btn_recovery.clicked.connect(self.recovery_pass)

    def my_errors(self, error):
        msg = QMessageBox(self)
        msg.setText(error)
        msg.show()
        return False

    def part_checker(self, login, secret):
        for word, type_ in zip([login, secret], ['Логин', "Секретное слово"]):
            if len(word.replace(' ', '')) == 0:
                return self.my_errors(f"{type_} не может быть пустой!")
            if len(word) == 0:
                return self.my_errors(f"{type_} не может быть пустой!")
            if any(ch in self.forbidden_chars for ch in word):
                return self.my_errors(f"{type_} не может содержать символы '?&='")

        return True

    def recovery_pass(self):
        login, secret = [x.text() for x in [self.edit_login, self.edit_secret]]

        if not self.part_checker(login, secret):
            return False

        if self.network is False:
            self.network = Client()

        command = f"password_reset?login={login}&secret={secret}"
        result, data = self.network.command_send(command).split('?')
        if result != "False":
            self.close()
        return self.my_errors(data)


class Game_menu(QMainWindow):
    """игровое меню"""
    def __init__(self, data, pre, login=None):
        try:
            self.main_network = pre.network
        except Exception as e:
            self.main_network = pre.main_network
        self.thread_switch = Window_swither_thread_1(self.main_network, self)
        self.thread_switch.result_ready.connect(self.switch_to_next_window)

        super().__init__()

        if data is not None:
            self.user_info = dict([expression.split('=') for expression in data.split('&')])
        else:
            self.get_info_acc(login)

        self.client_path = os.getcwd().rsplit("\\", maxsplit=1)[0]
        self.uic_auth = self.client_path + "\\ui files\\main_menu.ui"
        uic.loadUi(self.uic_auth, self)

        self.main_menu_labels()
        self.btn_play.clicked.connect(self.player_find)

    def get_info_acc(self, login=None):
        # вывод в UI данные пользователя
        if login is  None:
            login = self.user_info["login"]
        data = self.main_network.command_send(f"get_info?login={login}").split('&')
        self.user_info = dict(
            [type_, info] for info, type_ in zip(data, ['login', 'password', 'secret', 'win', 'lose', 'draw']))

    def main_menu_labels(self):
        self.label_login.setText(self.user_info['login'])
        self.label_win.setText(self.user_info['win'] + 'W')
        self.label_draw.setText(self.user_info['lose'] + 'L')

    def switch_to_next_window(self, data):
        data = data.split(':')
        self.field_prepare = Ship_replace(self, data[0], int(data[1]))
        self.field_prepare.show()
        self.close()

    @errors_handler
    def player_find(self):
        self.btn_play.setEnabled(False)
        self.label_status.setText("Finding 2nd player")
        self.thread_switch.start()


class Window_swither_thread_1(QThread):
    """поток для смены окна (игрового меню => расстановка кораблей)"""
    result_ready = pyqtSignal(str)

    def __init__(self, sock, calling_class):
        self.main_network = sock
        self.calling_class = calling_class

        super().__init__()

    def run(self):
        data = self.main_network.command_send(f'play?login={self.calling_class.user_info["login"]}')
        while data == "finding_player":
            data, addr = self.main_network.recvfrom(1024)
            data = data.decode()
        else:
            data = data.split('?')[1].split('=')[1]
            self.result_ready.emit(data)


class Ask_to_server(QThread):
    """поток который делает запросы на сервер (если делать в классе с приложением без потока,  то приложение зависнет)"""
    result_ready = pyqtSignal(str)

    def __init__(self, sock, calling_class, command=None):
        self.main_network = sock
        self.calling_class = calling_class
        if command is None:
            self.command = None
        else:
            self.command = command

        super().__init__()

    def run(self):
        if self.command is None:
            self.main_network.sendto(self.calling_class.compressed_data_str.encode(), self.calling_class.server_)
        else:
            self.main_network.sendto(self.command[0].encode(), self.calling_class.server_)
        print(self.main_network.getsockname())
        result = self.main_network.recv(1024)
        print(result)
        data_result = result.decode()
        self.result_ready.emit(data_result)


class Ship_replace(QMainWindow):
    """тут кораблики расстанавливаем"""
    def __init__(self, pre, ip, port):
        super().__init__()
        self.server_ = ip, port,
        self.main_menu = pre

        self.main_network = pre.main_network

        self.thread_ = Ask_to_server(self.main_network, self)
        self.thread_.result_ready.connect(self.switch_to_battle)

        self.client_path = os.getcwd().rsplit("\\", maxsplit=1)[0]

        uic.loadUi(self.client_path + r'\ui files\replace_field.ui', self)

        self.battle_field = [['.' for _ in range(10)] for __ in range(10)]
        self.count_ships = {1: 4, 2: 3, 3: 2, 4: 1}

        self.placed_ships = {1: dict(),
                             2: dict(),
                             3: dict(),
                             4: dict()}

        self.dict_ship = {0: {1: "■", 2: "■■", 3: "■■■", 4: "■■■■"},
                          1: {1: "■", 2: "■\n■", 3: "■\n■\n■", 4: "■\n■\n■\n■"}}

        self.already_choose = 1
        self.rotate_enb = 0

        self.btn_take_1.setEnabled(False)
        self.label_show.setText(self.dict_ship[self.rotate_enb][self.already_choose])

        self.btn_take_1.clicked.connect(self.choose_1)
        self.btn_take_2.clicked.connect(self.choose_2)
        self.btn_take_3.clicked.connect(self.choose_3)
        self.btn_take_4.clicked.connect(self.choose_4)

        self.btn_ship_ch = {1: self.btn_take_1, 2: self.btn_take_2, 3: self.btn_take_3, 4: self.btn_take_4}

        self.list_btn_in_grid = [self.btn_1, self.btn_2, self.btn_3, self.btn_4, self.btn_5, self.btn_6, self.btn_7,
                                 self.btn_8, self.btn_9, self.btn_10, self.btn_11, self.btn_12, self.btn_13,
                                 self.btn_14, self.btn_15, self.btn_16, self.btn_17, self.btn_18, self.btn_19,
                                 self.btn_20, self.btn_21, self.btn_22, self.btn_23, self.btn_24, self.btn_25,
                                 self.btn_26, self.btn_27, self.btn_28, self.btn_29, self.btn_30, self.btn_31,
                                 self.btn_32, self.btn_33, self.btn_34, self.btn_35, self.btn_36, self.btn_37,
                                 self.btn_38, self.btn_39, self.btn_40, self.btn_41, self.btn_42, self.btn_43,
                                 self.btn_44, self.btn_45, self.btn_46, self.btn_47, self.btn_48, self.btn_49,
                                 self.btn_50, self.btn_51, self.btn_52, self.btn_53, self.btn_54, self.btn_55,
                                 self.btn_56, self.btn_57, self.btn_58, self.btn_59, self.btn_60, self.btn_61,
                                 self.btn_62, self.btn_63, self.btn_64, self.btn_65, self.btn_66, self.btn_67,
                                 self.btn_68, self.btn_69, self.btn_70, self.btn_71, self.btn_72, self.btn_73,
                                 self.btn_74, self.btn_75, self.btn_76, self.btn_77, self.btn_78, self.btn_79,
                                 self.btn_80, self.btn_81, self.btn_82, self.btn_83, self.btn_84, self.btn_85,
                                 self.btn_86, self.btn_87, self.btn_88, self.btn_89, self.btn_90, self.btn_91,
                                 self.btn_92, self.btn_93, self.btn_94, self.btn_95, self.btn_96, self.btn_97,
                                 self.btn_98, self.btn_99, self.btn_100]

        self.list_btn_in_grid = dict([(i, btn) for i, btn in zip(range(100), self.list_btn_in_grid)])

        for btn in self.list_btn_in_grid.values():
            btn.clicked.connect(self.ship_placer)

        self.btn_rotate.clicked.connect(self.rot_io)
        self.btn_delete.clicked.connect(self.some_act)
        self.btn_ready.clicked.connect(self.btn_ready_f)

    def switch_to_battle(self, data):
        try:
            if "game_start" in data:
                virtual = data.split('=')
                self.battle_arena = Battle_2v2(self, virtual[1], virtual[-1])
                self.battle_arena.show()
                self.close()
            elif '2nd player left' in data:
                self.main_menu = Game_menu(None, self, login= self.main_menu.user_info['login'])
                self.main_menu.show()
                self.close()
                msg = QMessageBox(self.main_menu)
                msg.setText("Second player left")
                msg.show()
        except Exception as e:
            print(traceback.format_exc())

    @errors_handler
    def btn_ready_f(self):
        if not all(i == 0 for i in self.count_ships.values()):
            return self.my_error('Вы не выставили все корабли')

        self.btn_delete.setEnabled(False)
        self.btn_take_1.setEnabled(False)
        self.btn_take_2.setEnabled(False)
        self.btn_take_3.setEnabled(False)
        self.btn_take_4.setEnabled(False)
        self.btn_ready.setEnabled(False)

        self.compressed_data = {"field": self.battle_field, "ships": self.placed_ships}
        self.compressed_data_str = json.dumps(self.compressed_data)

        self.thread_.start()

    def some_act(self):
        self.already_choose = 0
        self.enb_all()
        self.btn_delete.setEnabled(False)

    def delete_ship(self, row, col):
        need_coords = list()
        for key_1, values in self.placed_ships.items():
            for key_2, values_ in values.items():
                for x in values_:
                    if x == (row, col):
                        need_coords = values_[:-1]
                        break
                if len(need_coords) != 0:
                    break
            if len(need_coords) != 0:
                break
        if len(need_coords) == 0:
            return None

        self.count_ships[key_1] += 1
        for row, col in need_coords:
            self.list_btn_in_grid[row * 10 + col].setText('')
            self.battle_field[row][col] = '.'
        del self.placed_ships[key_1][key_2]
        self.ship_left_show()

    def ship_left_show(self):
        self.label_1.setText(str(self.count_ships[1]))
        self.label_2.setText(str(self.count_ships[2]))
        self.label_3.setText(str(self.count_ships[3]))
        self.label_4.setText(str(self.count_ships[4]))

    def my_error(self, exp):
        msg = QMessageBox(self)
        msg.setText(exp)
        msg.show()

    def rot_io(self):
        if self.rotate_enb == 0:
            self.rotate_enb = 1
        else:
            self.rotate_enb = 0
        self.ship_setter()

    def scan_on_acc(self, row, col, ang, d):
        if ang == 0:
            col_from = 0 if col - 1 < 0 else col - 1
            col_to = 10 if col + d + 1 > 10 else col + d + 1
            row_from = 0 if row - 1 < 0 else row - 1
            row_to = 10 if row + 2 > 10 else row + 2

        else:
            col_from = 0 if col - 1 < 0 else col - 1
            col_to = 10 if col + 2 > 10 else col + 2
            row_from = 0 if row - 1 < 0 else row - 1
            row_to = 10 if row + 1 + d > 10 else row + 1 + d
        return all(self.battle_field[row_][col_] != '■' for row_ in range(row_from, row_to) for col_ in
                   range(col_from, col_to))

    def ship_setter(self):
        if self.already_choose != 0:
            self.label_show.setText(self.dict_ship[self.rotate_enb][self.already_choose])

    def enb_all(self):
        for x in [self.btn_take_1, self.btn_take_2, self.btn_take_3, self.btn_take_4, self.btn_delete]:
            x.setEnabled(True)
        self.ship_setter()

    def choose_1(self):
        self.already_choose = 1
        self.enb_all()
        self.btn_take_1.setEnabled(False)

    def choose_2(self):
        self.already_choose = 2
        self.enb_all()
        self.btn_take_2.setEnabled(False)

    def choose_3(self):
        self.already_choose = 3
        self.enb_all()
        self.btn_take_3.setEnabled(False)

    def choose_4(self):
        self.already_choose = 4
        self.enb_all()
        self.btn_take_4.setEnabled(False)

    @errors_handler
    def ship_placer(self):
        coord = int(self.sender().objectName().split('_')[-1]) - 1

        row, col = coord // 10, coord % 10

        if self.already_choose == 0:
            return self.delete_ship(row, col)

        if self.count_ships[self.already_choose] == 0:
            return self.my_error('Корабли данного типа кончились')

        if self.scan_on_acc(row, col, self.rotate_enb, self.already_choose) is False:
            return self.my_error(
                "Корабль которые пытаетесь поставить должен на расстоянии на одну клетку(со всех сторон) от других кораблей")

        key_place = f"{str(self.already_choose)}_"

        for i in range(4):
            if f"{key_place}{str(i)}" not in self.placed_ships[self.already_choose]:
                key_place += str(i)
                break

        if self.rotate_enb == 0:

            if col + self.already_choose <= 10:
                self.placed_ships[self.already_choose][key_place] = list()
                for i in range(self.already_choose):
                    self.battle_field[row][col + i] = '■'
                    self.list_btn_in_grid[row * 10 + col + i].setText('■')
                    self.placed_ships[self.already_choose][key_place].append((row, col + i))
                self.placed_ships[self.already_choose][key_place].append(self.already_choose)
            else:
                return self.my_error("Корабль выходит за пределы поля")
        else:
            if row + self.already_choose <= 10:
                self.placed_ships[self.already_choose][key_place] = list()
                for i in range(self.already_choose):
                    self.battle_field[row + i][col] = '■'
                    self.list_btn_in_grid[(row + i) * 10 + col].setText('■')
                    self.placed_ships[self.already_choose][key_place].append(((row + i), + col))
                self.placed_ships[self.already_choose][key_place].append(self.already_choose)
            else:
                return self.my_error("Корабль выходит за пределы поля")
        self.count_ships[self.already_choose] -= 1
        self.ship_left_show()


class Battle_2v2(QMainWindow):
    """Экран сражения"""
    def __init__(self, pre, first, enemy):
        super().__init__()
        self.previous_class = pre

        self._user_data = self.previous_class.main_menu.user_info
        self._login = self._user_data['login']

        self.client_path = os.getcwd().rsplit("\\", maxsplit=1)[0]

        uic.loadUi(self.client_path + r"\ui files\battle_fields.ui", self)

        self.label_2.setText(f'Enemy {enemy}')

        self.main_network = pre.main_network
        self.server_ = pre.server_
        self.command = ['waiting']

        self.move = first.split(':')
        self.move = (self.move[0], int(self.move[1]))
        self.move = self.move != self.main_network.getsockname()

        self.player_1_ships = pre.compressed_data['field']

        self.perm_block = list()
        self.list_btn_in_grid_1 = [self.btn_1, self.btn_2, self.btn_3, self.btn_4, self.btn_5, self.btn_6, self.btn_7,
                                   self.btn_8, self.btn_9, self.btn_10, self.btn_11, self.btn_12, self.btn_13,
                                   self.btn_14, self.btn_15, self.btn_16, self.btn_17, self.btn_18, self.btn_19,
                                   self.btn_20, self.btn_21, self.btn_22, self.btn_23, self.btn_24, self.btn_25,
                                   self.btn_26, self.btn_27, self.btn_28, self.btn_29, self.btn_30, self.btn_31,
                                   self.btn_32, self.btn_33, self.btn_34, self.btn_35, self.btn_36, self.btn_37,
                                   self.btn_38, self.btn_39, self.btn_40, self.btn_41, self.btn_42, self.btn_43,
                                   self.btn_44, self.btn_45, self.btn_46, self.btn_47, self.btn_48, self.btn_49,
                                   self.btn_50, self.btn_51, self.btn_52, self.btn_53, self.btn_54, self.btn_55,
                                   self.btn_56, self.btn_57, self.btn_58, self.btn_59, self.btn_60, self.btn_61,
                                   self.btn_62, self.btn_63, self.btn_64, self.btn_65, self.btn_66, self.btn_67,
                                   self.btn_68, self.btn_69, self.btn_70, self.btn_71, self.btn_72, self.btn_73,
                                   self.btn_74, self.btn_75, self.btn_76, self.btn_77, self.btn_78, self.btn_79,
                                   self.btn_80, self.btn_81, self.btn_82, self.btn_83, self.btn_84, self.btn_85,
                                   self.btn_86, self.btn_87, self.btn_88, self.btn_89, self.btn_90, self.btn_91,
                                   self.btn_92, self.btn_93, self.btn_94, self.btn_95, self.btn_96, self.btn_97,
                                   self.btn_98, self.btn_99, self.btn_100]

        self.list_btn_in_grid_2 = [self.btn__1, self.btn__2, self.btn__3, self.btn__4, self.btn__5, self.btn__6,
                                   self.btn__7,
                                   self.btn__8, self.btn__9, self.btn__10, self.btn__11, self.btn__12, self.btn__13,
                                   self.btn__14, self.btn__15, self.btn__16, self.btn__17, self.btn__18, self.btn__19,
                                   self.btn__20, self.btn__21, self.btn__22, self.btn__23, self.btn__24, self.btn__25,
                                   self.btn__26, self.btn__27, self.btn__28, self.btn__29, self.btn__30, self.btn__31,
                                   self.btn__32, self.btn__33, self.btn__34, self.btn__35, self.btn__36, self.btn__37,
                                   self.btn__38, self.btn__39, self.btn__40, self.btn__41, self.btn__42, self.btn__43,
                                   self.btn__44, self.btn__45, self.btn__46, self.btn__47, self.btn__48, self.btn__49,
                                   self.btn__50, self.btn__51, self.btn__52, self.btn__53, self.btn__54, self.btn__55,
                                   self.btn__56, self.btn__57, self.btn__58, self.btn__59, self.btn__60, self.btn__61,
                                   self.btn__62, self.btn__63, self.btn__64, self.btn__65, self.btn__66, self.btn__67,
                                   self.btn__68, self.btn__69, self.btn__70, self.btn__71, self.btn__72, self.btn__73,
                                   self.btn__74, self.btn__75, self.btn__76, self.btn__77, self.btn__78, self.btn__79,
                                   self.btn__80, self.btn__81, self.btn__82, self.btn__83, self.btn__84, self.btn__85,
                                   self.btn__86, self.btn__87, self.btn__88, self.btn__89, self.btn__90, self.btn__91,
                                   self.btn__92, self.btn__93, self.btn__94, self.btn__95, self.btn__96, self.btn__97,
                                   self.btn__98, self.btn__99, self.btn__100]

        self.list_btn_in_grid_1 = dict([(i, btn) for i, btn in zip(range(100), self.list_btn_in_grid_1)])
        self.list_btn_in_grid_2 = dict([(i, btn) for i, btn in zip(range(100), self.list_btn_in_grid_2)])

        for row in range(10):
            for col in range(10):
                self.list_btn_in_grid_1[row * 10 + col].setEnabled(False)
                if self.player_1_ships[row][col] != '.':
                    self.list_btn_in_grid_1[row * 10 + col].setText(self.player_1_ships[row][col])

        self.thread_ = Ask_to_server(self.main_network, self, self.command)
        self.thread_.result_ready.connect(self.made_turn)

        for btn in self.list_btn_in_grid_2.values():
            if self.move:
                btn.setEnabled(False)
            btn.clicked.connect(self.send_turn)
        if self.move:
            self.label_turn.setText('Enemy')
            self.thread_.start()
        else:
            self.label_turn.setText('You')

    def block_btns(self):
        for value in self.list_btn_in_grid_2.values():
            value.setEnabled(False)

    def unblock_btns(self):
        for value in self.list_btn_in_grid_2.values():
            if value not in self.perm_block:
                value.setEnabled(True)

    def made_turn(self, data):
        print('got data', data)
        try:
            data = json.loads(data)
            if 'error' in data:
                self.main_menu = Game_menu(None, self, login=self._login)
                self.main_menu.show()
                self.close()
                msg = QMessageBox(self.main_menu)
                msg.setText(data["error"])
                msg.show()

            else:
                if tuple(data['moved']) == self.main_network.getsockname():
                    for steps, type_ in data['moves']:
                        row, col = steps
                        self.list_btn_in_grid_2[row * 10 + col].setText(type_)
                        self.list_btn_in_grid_2[row * 10 + col].setEnabled(False)
                        self.perm_block.append(self.list_btn_in_grid_2[row * 10 + col])
                    ch = 1
                    for label in [self.label_one_2, self.label_two_2, self.label_three_2, self.label_four_2]:
                        label.setText(str(data['left_ships'][str(ch)]))
                        ch += 1

                else:
                    for steps, type_ in data['moves']:
                        row, col = steps
                        if type_ == "■":
                            self.list_btn_in_grid_1[row * 10 + col].setText('X')
                        else:
                            self.list_btn_in_grid_1[row * 10 + col].setText(type_)
                    ch = 1
                    for label in [self.label_one, self.label_two, self.label_three, self.label_four]:
                        label.setText(str(data['left_ships'][str(ch)]))
                        ch += 1

                if tuple(data['move']) == self.main_network.getsockname():
                    self.unblock_btns()
                    self.label_turn.setText( 'You')
                else:
                    self.label_turn.setText( 'Enemy')
                    if data['won'] == None:
                        self.thread_.start()
                    self.block_btns()

                if data['won'] != None:

                    won = "You won" if tuple(data['won']) == self.main_network.getsockname() else "You lost"

                    if won == 'You won':
                        self.main_network.command_send(
                            f'info_correct?win={int(self._user_data["win"]) + 1}&lose={self._user_data["lose"]}&login={self._login}')
                    else:
                        self.main_network.command_send(
                            f'info_correct?win={int(self._user_data["win"])}&lose={int(self._user_data["lose"]) + 1}&login={self._login}')

                    self.main_menu = Game_menu(None, self, login=self._login)
                    self.main_menu.show()
                    msg = QMessageBox(self.main_menu)
                    msg.setText(won)
                    msg.show()
                    self.close()

        except:
            print(traceback.format_exc())

    @errors_handler
    def send_turn(self):
        # Оправка данных о ходе
        coord = int(self.sender().objectName().split('__')[-1]) - 1
        self.perm_block.append(self.list_btn_in_grid_2[coord])
        self.block_btns()
        row, col = coord // 10, coord % 10
        self.command[0] = f"turn?row={row}&col={col}"
        self.thread_.start()
