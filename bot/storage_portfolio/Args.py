from bot.config import *


class Args:
    def __init__(self, commands) -> None:
        self.input = commands
        self.list = ""
        self.select = ""
        self.current = ""
        self.save = ""
        self.add = ""
        self.rm = ""
        self.delete = ""
        self.stat = ""
        self.compare = ""

        self.name = ""
        self.compared_name = ""
        self.stock = ""
        self.id = ""
        self.lot = ""
        self.price = ""

    def parse(self):
        words = str(self.input).split(" ")
        command = words[1]
        if command == SAVED_PORTFOLIO[1]:
            self.list = SAVED_PORTFOLIO[1]

        elif command == SAVED_PORTFOLIO[2]:
            self.select = SAVED_PORTFOLIO[2]
            self.name = words[2]

        elif command == SAVED_PORTFOLIO[3]:
            self.current = SAVED_PORTFOLIO[3]

        elif command == SAVED_PORTFOLIO[4]:
            self.save = SAVED_PORTFOLIO[4]
            self.id = words[2]
            self.name = words[3]

        elif command == SAVED_PORTFOLIO[5]:
            self.add = SAVED_PORTFOLIO[5]
            self.stock = words[2]
            self.lot = words[3]
            self.price = words[4]

        elif command == SAVED_PORTFOLIO[6]:
            self.rm = SAVED_PORTFOLIO[6]
            self.stock = words[2]
            self.lot = words[3]

        elif command == SAVED_PORTFOLIO[7]:
            self.delete = SAVED_PORTFOLIO[7]
            self.name = words[2]

        elif command == SAVED_PORTFOLIO[8]:
            self.stat = SAVED_PORTFOLIO[8]

        elif command == SAVED_PORTFOLIO[9]:
            self.compare = SAVED_PORTFOLIO[9]
            self.compared_name = words[2]
        return self

    def is_list(self) -> bool:
        return self.list == SAVED_PORTFOLIO[1]

    def is_select(self) -> bool:
        return self.select == SAVED_PORTFOLIO[2] and len(self.name) > 0

    def is_current(self) -> bool:
        return self.current == SAVED_PORTFOLIO[3]

    def is_save(self) -> bool:
        return self.save == SAVED_PORTFOLIO[4] and len(self.id) > 0 and len(self.name) > 0

    def is_add(self) -> bool:
        return self.add == SAVED_PORTFOLIO[5] and len(self.stock) > 0 and len(self.lot) > 0 and len(self.price) > 0

    def is_rm(self) -> bool:
        return self.rm == SAVED_PORTFOLIO[6] and len(self.stock) > 0 and len(self.lot) > 0

    def is_delete(self) -> bool:
        return self.delete == SAVED_PORTFOLIO[7] and len(self.delete) > 0

    def is_stat(self) -> bool:
        return self.stat == SAVED_PORTFOLIO[8]

    def is_compare(self) -> bool:
        return self.compare == SAVED_PORTFOLIO[9] and len(self.compared_name) > 0
