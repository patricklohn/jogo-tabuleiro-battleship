#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Este é um projeto feito por alunos da Unisul.
Erick Vieira
Patrick Lohn
Rafael Sonoki
Ruan Oliveira

Versão para dois jogadores do clássico jogo: Batalha Naval.
Requisitos Técnicos: listas, filas, pilhas, análise Big O, interface Pygame.
"""

import random
import sys
import pygame
import os
from pygame.locals import *
from collections import deque  # fila para turnos

# ------- Configurações Globais -------
FPS = 30
REVEALSPEED = 8
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
RED = (255, 0, 0)
DARKGRAY = (40, 40, 40)

# Tema de cores
BGCOLOR = GRAY
TEXTCOLOR = WHITE
TILECOLOR = GREEN
SHIPCOLOR = YELLOW
HIGHLIGHTCOLOR = BLUE

# Flags de áudio
SOUND_ON = True
MUSIC_ON = True


def main():
    """
    Inicializa Pygame, mixer, janela, fontes e recursos.
    Inclui música de fundo opcional e botões de configuração.
    """
    pygame.init()
    pygame.mixer.init()
    global DISPLAYSURF, FPSCLOCK, BASICFONT, BIGFONT
    global NEW_SURF, NEW_RECT, HELP_SURF, HELP_RECT, CONFIG_SURF, CONFIG_RECT
    global SHOT_SOUND, EXPLOSION_SOUND, EXPLOSION_IMAGES

    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    FPSCLOCK = pygame.time.Clock()
    BASICFONT = pygame.font.Font('freesansbold.ttf', 20)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 50)
    pygame.display.set_caption('Batalha Naval - Dois Jogadores')

    # Carrega e toca música de fundo
    bg_path = os.path.join('sound', 'background.wav')
    if MUSIC_ON and os.path.exists(bg_path):
        pygame.mixer.music.load(bg_path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

    # Botões NOVO JOGO, CONFIG e AJUDA
    NEW_SURF = BASICFONT.render('NOVO JOGO', True, TEXTCOLOR)
    NEW_RECT = NEW_SURF.get_rect(topleft=(WINDOWWIDTH - NEW_SURF.get_width() - 20, 10))
    CONFIG_SURF = BASICFONT.render('CONFIG', True, TEXTCOLOR)
    CONFIG_RECT = CONFIG_SURF.get_rect(topleft=(NEW_RECT.left - CONFIG_SURF.get_width() - 20, 10))
    HELP_SURF = BASICFONT.render('AJUDA', True, TEXTCOLOR)
    HELP_RECT = HELP_SURF.get_rect(topleft=(CONFIG_RECT.left - HELP_SURF.get_width() - 20, 10))

    # Sons de efeitos
    SHOT_SOUND = pygame.mixer.Sound(os.path.join('sound', 'pew.wav'))
    EXPLOSION_SOUND = pygame.mixer.Sound(os.path.join('sound', 'boom.wav'))
    # Animações de explosão
    EXPLOSION_IMAGES = [pygame.image.load(f'img/blowup{i}.png') for i in range(1, 7)]

    while True:
        vencedor, tiros = run_game()
        show_gameover_screen(vencedor, tiros)


def show_settings_screen():
    """
    Tela de configurações para ativar/desativar som e música,
    redesenhando após cada comando para refletir o novo estado.
    """
    global SOUND_ON, MUSIC_ON
    while True:
        # Limpa fundo
        DISPLAYSURF.fill(BGCOLOR)

        # Opções atualizadas
        options = [
            f"Efeitos Sonoros: {'On' if SOUND_ON else 'Off'}",
            f"Música de Fundo: {'On' if MUSIC_ON else 'Off'}",
            "Pressione S para Som, M para Música, qualquer outra tecla para sair."
        ]

        # Desenha cada linha
        for i, text in enumerate(options):
            surf, rect = make_text_objs(text, BASICFONT, TEXTCOLOR)
            rect.center = (
                WINDOWWIDTH // 2,
                WINDOWHEIGHT // 3 + i * (TEXT_HEIGHT * 2)
            )
            DISPLAYSURF.blit(surf, rect)

        pygame.display.update()

        # Aguarda evento
        ev = pygame.event.wait()
        if ev.type == KEYDOWN:
            if ev.key == K_s:
                SOUND_ON = not SOUND_ON
            elif ev.key == K_m:
                MUSIC_ON = not MUSIC_ON
                if MUSIC_ON:
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.pause()
            else:
                # Qualquer outra tecla sai da tela de configurações
                break

    # Espera interação
    while True:
        ev = pygame.event.wait()
        if ev.type == KEYDOWN:
            if ev.key == K_s:
                SOUND_ON = not SOUND_ON
            elif ev.key == K_m:
                MUSIC_ON = not MUSIC_ON
                if MUSIC_ON:
                    pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.pause()
            else:
                break
    # Retorna após ajuste


def run_game():
    """
    Loop principal para dois jogadores.
    Usa listas, fila e pilha. Retorna (vencedor, tiros).
    Big O: deque.rotate() O(1), append/pop O(1), vitória O(n^2).
    """
    players = ['Jogador 1', 'Jogador 2']
    turn_queue = deque(players)
    action_stack = []

    boards = {p: generate_default_tiles(None) for p in players}
    revealed = {p: generate_default_tiles(False) for p in players}
    ship_list = ['battleship','cruiser1','cruiser2',
                 'destroyer1','destroyer2','destroyer3',
                 'submarine1','submarine2','submarine3','submarine4']
    for p in players:
        boards[p] = add_ships_to_board(boards[p], ship_list)

    ship_positions = {p: {} for p in players}
    for p in players:
        for sh in ship_list:
            ship_positions[p][sh] = [(x,y) for x in range(BOARDWIDTH) for y in range(BOARDHEIGHT)
                                     if boards[p][x][y] == sh]

    tiros = 0
    xmarkers = {p: set_markers(boards[p])[0] for p in players}
    ymarkers = {p: set_markers(boards[p])[1] for p in players}

    while True:
        current = turn_queue[0]
        opponent = turn_queue[1]

        DISPLAYSURF.fill(BGCOLOR)
        DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
        DISPLAYSURF.blit(CONFIG_SURF, CONFIG_RECT)
        DISPLAYSURF.blit(HELP_SURF, HELP_RECT)
        draw_status(current, tiros)
        draw_board(boards[opponent], revealed[opponent])
        draw_markers(xmarkers[opponent], ymarkers[opponent])
        pygame.display.update()
        FPSCLOCK.tick(FPS)

        clicked = False; mx=my=None
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit(); sys.exit()
            if e.type == MOUSEBUTTONUP:
                if NEW_RECT.collidepoint(e.pos):
                    return run_game()
                elif CONFIG_RECT.collidepoint(e.pos):
                    show_settings_screen()
                elif HELP_RECT.collidepoint(e.pos):
                    show_help_screen()
                else:
                    mx,my=e.pos; clicked=True

        if clicked and mx is not None:
            tx,ty = get_tile_at_pixel(mx,my)
            if tx is not None and not revealed[opponent][tx][ty]:
                if SOUND_ON: SHOT_SOUND.play()
                action_stack.append((current,opponent,(tx,ty)))
                reveal_tile_animation(boards[opponent],[(tx,ty)])
                revealed[opponent][tx][ty]=True
                tiros+=1
                if check_revealed_tile(boards[opponent],[(tx,ty)]):
                    if SOUND_ON: EXPLOSION_SOUND.play()
                    blowup_animation(left_top_coords_tile(tx,ty))
                    ship=boards[opponent][tx][ty]
                    if all(revealed[opponent][x][y] for x,y in ship_positions[opponent][ship]):
                        highlight_sunk_ship(ship_positions[opponent][ship])
                    if check_for_win(boards[opponent],revealed[opponent]):
                        return current,tiros
                turn_queue.rotate(-1)

def highlight_sunk_ship(coords):
    """
    Destaca navio afundado com borda vermelha.
    """
    for x,y in coords:
        left, top = left_top_coords_tile(x, y)
        pygame.draw.rect(DISPLAYSURF, RED, (left, top, TILESIZE, TILESIZE), 3)
    pygame.display.update()
    pygame.time.delay(500)


def draw_status(player, tiros):
    text = f'Vez: {player}   Tiros: {tiros}'
    surf = BASICFONT.render(text, True, TEXTCOLOR)
    DISPLAYSURF.blit(surf, (10, 10))


def show_help_screen():
    DISPLAYSURF.fill(BGCOLOR)
    msgs = [
        '• Para atirar: clique em uma célula do tabuleiro adversário.',
        '• Contador de tiros: canto superior esquerdo.',
        '• Acertos disparam explosão; erros revelam água.',
        '• Turno alterna automaticamente após cada tiro.',
        '• Pressione qualquer tecla para voltar.'
    ]
    panel_w = WINDOWWIDTH - 2 * XMARGIN
    panel_h = len(msgs) * (TEXT_HEIGHT * 2) + 40
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 200))
    panel_rect = panel.get_rect(center=(WINDOWWIDTH//2, WINDOWHEIGHT//2))
    DISPLAYSURF.blit(panel, panel_rect)
    margin_left = panel_rect.left + 20
    margin_top = panel_rect.top + 20
    spacing = TEXT_HEIGHT * 2
    for i, line in enumerate(msgs):
        surf, rect = make_text_objs(line, BASICFONT, TEXTCOLOR)
        rect.topleft = (margin_left, margin_top + i * spacing)
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


def generate_default_tiles(val):
    return [[val] * BOARDHEIGHT for _ in range(BOARDWIDTH)]


def blowup_animation(coord):
    for img in EXPLOSION_IMAGES:
        frame = pygame.transform.scale(img, (TILESIZE + 10, TILESIZE + 10))
        DISPLAYSURF.blit(frame, coord)
        pygame.display.flip()
        FPSCLOCK.tick(EXPLOSIONSPEED)


def reveal_tile_animation(board, coords):
    for cov in range(TILESIZE, -REVEALSPEED-1, -REVEALSPEED):
        draw_tile_covers(board, coords, cov)


def draw_tile_covers(board, coords, cov):
    lx, ly = left_top_coords_tile(coords[0][0], coords[0][1])
    clr = SHIPCOLOR if check_revealed_tile(board, coords) else BGCOLOR
    pygame.draw.rect(DISPLAYSURF, clr, (lx, ly, TILESIZE, TILESIZE))
    if cov > 0:
        pygame.draw.rect(DISPLAYSURF, TILECOLOR, (lx, ly, cov, TILESIZE))
    pygame.display.update()
    FPSCLOCK.tick(FPS)


def check_revealed_tile(board, tile):
    return board[tile[0][0]][tile[0][1]] is not None


def check_for_win(board, rev):
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] is not None and not rev[x][y]:
                return False
    return True


def draw_board(board, rev):
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            lx, ly = left_top_coords_tile(x, y)
            color = TILECOLOR if not rev[x][y] else (SHIPCOLOR if board[x][y] else BGCOLOR)
            pygame.draw.rect(DISPLAYSURF, color, (lx, ly, TILESIZE, TILESIZE))
    for i in range(BOARDWIDTH+1):
        pygame.draw.line(DISPLAYSURF, DARKGRAY,
                         (XMARGIN + MARKERSIZE + i*TILESIZE, YMARGIN + MARKERSIZE),
                         (XMARGIN + MARKERSIZE + i*TILESIZE, WINDOWHEIGHT - YMARGIN))
    for i in range(BOARDHEIGHT+1):
        pygame.draw.line(DISPLAYSURF, DARKGRAY,
                         (XMARGIN + MARKERSIZE, YMARGIN + MARKERSIZE + i*TILESIZE),
                         (WINDOWWIDTH - (DISPLAYWIDTH + MARKERSIZE*2), YMARGIN + MARKERSIZE + i*TILESIZE))


def set_markers(board):
    xm = [0]*BOARDWIDTH
    ym = [0]*BOARDHEIGHT
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] is not None:
                xm[x]+=1; ym[y]+=1
    return xm, ym


def draw_markers(xlist, ylist):
    for i, val in enumerate(xlist):
        surf, rect = make_text_objs(str(val), BASICFONT, TEXTCOLOR)
        rect.center = (XMARGIN + MARKERSIZE + i*TILESIZE + TILESIZE/2,
                       YMARGIN + MARKERSIZE/2)
        DISPLAYSURF.blit(surf, rect)
    for j, val in enumerate(ylist):
        surf, rect = make_text_objs(str(val), BASICFONT, TEXTCOLOR)
        rect.center = (XMARGIN + MARKERSIZE/2,
                       YMARGIN + MARKERSIZE + j*TILESIZE + TILESIZE/2)
        DISPLAYSURF.blit(surf, rect)


def add_ships_to_board(board, ships):
    nb = [row[:] for row in board]
    for sh in ships:
        length = 4 if 'battleship' in sh else 3 if 'cruiser' in sh else 2 if 'destroyer' in sh else 1
        placed=False
        while not placed:
            xs,ys = random.randint(0,BOARDWIDTH-1), random.randint(0,BOARDHEIGHT-1)
            hor = random.choice([True,False])
            valid,coords = make_ship_position(nb,xs,ys,hor,length,sh)
            if valid:
                for cx,cy in coords: nb[cx][cy]=sh
                placed=True
    return nb


def make_ship_position(board, x, y, hor, length, ship):
    coords=[]
    for i in range(length):
        xx = x+i if hor else x; yy = y if hor else y+i
        if xx>=BOARDWIDTH or yy>=BOARDHEIGHT or board[xx][yy] is not None or hasAdjacent(board,xx,yy,ship):
            return False, []
        coords.append((xx,yy))
    return True, coords


def hasAdjacent(board, x, y, ship):
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            nx,ny = x+dx, y+dy
            if 0<=nx<BOARDWIDTH and 0<=ny<BOARDHEIGHT and board[nx][ny] not in (ship,None):
                return True
    return False


def left_top_coords_tile(tx, ty):
    return (tx*TILESIZE + XMARGIN + MARKERSIZE,
            ty*TILESIZE + YMARGIN + MARKERSIZE)


def get_tile_at_pixel(x, y):
    for tx in range(BOARDWIDTH):
        for ty in range(BOARDHEIGHT):
            lx,ly = left_top_coords_tile(tx,ty)
            if pygame.Rect(lx,ly,TILESIZE,TILESIZE).collidepoint(x,y):
                return tx, ty
    return None, None


def make_text_objs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def wait_for_key():
    while True:
        for e in pygame.event.get():
            if e.type in (KEYDOWN, MOUSEBUTTONUP): return


if __name__ == '__main__':
    main()
