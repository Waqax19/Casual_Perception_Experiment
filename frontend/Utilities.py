# utils.py
import random
import math

WIDTH = 900
HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
#a perfect circle
POSITIONS = [
    (400 + 200 * math.cos(2 * math.pi * i / 128), 300 + 200 * math.sin(2 * math.pi * i / 128))
    for i in range(128)
]

def random_digit():
    return str(random.randint(1, 9))

def random_letter():
    return random.choice('ABCDEFGHIJKLMNPQRSTUVWXYZ')

