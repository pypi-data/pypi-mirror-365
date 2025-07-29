import sys
import os

class ScreenBuffer:
    def __init__(self, width: int = 70, height: int = 30, fill=" "):
        self.width = width
        self.height = height
        self.fill = fill

        # Matriz: linhas (y), colunas (x)
        self.screen = [[self.fill for _ in range(width)] for _ in range(height)]

        self.dirty_cells: set[tuple[int, int]] = set()
        self._border_drawn = False

    @staticmethod
    def os_clearterminal():
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

    def clear(self):
        for y in range(self.height):
            for x in range(self.width):
                self.screen[y][x] = self.fill

        self.dirty_cells = {(x, y) for y in range(self.height) for x in range(self.width)}

    def draw(self, x: int, y: int, text: str):
        for i, char in enumerate(text):
            px = x + i
            if 0 <= px < self.width and 0 <= y < self.height:
                self.screen[y][px] = char
                self.dirty_cells.add((px, y))  

    def draw_matrix(self, x: int, y: int, matrix: list[list[str]]):
        for dy, row in enumerate(matrix):
            for dx, char in enumerate(row):
                px, py = x + dx, y + dy
                if 0 <= px < self.width and 0 <= py < self.height:
                    self.screen[py][px] = char  # [y][x]
                    self.dirty_cells.add((px, py))  # (x,y)

    def render(self, draw_border: bool = True):
        if draw_border and not self._border_drawn:
            sys.stdout.write("\033[H")
            sys.stdout.write("┌" + "─" * self.width + "┐\n")
            for _ in range(self.height):
                sys.stdout.write("│" + " " * self.width + "│\n")
            sys.stdout.write("└" + "─" * self.width + "┘")
            sys.stdout.flush()
            self._border_drawn = True

        for (x, y) in self.dirty_cells:
            if 0 <= x < self.width and 0 <= y < self.height:
                sys.stdout.write(f"\033[{y + 2};{x + 2}H{self.screen[y][x]}")

        sys.stdout.flush()
        self.dirty_cells.clear()
