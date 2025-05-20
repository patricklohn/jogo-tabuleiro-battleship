"""
Servidor TCP para Batalha Naval multiplayer.
Aceita 2 jogadores, coordena estado do jogo e envia resultados.
"""
import socket
import json
from game_logic import *

HOST = '0.0.0.0'
PORT = 5000


def run_server():
    """Inicializa o servidor, aceita conexões e inicia o loop de jogo."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(2)
    print(f"[Servidor] Aguardando 2 jogadores em {HOST}:{PORT}...")

    conns = []
    for i in range(2):
        conn, addr = srv.accept()
        print(f"[Servidor] Jogador {i} conectado de {addr}")
        conns.append(conn)

    # Estado inicial do jogo
    boards = {
        0: add_ships_to_board(generate_default_tiles(None), ship_list),
        1: add_ships_to_board(generate_default_tiles(None), ship_list)
    }
    revealed = {
        0: generate_default_tiles(False),
        1: generate_default_tiles(False)
    }
    turn = 0  # índice do jogador que joga

    # Loop principal de jogo
    while True:
        data = conns[turn].recv(1024)
        if not data:
            print("[Servidor] Conexão encerrada prematuramente.")
            break
        jogada = json.loads(data.decode())
        x, y = jogada['x'], jogada['y']

        # Verifica acerto
        hit = check_revealed_tile(boards[1-turn], x, y)
        revealed[1-turn][x][y] = True

        # Verifica se afundou navio
        sunk = None
        if hit:
            for sh in ship_list:
                coords = [ (i,j)
                          for i in range(BOARDWIDTH)
                          for j in range(BOARDHEIGHT)
                          if boards[1-turn][i][j] == sh ]
                if coords and all(revealed[1-turn][i][j] for i,j in coords):
                    sunk = sh

        # Verifica vitória
        game_over = check_for_win(boards[1-turn], revealed[1-turn])

        # Prepara resposta JSON
        resp = {
            'tipo': 'resultado',
            'x': x, 'y': y,
            'hit': hit,
            'sunk': sunk,
            'game_over': game_over,
            'next_player': 1-turn
        }
        msg = json.dumps(resp).encode()

        # Envia a ambos jogadores
        for c in conns:
            c.send(msg)

        if game_over:
            print(f"[Servidor] Jogo encerrado! Jogador {turn} venceu.")
            break

        # Alterna a vez
        turn = 1 - turn

    # Fecha conexões
    for c in conns:
        c.close()
    srv.close()


if __name__ == '__main__':
    run_server()
