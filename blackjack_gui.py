# blackjack_gui.py
# I made this because I'm convinced that blackjack apps which have a monetization
# scheme will play unfairly in order to get players to put USD into the game.

# This is the GUI version of the blackjack.py backend.

import random
import os
import sys
import csv
import math
import statistics
import time
import pygame
import pygame.freetype

pygame.init()
screen_width = 600
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
my_font = pygame.freetype.SysFont('Helvetica', 24)
clock = pygame.time.Clock()


is_blue = True
x = screen_width * 3 // 4
y = -20


class Card:
    def __init__(self, rank, suit, sets):
        self.rank = rank
        self.suit = suit
        self.sets = sets
        if rank in range(1, 14):
            self.value = rank
        if rank in ['J', 'Q', 'K']:
            self.value = 10
        if rank == 'A':
            self.value = 11

        # This is the "shuffle card" which when drawn indicates that the end of the
        # deck is coming up and a new deck is needed.
        if rank == 0:
            self.rank = suit
            self.suit = suit
            self.value = suit


continue_play = True

while continue_play:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            continue_play = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            is_blue = not is_blue

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_UP]: y -= 3
    if pressed[pygame.K_DOWN]: y += 3
    if pressed[pygame.K_LEFT]: x -= 3
    if pressed[pygame.K_RIGHT]: x += 3

    if is_blue:
        color = (255, 255, 255)
    else:
        color = (255, 255, 255)

    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, color, pygame.Rect(x, y, 60, 60))

    pygame.display.flip()
    clock.tick(60)

# Psuedo Code

# Input Phase:
    # while pre_hand:
        # displaying quit and change bet and deal

    # while player hand:
        # displaying hit and stand and double and split

    # while post hand:
        # displaying quit and change bet and deal