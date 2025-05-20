"""
Módulo com a lógica de Batalha Naval:
- Geração de tabuleiro
- Posicionamento aleatório de navios sem colisões
- Verificação de acerto (hit) e vitória
- Cálculo de marcadores (número de partes de navio por linha/coluna)
"""
import random

# Dimensões do tabuleiro
BOARDWIDTH = 10
BOARDHEIGHT = 10

# Lista de navios e suas identificações
ship_list = [
    'battleship',
    'cruiser1', 'cruiser2',
    'destroyer1', 'destroyer2', 'destroyer3',
    'submarine1', 'submarine2', 'submarine3', 'submarine4'
]


def generate_default_tiles(val):
    """Gera matriz BOARDWIDTH × BOARDHEIGHT preenchida com 'val'."""
    return [[val for _ in range(BOARDHEIGHT)] for _ in range(BOARDWIDTH)]


def has_adjacent(board, x, y):
    """Retorna True se há navio em qualquer célula adjacente a (x,y)."""
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < BOARDWIDTH and 0 <= ny < BOARDHEIGHT:
                if board[nx][ny] is not None:
                    return True
    return False


def make_ship_position(board, x, y, hor, length):
    """
    Verifica se um navio de 'length' cabe em (x,y) na orientação 'hor'.
    Retorna (valid, coords) onde coords é lista de tuplas (x,y).
    """
    coords = []
    for i in range(length):
        nx = x + i if hor else x
        ny = y if hor else y + i
        # verifica limites e colisões
        if (
            nx >= BOARDWIDTH or ny >= BOARDHEIGHT
            or board[nx][ny] is not None
            or has_adjacent(board, nx, ny)
        ):
            return False, []
        coords.append((nx, ny))
    return True, coords


def add_ships_to_board(board, ships):
    """
    Posiciona aleatoriamente cada navio de 'ships' no tabuleiro sem colisões.
    Retorna nova matriz 'nb' com valores None ou identificador de navio.
    """
    nb = [row[:] for row in board]
    for sh in ships:
        # define tamanho conforme navio
        if 'battleship' in sh:
            length = 4
        elif 'cruiser' in sh:
            length = 3
        elif 'destroyer' in sh:
            length = 2
        else:
            length = 1
        placed = False
        while not placed:
            xs = random.randint(0, BOARDWIDTH - 1)
            ys = random.randint(0, BOARDHEIGHT - 1)
            hor = random.choice([True, False])
            valid, coords = make_ship_position(nb, xs, ys, hor, length)
            if valid:
                for cx, cy in coords:
                    nb[cx][cy] = sh
                placed = True
    return nb


def check_revealed_tile(board, x, y):
    """Retorna True se há navio na posição (x,y) no tabuleiro 'board'."""
    return board[x][y] is not None


def check_for_win(board, revealed):
    """
    Retorna True se todos os navios em 'board' foram revelados
    conforme o boolean matrix 'revealed'.
    """
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] is not None and not revealed[x][y]:
                return False
    return True


def set_markers(board):
    """
    Retorna dois vetores (xm, ym) com a contagem de partes de navio
    em cada coluna (xm) e linha (ym) do tabuleiro.
    """
    xm = [0] * BOARDWIDTH
    ym = [0] * BOARDHEIGHT
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] is not None:
                xm[x] += 1
                ym[y] += 1
    return xm, ym
