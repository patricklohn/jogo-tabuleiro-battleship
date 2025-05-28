import pygame
import sys
import threading
import time
import os
from queue import Queue
from start_screen import StartScreen
from network import NetworkServer, NetworkClient
from board import Board
from config import Config
import socket

pygame.init()
pygame.font.init()
pygame.mixer.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 750
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Batalha Naval")

# Carregar sons
sound_pew = pygame.mixer.Sound("assets/sounds/pew.wav")
sound_boom = pygame.mixer.Sound("assets/sounds/boom.wav")
sound_background = pygame.mixer.Sound("assets/sounds/background.wav")

history = []
HISTORY_FILE = "history.txt"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def save_history_to_file():
    try:
        with open(HISTORY_FILE, "w") as f:
            for h, c in history:
                f.write(f"{h},{c}\n")
    except Exception as e:
        print("Erro ao salvar histórico:", e)

def load_history_from_file():
    if not os.path.isfile(HISTORY_FILE):
        return
    try:
        with open(HISTORY_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(",")
                    if len(parts) == 2:
                        history.append((parts[0], parts[1]))
    except Exception as e:
        print("Erro ao carregar histórico:", e)

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

    # Posicionar navios no tabuleiro
    for ship in my_ships:
        board.place_ship(ship)
    for ship in enemy_ships:
        enemy_board.place_ship([tuple(cell) for cell in ship])

    # Definir fila de turno: servidor começa (self) ou cliente
    turn_queue = Queue()
    if is_server:
        turn_queue.put("self")
        turn_queue.put("enemy")
    else:
        turn_queue.put("enemy")
        turn_queue.put("self")

    game_over = False
    winner = None

    # Tocar música de fundo se habilitada
    if sound_config.get("background", True):
        sound_background.play(-1)

    while not game_over:
        screen.fill((0, 0, 50))
        # Mostrar tabuleiros
        board.draw(screen, offset_x=50, offset_y=50, reveal=True)
        enemy_board.draw(screen, offset_x=500, offset_y=50, reveal=False)

        draw_text_centered(screen, "Seu Tabuleiro", 24, (255, 255, 255), 20)
        draw_text_centered(screen, "Tabuleiro Inimigo", 24, (255, 255, 255), 20)

        my_turn = (turn_queue.queue[0] == "self")
        if my_turn:
            draw_text_centered(screen, "Seu turno", 28, (0, 255, 0), 460)
        else:
            draw_text_centered(screen, "Aguardando oponente...", 28, (255, 255, 0), 460)

        pygame.display.flip()

        # Processar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sound_background.stop()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and my_turn:
                mx, my = event.pos
                x = (mx - 500) // 40
                y = (my - 50) // 40
                if 0 <= x < 10 and 0 <= y < 10:
                    cell = (x, y)
                    play_sound(sound_pew, sound_config.get("pew", True))
                    try:
                        network.send({"action": "attack", "cell": cell})
                        result = network.receive(timeout=5)  # espera resposta até 5s
                    except Exception:
                        result = None
                    if result and "hit" in result:
                        enemy_board.receive_attack(cell)
                        if result["hit"]:
                            play_sound(sound_boom, sound_config.get("boom", True))
                        # Alterna turno
                        turn_queue.get()
                        turn_queue.put("enemy")

        # Turno do oponente: aguardar e processar dados
        if not my_turn:
            try:
                data = network.receive(timeout=0.1)  # espera rápida
            except Exception:
                data = None
            if data:
                if data.get("action") == "attack":
                    cell = tuple(data["cell"])
                    hit = board.receive_attack(cell)
                    network.send({"hit": hit})
                    turn_queue.get()
                    turn_queue.put("self")
                elif data.get("action") == "game_over":
                    game_over = True
                    winner = "self" if data.get("winner") else "enemy"

        # Verificar vitória
        if board.all_ships_sunk():
            try:
                network.send({"action": "game_over", "winner": False})
            except Exception:
                pass
            game_over = True
            winner = "enemy"
        elif enemy_board.all_ships_sunk():
            try:
                network.send({"action": "game_over", "winner": True})
            except Exception:
                pass
            game_over = True
            winner = "self"

        clock.tick(30)

    # Final do jogo: mostrar resultado e salvar histórico
    screen.fill((0, 0, 50))
    if winner == "self":
        draw_text_centered(screen, "Você venceu!", 48, (0, 255, 0), SCREEN_HEIGHT // 2)
        history.append(("V", "X") if is_server else ("X", "V"))
    else:
        draw_text_centered(screen, "Você perdeu!", 48, (255, 0, 0), SCREEN_HEIGHT // 2)
        history.append(("X", "V") if is_server else ("V", "X"))

    save_history_to_file()
    pygame.display.flip()
    pygame.time.wait(3000)
    sound_background.stop()

def draw_history(screen, history):
    screen.fill((0, 0, 50))
    draw_text_centered(screen, "Histórico de Partidas", 40, (255, 255, 255), 50)

    header = "Host       |     Client"
    font = pygame.font.SysFont(None, 28)
    header_text = font.render(header, True, (255, 255, 255))
    screen.blit(header_text, (SCREEN_WIDTH // 2 - header_text.get_width() // 2, 100))

    for i, (h, c) in enumerate(history):
        line = f"   {h}              {c}"
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 140 + i * 30))

    pygame.display.flip()
    pygame.time.wait(4000)

def wait_for_connection(screen, server):
    font = pygame.font.SysFont(None, 36)
    connected = False

    def accept_thread():
        nonlocal connected
        try:
            server.accept()
            connected = True
        except Exception as e:
            print("Erro ao aceitar conexão:", e)
            connected = False

    t = threading.Thread(target=accept_thread)
    t.start()

    while not connected:
        screen.fill((10, 10, 30))
        draw_text_centered(screen, "Aguardando conexão do cliente...", 30, (255, 255, 0), SCREEN_HEIGHT // 2)
        draw_text_centered(screen, "IP do HOST:", 30, (255, 255, 0), SCREEN_HEIGHT // 2)
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
    load_history_from_file()

    while True:
        start = StartScreen(screen)

        result = start.run()
        if isinstance(result, tuple) and len(result) == 3:
            choice, ip, sound_config = result
        elif isinstance(result, tuple) and len(result) == 2:
            choice, ip = result
            sound_config = {"pew": True, "boom": True, "background": True}
        else:
            choice = None
            ip = None
            sound_config = {"pew": True, "boom": True, "background": True}

        if choice == "Sair":
            pygame.quit()
            sys.exit()  # Encerra o programa imediatamente

        elif choice == "Ver histórico":
            draw_history(screen, history)
            continue  # Volta direto para o menu, sem pedir para escolher barcos

        elif choice == "Jogo Local":
            import subprocess
            pygame.quit()
            subprocess.run(["python", "battleship.py"])
            continue

        config = Config(screen)
        my_ships = config.run()
        if not my_ships:
            continue

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
    main()
