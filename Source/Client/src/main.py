from PyQt5.QtWidgets import QApplication
from sys import argv, exit
from client import SeeBattle_Auth
import threading
from check_alive import Check_alive
import multiprocessing


def main_qt():
    # Основной поток программы
    app = QApplication(argv)
    ex = SeeBattle_Auth()
    ex.show()
    exit(app.exec())


def main():
    # Поток для проверки клиента
    thread_alive = Check_alive()
    thread_alive.start()
    print(thread_alive.isDaemon())

    main_qt()


if __name__ == '__main__':
    main()
