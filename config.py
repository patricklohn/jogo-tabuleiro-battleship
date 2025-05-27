import pygame

class Config:
    def __init__(self, screen, board_size=10, cell_size=40):
        self.screen = screen
        self.board_size = board_size
        self.cell_size = cell_size
        self.grid = [["~"] * board_size for _ in range(board_size)]
        self.ships = []
        # Navios para posicionar: (nome, tamanho)
        self.ships_to_place = [("Porta-aviões", 5), ("Encouraçado", 4), ("Destroyer", 3), ("Submarino", 3), ("Patrulha", 2)]
        self.current_ship_index = 0
        self.placing_horizontal = True
        self.running = True
        self.font = pygame.font.SysFont(None, 24)

    def run(self):
        clock = pygame.time.Clock()

        while self.running:
            self.screen.fill((0, 0, 50))
            self.draw_grid()
            self.draw_ships()
            self.draw_ui()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.placing_horizontal = not self.placing_horizontal
                    elif event.key == pygame.K_RETURN:
                        # Confirmação — se todos os navios posicionados
                        if self.current_ship_index >= len(self.ships_to_place):
                            self.running = False
                            return self.ships
                    elif event.key == pygame.K_BACKSPACE:
                        # Apaga último navio posicionado
                        if self.ships:
                            last = self.ships.pop()
                            for x, y in last:
                                self.grid[y][x] = "~"
                            self.current_ship_index = max(0, self.current_ship_index - 1)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.current_ship_index < len(self.ships_to_place):
                        pos = pygame.mouse.get_pos()
                        x = pos[0] // self.cell_size
                        y = pos[1] // self.cell_size
                        if self.can_place_ship(x, y):
                            ship_len = self.ships_to_place[self.current_ship_index][1]
                            coords = self.get_ship_coords(x, y, ship_len)
                            for cx, cy in coords:
                                self.grid[cy][cx] = "N"
                            self.ships.append(coords)
                            self.current_ship_index += 1

            clock.tick(30)

    def can_place_ship(self, x, y):
        ship_len = self.ships_to_place[self.current_ship_index][1]
        coords = self.get_ship_coords(x, y, ship_len)
        # Verifica limites
        for cx, cy in coords:
            if cx < 0 or cx >= self.board_size or cy < 0 or cy >= self.board_size:
                return False
            if self.grid[cy][cx] == "N":
                return False
        return True

    def get_ship_coords(self, x, y, length):
        if self.placing_horizontal:
            return [(x + i, y) for i in range(length)]
        else:
            return [(x, y + i) for i in range(length)]

    def draw_grid(self):
        for y in range(self.board_size):
            for x in range(self.board_size):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (0, 0, 100), rect)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)

                if self.grid[y][x] == "N":
                    pygame.draw.rect(self.screen, (0, 255, 0), rect.inflate(-10, -10))

    def draw_ships(self):
        # Opcional: destaca navio que está sendo posicionado (preview)
        pos = pygame.mouse.get_pos()
        x = pos[0] // self.cell_size
        y = pos[1] // self.cell_size
        if self.current_ship_index < len(self.ships_to_place):
            ship_len = self.ships_to_place[self.current_ship_index][1]
            coords = self.get_ship_coords(x, y, ship_len)
            valid = self.can_place_ship(x, y)
            color = (0, 200, 0, 100) if valid else (200, 0, 0, 100)
            s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            s.fill(color)
            for cx, cy in coords:
                if 0 <= cx < self.board_size and 0 <= cy < self.board_size:
                    self.screen.blit(s, (cx * self.cell_size, cy * self.cell_size))

    def draw_ui(self):
        # Instruções e status
        ship_name = "Todos os navios posicionados" if self.current_ship_index >= len(self.ships_to_place) else self.ships_to_place[self.current_ship_index][0]
        instr1 = "Clique para posicionar navio"
        instr2 = "R para rotacionar (horizontal/vertical)"
        instr3 = "Enter para confirmar"
        instr4 = "Backspace para apagar último navio"

        self.screen.blit(self.font.render(f"Posicionando: {ship_name}", True, (255, 255, 255)), (10, 410))
        self.screen.blit(self.font.render(instr1, True, (255, 255, 255)), (10, 430))
        self.screen.blit(self.font.render(instr2, True, (255, 255, 255)), (10, 450))
        self.screen.blit(self.font.render(instr3, True, (255, 255, 255)), (10, 470))
        self.screen.blit(self.font.render(instr4, True, (255, 255, 255)), (10, 490))
