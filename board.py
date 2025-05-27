import random

class Board:
    def __init__(self):
        self.size = 10
        self.grid = [["~"] * self.size for _ in range(self.size)]
        self.ships = []  # lista de sets de coordenadas
        self.hits = set()
        self.misses = set()

    def place_ship(self, positions):
        self.ships.append(set(positions))
        for x, y in positions:
            self.grid[y][x] = "N"

    def receive_attack(self, cell):
        x, y = cell
        for ship in self.ships:
            if cell in ship:
                self.hits.add(cell)
                self.grid[y][x] = "X"
                return True
        self.misses.add(cell)
        self.grid[y][x] = "O"
        return False

    def all_ships_sunk(self):
        for ship in self.ships:
            if not ship.issubset(self.hits):
                return False
        return True

    def can_place_ship(self, x, y, length, horizontal):
        coords = []
        for i in range(length):
            nx = x + i if horizontal else x
            ny = y if horizontal else y + i
            if nx >= self.size or ny >= self.size or self.grid[ny][nx] != "~":
                return False
            coords.append((nx, ny))

        # Verifica adjacentes
        for nx, ny in coords:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    ax, ay = nx + dx, ny + dy
                    if 0 <= ax < self.size and 0 <= ay < self.size:
                        if self.grid[ay][ax] == "N" and (ax, ay) not in coords:
                            return False
        return True

    def randomize_ships(self):
        ship_lengths = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        for length in ship_lengths:
            placed = False
            while not placed:
                x = random.randint(0, self.size - 1)
                y = random.randint(0, self.size - 1)
                horizontal = random.choice([True, False])
                if self.can_place_ship(x, y, length, horizontal):
                    positions = [(x + i, y) if horizontal else (x, y + i) for i in range(length)]
                    self.place_ship(positions)
                    placed = True

    def draw(self, surface, offset_x=0, offset_y=0, reveal=False):
        import pygame
        for y in range(self.size):
            for x in range(self.size):
                rect = pygame.Rect(offset_x + x*40, offset_y + y*40, 40, 40)
                pygame.draw.rect(surface, (0, 0, 100), rect)
                pygame.draw.rect(surface, (255, 255, 255), rect, 1)

                value = self.grid[y][x]
                if value == "X":
                    pygame.draw.line(surface, (255, 0, 0), rect.topleft, rect.bottomright, 3)
                    pygame.draw.line(surface, (255, 0, 0), rect.topright, rect.bottomleft, 3)
                elif value == "O":
                    pygame.draw.circle(surface, (255, 255, 255), rect.center, 10, 2)
                elif value == "N" and reveal:
                    pygame.draw.rect(surface, (0, 255, 0), rect.inflate(-10, -10))
