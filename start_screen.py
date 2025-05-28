import pygame

class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 48)
        self.options = ["Jogo Local", "Criar Sala (Servidor)", "Entrar em Sala (Cliente)", "Ver histórico", "Sair"]
        self.selected = 0
        self.ip_input_active = False
        self.ip_text = ''
        self.ip_prompt = "Digite o IP do servidor:"
        self.sound_options = {
            "background": True,
            "pew": True,
            "boom": True
        }

    def run(self):
        clock = pygame.time.Clock()
        while True:
            self.screen.fill((0, 0, 80))
            if self.ip_input_active:
                self.draw_ip_input()
            else:
                self.draw_options()
                self.draw_checkboxes()

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None, self.sound_options

                if self.ip_input_active:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            ip = self.ip_text.strip()
                            if ip:
                                return ("Entrar em Sala (Cliente)", ip, self.sound_options)
                        elif event.key == pygame.K_BACKSPACE:
                            self.ip_text = self.ip_text[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            self.ip_input_active = False
                            self.ip_text = ''
                        elif len(self.ip_text) < 15 and (event.unicode.isdigit() or event.unicode == '.'):
                            self.ip_text += event.unicode
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.selected = (self.selected - 1) % len(self.options)
                        elif event.key == pygame.K_DOWN:
                            self.selected = (self.selected + 1) % len(self.options)
                        elif event.key == pygame.K_RETURN:
                            if self.options[self.selected] == "Entrar em Sala (Cliente)":
                                self.ip_input_active = True
                                self.ip_text = ''
                            else:
                                return (self.options[self.selected], None, self.sound_options)

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self.check_checkbox_click(event.pos)

            clock.tick(30)

    def draw_options(self):
        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i == self.selected else (180, 180, 180)
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(self.screen.get_width() // 2, 150 + i * 60))
            self.screen.blit(text, rect)

    def draw_ip_input(self):
        prompt = self.font.render(self.ip_prompt, True, (255, 255, 255))
        self.screen.blit(prompt, (50, 180))

        input_box = pygame.Rect(50, 240, 400, 50)
        pygame.draw.rect(self.screen, (255, 255, 255), input_box, 2)

        ip_surface = self.font.render(self.ip_text, True, (255, 255, 255))
        self.screen.blit(ip_surface, (input_box.x + 10, input_box.y + 10))

        info = pygame.font.SysFont(None, 28).render("Pressione ESC para voltar", True, (200, 200, 200))
        self.screen.blit(info, (50, 310))

    def draw_checkboxes(self):
        small_font = pygame.font.SysFont(None, 32)
        start_y = 400
        spacing = 40
        for i, (key, label) in enumerate({
            "background": "Som de Fundo",
            "pew": "Som de Disparo",
            "boom": "Som de Acerto"
        }.items()):
            checked = self.sound_options[key]
            text = small_font.render(label, True, (255, 255, 255))
            self.screen.blit(text, (100, start_y + i * spacing))

            box = pygame.Rect(60, start_y + i * spacing + 5, 20, 20)
            pygame.draw.rect(self.screen, (255, 255, 255), box, 2)
            if checked:
                pygame.draw.line(self.screen, (255, 255, 255), box.topleft, box.bottomright, 2)
                pygame.draw.line(self.screen, (255, 255, 255), box.topright, box.bottomleft, 2)

    def check_checkbox_click(self, pos):
        start_y = 400
        spacing = 40
        for i, key in enumerate(["background", "pew", "boom"]):
            box = pygame.Rect(60, start_y + i * spacing + 5, 20, 20)
            if box.collidepoint(pos):
                self.sound_options[key] = not self.sound_options[key]
