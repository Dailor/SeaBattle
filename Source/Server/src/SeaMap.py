class SeaMap:
    # класс для карты боя
    def __init__(self):
        self.m = [['.' for i in range(10)] for x in range(10)]
        self.h = []
        self.ho = []
        self.k = 0

    def shoot(self, x, y, task):
        if task == 'miss':
            self.m[x][y] = '*'
        elif task == 'hit':
            self.m[x][y] = '■'
        else:
            self.m[x][y] = '■'
            self.h = []
            self.ho = list()
            for i in range(x, 10):
                if self.cell(i, y) == '■':
                    self.h.append((i, y))
                else:
                    break
            for i in range(x, -1, -1):
                if self.cell(i, y) == '■':
                    self.h.append((i, y))
                else:
                    break
            # -------------------------------
            for i in range(y, 10):
                if self.cell(x, i) == '■':
                    self.h.append((x, i))
                else:
                    break
            for i in range(y, -1, -1):
                if self.cell(x, i) == '■':
                    self.h.append((x, i))
                else:
                    break
            self.ho = list(set(self.h))

            for x, y in self.ho:
                if x - 1 >= 0 and self.cell(x - 1, y) != '■':
                    self.shoot(x - 1, y, 'miss')
                if (x - 1 >= 0) and (y + 1 <= 9) and self.cell(x - 1, y + 1) != '■':
                    self.shoot(x - 1, y + 1, 'miss')
                if y + 1 <= 9 and self.cell(x, y + 1) != '■':
                    self.shoot(x, y + 1, 'miss')
                if (x + 1 <= 9) and (y + 1 <= 9) and self.cell(x + 1, y + 1) != '■':
                    self.shoot(x + 1, y + 1, 'miss')
                if x + 1 <= 9 and self.cell(x + 1, y) != '■':
                    self.shoot(x + 1, y, 'miss')
                if y - 1 >= 0 and x + 1 <= 9 and self.cell(x + 1, y - 1) != '■':
                    self.shoot(x + 1, y - 1, 'miss')
                if y - 1 >= 0 and self.cell(x, y - 1) != '■':
                    self.shoot(x, y - 1, 'miss')
                if x - 1 >= 0 and y - 1 >= 0 and self.cell(x - 1, y - 1) != '■':
                    self.shoot(x - 1, y - 1, 'miss')

    def cell(self, x, y):
        return self.m[x][y]

    def battle_map(self):
        return self.m

    def show_difference(self, compare):
        difference = list()
        for row in range(10):
            for col in range(10):
                if compare[row][col] != self.m[row][col]:
                    difference.append(((row, col), self.m[row][col]))
        return difference
