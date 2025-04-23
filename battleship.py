#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Este é um projeto feito por alunos da Unisul.
Erick Vieira
Patrick Lohn
Rafael Sonoki
Ruan Oliveira

O projeto apresenta uma versão para dois jogadores do clássico jogo: batalha naval.

Requisitos Técnicos Obrigatórios:
- Uso de Listas, Filas e Pilhas
- Análise de Complexidade (Big O)
- Dois jogadores, interface gráfica com Pygame
"""

import random
import sys
import pygame
from pygame.locals import *
from collections import deque  # requisito: fila para turnos (deque)

# ------- Configurações Globais -------
FPS = 30                # frames por segundo
REVEALSPEED = 8         # velocidade de animação de revelação
WINDOWWIDTH = 800
WINDOWHEIGHT = 600
TILESIZE = 40
MARKERSIZE = 40
TEXT_HEIGHT = 25
TEXT_LEFT_POSN = 10
BOARDWIDTH = 10
BOARDHEIGHT = 10
DISPLAYWIDTH = 200
EXPLOSIONSPEED = 10

XMARGIN = (WINDOWWIDTH - (BOARDWIDTH * TILESIZE) - DISPLAYWIDTH - MARKERSIZE) // 2
YMARGIN = (WINDOWHEIGHT - (BOARDHEIGHT * TILESIZE) - MARKERSIZE) // 2

# Cores (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 204, 0)
GRAY = (60, 60, 60)
BLUE = (0, 50, 255)
YELLOW = (255, 255, 0)
DARKGRAY = (40, 40, 40)

# Tema de cores
BGCOLOR = GRAY
TEXTCOLOR = WHITE
TILECOLOR = GREEN
SHIPCOLOR = YELLOW
HIGHLIGHTCOLOR = BLUE


def main():
    """
    Inicializa Pygame, janela, fontes e recursos.
    Requisito: código funcional e bem estruturado.
    """
    pygame.init()
    global DISPLAYSURF, FPSCLOCK, BASICFONT, BIGFONT
    global HELP_SURF, HELP_RECT, NEW_SURF, NEW_RECT, EXPLOSION_IMAGES

    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    FPSCLOCK = pygame.time.Clock()
    BASICFONT = pygame.font.Font('freesansbold.ttf', 20)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 50)
    pygame.display.set_caption('Batalha Naval - Dois Jogadores')

    # Botões NOVO JOGO e AJUDA – interface gráfica
    NEW_SURF = BASICFONT.render('NOVO JOGO', True, TEXTCOLOR)
    NEW_RECT = NEW_SURF.get_rect()
    NEW_RECT.topleft = (WINDOWWIDTH - NEW_RECT.width - 20, 10)
    HELP_SURF = BASICFONT.render('AJUDA', True, TEXTCOLOR)
    HELP_RECT = HELP_SURF.get_rect()
    HELP_RECT.topleft = (NEW_RECT.left - HELP_RECT.width - 20, 10)

    # Carrega animações de explosão – recursos gráficos
    EXPLOSION_IMAGES = [pygame.image.load(f'img/blowup{i}.png') for i in range(1, 7)]

    # Loop principal para reiniciar o jogo
    while True:
        vencedor, tiros = run_game()
        show_gameover_screen(vencedor, tiros)


def run_game():
    """
    Loop principal de jogo para dois jogadores.
    Usa listas, fila e pilha. Retorna (vencedor, número_de_tiros).

    Complexidade:
    - deque.rotate(): O(1)
    - action_stack append/pop: O(1)
    - check_for_win (varredura 10×10): O(n²)
    """
    # Listas: jogadores e lista de navios
    players = ['Jogador 1', 'Jogador 2']             # requisito: lista
    # Fila (deque) para alternância de turnos
    turn_queue = deque(players)                       # requisito: fila
    # Pilha para histórico de ações (undo futuro)
    action_stack = []                                 # requisito: pilha

    # Gera tabuleiros e estados de revelação de cada jogador
    boards = {p: generate_default_tiles(None) for p in players}   # matriz 10×10 via lista de listas
    revealed = {p: generate_default_tiles(False) for p in players}
    ship_list = [
        'battleship', 'cruiser1', 'cruiser2',
        'destroyer1', 'destroyer2', 'destroyer3',
        'submarine1', 'submarine2', 'submarine3', 'submarine4'
    ]
    for p in players:
        boards[p] = add_ships_to_board(boards[p], ship_list)

    tiros = 0
    xmarkers = {p: set_markers(boards[p])[0] for p in players}
    ymarkers = {p: set_markers(boards[p])[1] for p in players}

    # Loop de turnos até vitória
    while True:
        current = turn_queue[0]
        opponent = turn_queue[1]

        # Desenha interface
        DISPLAYSURF.fill(BGCOLOR)
        DISPLAYSURF.blit(HELP_SURF, HELP_RECT)
        DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
        draw_status(current, tiros)
        draw_board(boards[opponent], revealed[opponent])
        draw_markers(xmarkers[opponent], ymarkers[opponent])
        pygame.display.update()
        FPSCLOCK.tick(FPS)

        # Tratamento de eventos
        clicked = False
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit(); sys.exit()
            if e.type == MOUSEBUTTONUP:
                if HELP_RECT.collidepoint(e.pos):
                    show_help_screen()
                elif NEW_RECT.collidepoint(e.pos):
                    return run_game()
                else:
                    mx, my = e.pos
                    clicked = True

        if clicked:
            tx, ty = get_tile_at_pixel(mx, my)
            if tx is not None and not revealed[opponent][tx][ty]:
                # Registra ação na pilha (O(1))
                action_stack.append((current, opponent, (tx, ty)))
                # Revela célula e animação
                reveal_tile_animation(boards[opponent], [(tx, ty)])
                revealed[opponent][tx][ty] = True
                tiros += 1
                # Verifica acerto e condição de vitória
                if check_revealed_tile(boards[opponent], [(tx, ty)]):
                    blowup_animation(left_top_coords_tile(tx, ty))
                    if check_for_win(boards[opponent], revealed[opponent]):
                        return current, tiros
                # Troca de turno (deque.rotate em O(1))
                turn_queue.rotate(-1)


def draw_status(player, tiros):
    """Desenha texto com jogador atual e contagem de tiros."""
    text = f'Vez: {player}   Tiros: {tiros}'
    surf = BASICFONT.render(text, True, TEXTCOLOR)
    DISPLAYSURF.blit(surf, (10, 10))


def show_help_screen():
    """Exibe instruções de jogo e aguarda tecla para retornar."""
    DISPLAYSURF.fill(BGCOLOR)
    msgs = [
        'Para atirar, clique em uma célula do tabuleiro adversário.',
        'O total de disparos aparece no canto superior esquerdo.',
        'Acertos disparam explosão; erros revelam água.',
        'A vez alterna automaticamente após cada tiro.',
        'Pressione qualquer tecla para voltar.'
    ]
    for i, line in enumerate(msgs):
        surf, rect = make_text_objs(line, BASICFONT, TEXTCOLOR)
        rect.topleft = (TEXT_LEFT_POSN, TEXT_HEIGHT * (i + 2))
        DISPLAYSURF.blit(surf, rect)
    pygame.display.update()
    wait_for_key()


def show_gameover_screen(vencedor, tiros):
    DISPLAYSURF.fill(BGCOLOR)
    msg1 = f'{vencedor} venceu em {tiros} tiros!'
    s1, r1 = make_text_objs(msg1, BIGFONT, TEXTCOLOR)
    r1.center = (WINDOWWIDTH//2, WINDOWHEIGHT//2 - 20)
    DISPLAYSURF.blit(s1, r1)
    msg2 = 'Pressione qualquer tecla para reiniciar'
    s2, r2 = make_text_objs(msg2, BASICFONT, TEXTCOLOR)
    r2.center = (WINDOWWIDTH//2, WINDOWHEIGHT//2 + 20)
    DISPLAYSURF.blit(s2, r2)
    pygame.display.update()
    wait_for_key()


# --- Funções Auxiliares ---

def generate_default_tiles(val):
    """Gera matriz 10×10 preenchida com val (None ou False)."""
    return [[val] * BOARDHEIGHT for _ in range(BOARDWIDTH)]


def blowup_animation(coord):
    """Reproduz sequência de explosão em coord."""
    for img in EXPLOSION_IMAGES:
        frame = pygame.transform.scale(img, (TILESIZE + 10, TILESIZE + 10))
        DISPLAYSURF.blit(frame, coord)
        pygame.display.flip()
        FPSCLOCK.tick(EXPLOSIONSPEED)


def reveal_tile_animation(board, coords):
    """Animação de revelação progressiva do tile."""
    for cov in range(TILESIZE, -REVEALSPEED - 1, -REVEALSPEED):
        draw_tile_covers(board, coords, cov)


def draw_tile_covers(board, coords, cov):
    """Desenha cobertura e revela conteúdo do tile."""
    lx, ly = left_top_coords_tile(coords[0][0], coords[0][1])
    clr = SHIPCOLOR if check_revealed_tile(board, coords) else BGCOLOR
    pygame.draw.rect(DISPLAYSURF, clr, (lx, ly, TILESIZE, TILESIZE))
    if cov > 0:
        pygame.draw.rect(DISPLAYSURF, TILECOLOR, (lx, ly, cov, TILESIZE))
    pygame.display.update()
    FPSCLOCK.tick(FPS)


def check_revealed_tile(board, tile):
    """Retorna True se tile contém navio."""
    return board[tile[0][0]][tile[0][1]] is not None


def check_for_win(board, rev):
    """Verifica se todos os navios foram afundados (nenhuma parte ocult"""
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] is not None and not rev[x][y]:
                return False
    return True


def draw_board(board, rev):
    """Desenha grade e conteúdo de cada tile."""
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            lx, ly = left_top_coords_tile(x, y)
            if not rev[x][y]:
                pygame.draw.rect(DISPLAYSURF, TILECOLOR, (lx, ly, TILESIZE, TILESIZE))
            else:
                c = SHIPCOLOR if board[x][y] is not None else BGCOLOR
                pygame.draw.rect(DISPLAYSURF, c, (lx, ly, TILESIZE, TILESIZE))
    # Linhas da grade
    for i in range(BOARDWIDTH + 1):
        pygame.draw.line(DISPLAYSURF, DARKGRAY,
                         (XMARGIN + MARKERSIZE + i * TILESIZE, YMARGIN + MARKERSIZE),
                         (XMARGIN + MARKERSIZE + i * TILESIZE, WINDOWHEIGHT - YMARGIN))
    for i in range(BOARDHEIGHT + 1):
        pygame.draw.line(DISPLAYSURF, DARKGRAY,
                         (XMARGIN + MARKERSIZE, YMARGIN + MARKERSIZE + i * TILESIZE),
                         (WINDOWWIDTH - (DISPLAYWIDTH + MARKERSIZE * 2), YMARGIN + MARKERSIZE + i * TILESIZE))


def set_markers(board):
    """Conta partes de navio por coluna e por linha."""
    xm = [0] * BOARDWIDTH
    ym = [0] * BOARDHEIGHT
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] is not None:
                xm[x] += 1
                ym[y] += 1
    return xm, ym


def draw_markers(xlist, ylist):
    """
    Desenha os marcadores (números) centralizados ao lado do tabuleiro.
    Uso de listas e lógica gráfica.
    """
    # marcadores de cima
    for i, val in enumerate(xlist):
        text_surf, text_rect = make_text_objs(str(val), BASICFONT, TEXTCOLOR)
        center_x = XMARGIN + MARKERSIZE + i * TILESIZE + TILESIZE / 2
        center_y = YMARGIN + MARKERSIZE / 2
        text_rect.center = (center_x, center_y)
        DISPLAYSURF.blit(text_surf, text_rect)
    # marcadores da esquerda
    for j, val in enumerate(ylist):
        text_surf, text_rect = make_text_objs(str(val), BASICFONT, TEXTCOLOR)
        center_x = XMARGIN + MARKERSIZE / 2
        center_y = YMARGIN + MARKERSIZE + j * TILESIZE + TILESIZE / 2
        text_rect.center = (center_x, center_y)
        DISPLAYSURF.blit(text_surf, text_rect)


def add_ships_to_board(board, ships):
    """Posiciona navios aleatoriamente sem colisões."""
    nb = [row[:] for row in board]
    for sh in ships:
        length = 4 if 'battleship' in sh else 3 if 'cruiser' in sh else 2 if 'destroyer' in sh else 1
        placed = False
        while not placed:
            xs = random.randint(0, BOARDWIDTH - 1)
            ys = random.randint(0, BOARDHEIGHT - 1)
            hor = random.choice([True, False])
            valid, coords = make_ship_position(nb, xs, ys, hor, length, sh)
            if valid:
                for cx, cy in coords:
                    nb[cx][cy] = sh
                placed = True
    return nb


def make_ship_position(board, x, y, hor, length, ship):
    """Calcula se cabe e não colide/adjacente a outro navio."""
    coords = []
    for i in range(length):
        xx = x + i if hor else x
        yy = y if hor else y + i
        if xx >= BOARDWIDTH or yy >= BOARDHEIGHT or board[xx][yy] is not None or hasAdjacent(board, xx, yy, ship):
            return False, []
        coords.append((xx, yy))
    return True, coords


def hasAdjacent(board, x, y, ship):
    """Verifica se há navios adjacentes (8 direções)."""
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < BOARDWIDTH and 0 <= ny < BOARDHEIGHT:
                if board[nx][ny] not in (ship, None):
                    return True
    return False


def left_top_coords_tile(tx, ty):
    """Converte (tilex, tiley) em coordenadas de pixel (left, top)."""
    return (
        tx * TILESIZE + XMARGIN + MARKERSIZE,
        ty * TILESIZE + YMARGIN + MARKERSIZE
    )


def get_tile_at_pixel(x, y):
    """Retorna (tilex, tiley) ou (None, None) dado pixel (x,y)."""
    for tx in range(BOARDWIDTH):
        for ty in range(BOARDHEIGHT):
            lx, ly = left_top_coords_tile(tx, ty)
            if pygame.Rect(lx, ly, TILESIZE, TILESIZE).collidepoint(x, y):
                return tx, ty
    return None, None


def make_text_objs(text, font, color):
    """Cria Surface e Rect para texto."""
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def wait_for_key():
    """Aguarda qualquer tecla ou clique para continuar."""
    while True:
        for e in pygame.event.get():
            if e.type in (KEYDOWN, MOUSEBUTTONUP):
                return


if __name__ == '__main__':
    main()
