import pygame
import sys
from start_screen import StartScreen
from network import NetworkServer, NetworkClient
from board import Board
from config import Config
import threading
import time
from queue import Queue
import socket

# Inicializa pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 950, 650
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Batalha Naval")

sound_pew = pygame.mixer.Sound("assets/sounds/pew.wav")
sound_boom = pygame.mixer.Sound("assets/sounds/boom.wav")
sound_background = pygame.mixer.Sound("assets/sounds/background.wav")

def draw_text_centered(screen, text, size, color, y):
    font = pygame.font.SysFont(None, size)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(SCREEN_WIDTH // 2, y))
    screen.blit(rendered, rect)

def play_sound(sound, enabled):
    if enabled:
        sound.play()

def game_loop(screen, network, is_server, sound_config, my_ships, enemy_ships):
    clock = pygame.time.Clock()
    board = Board()
    enemy_board = Board()

    for ship in my_ships:
        board.place_ship(ship)

    for ship in enemy_ships:
        enemy_board.place_ship([tuple(cell) for cell in ship])  # converte listas para tuplas

    turn_queue = Queue()
    if is_server:
        turn_queue.put("self")
        turn_queue.put("enemy")
    else:
        turn_queue.put("enemy")
        turn_queue.put("self")

    game_over = False

    if sound_config["background"]:
        sound_background.play(-1)

    while not game_over:
        screen.fill((0, 0, 50))
        board.draw(screen, offset_x=50, offset_y=50, reveal=True)
        enemy_board.draw(screen, offset_x=500, offset_y=50, reveal=False)

        draw_text_centered(screen, "VSVSVSVSVSSVVS", 24, (255, 255, 255), 20)
        draw_text_centered(screen, "--------------", 24, (255, 255, 255), 20)

        my_turn = (turn_queue.queue[0] == "self")
        if my_turn:
            draw_text_centered(screen, "Seu turno", 28, (0, 255, 0), 460)
        else:
            draw_text_centered(screen, "Aguardando oponente...", 28, (255, 255, 0), 460)

        pygame.display.flip()

        if my_turn:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    x = (mx - 500) // 40
                    y = (my - 50) // 40
                    if 0 <= x < 10 and 0 <= y < 10:
                        play_sound(sound_pew, sound_config["pew"])
                        cell = (x, y)
                        network.send({"action": "attack", "cell": cell})
                        result = network.receive()
                        if result and "hit" in result:
                            enemy_board.receive_attack(cell)
                            if result["hit"]:
                                play_sound(sound_boom, sound_config["boom"])
                            turn_queue.get()
                            turn_queue.put("enemy")
        else:
            data = network.receive()
            if data:
                if data.get("action") == "attack":
                    cell = tuple(data["cell"])
                    hit = board.receive_attack(cell)
                    network.send({"hit": hit})
                    turn_queue.get()
                    turn_queue.put("self")
                elif data.get("action") == "game_over":
                    game_over = True
                    if data.get("winner"):
                        draw_text_centered(screen, "Você venceu!", 48, (0, 255, 0), 250)
                    else:
                        draw_text_centered(screen, "Você perdeu!", 48, (255, 0, 0), 250)

        # Fim de jogo local
        if board.all_ships_sunk():
            network.send({"action": "game_over", "winner": False})
            game_over = True
            draw_text_centered(screen, "Você perdeu!", 48, (255, 0, 0), 250)
        elif enemy_board.all_ships_sunk():
            network.send({"action": "game_over", "winner": True})
            game_over = True
            draw_text_centered(screen, "Você venceu!", 48, (0, 255, 0), 250)

        clock.tick(30)

    pygame.display.flip()
    pygame.time.wait(3000)
    sound_background.stop()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def wait_for_connection(screen, server):
    font = pygame.font.SysFont(None, 36)
    connected = False
    host_ip = get_local_ip()

    def accept_thread():
        nonlocal connected
        server.accept()
        connected = True

    t = threading.Thread(target=accept_thread)
    t.start()

    while not connected:
        screen.fill((10, 10, 30))
        draw_text_centered(screen, "Aguardando conexão do cliente...", 30, (255, 255, 0), SCREEN_HEIGHT // 2 - 40)
        draw_text_centered(screen, f"IP do HOST: {host_ip}", 30, (255, 255, 0), SCREEN_HEIGHT // 2)
        draw_text_centered(screen, "Pressione ESC para cancelar", 20, (180, 180, 180), SCREEN_HEIGHT // 2 + 40)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False

        time.sleep(0.1)

    return True

def main():
    while True:
        start = StartScreen(screen)
        choice, ip, sound_config = start.run()

        if choice == "Jogo Local":
            import subprocess
            pygame.quit()
            subprocess.run(["python", "battleship.py"])
            continue

        config = Config(screen)
        my_ships = config.run()
        if not my_ships:
            continue  # volta ao menu

        if choice == "Criar Sala (Servidor)":
            server = NetworkServer()
            if not wait_for_connection(screen, server):
                server.close()
                continue
            server.send({"ships": my_ships})
            enemy_data = server.receive()
            if not enemy_data or "ships" not in enemy_data:
                server.close()
                continue
            game_loop(screen, server, is_server=True, sound_config=sound_config,
                      my_ships=my_ships, enemy_ships=enemy_data["ships"])
            server.close()

        elif choice == "Entrar em Sala (Cliente)":
            if not ip:
                continue
            try:
                client = NetworkClient(host=ip)
            except Exception as e:
                screen.fill((0, 0, 0))
                draw_text_centered(screen, f"Erro ao conectar: {e}", 30, (255, 0, 0), SCREEN_HEIGHT // 2)
                pygame.display.flip()
                pygame.time.wait(3000)
                continue
            data = client.receive()
            if not data or "ships" not in data:
                client.close()
                continue
            client.send({"ships": my_ships})
            game_loop(screen, client, is_server=False, sound_config=sound_config,
                      my_ships=my_ships, enemy_ships=data["ships"])
            client.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Erro inesperado:", e)
        import traceback
        traceback.print_exc()
        input("\nPressione ENTER para sair...")