# objects.py
import random
import time
from Utilities import POSITIONS, random_digit, random_letter

class MovingObject:
    def __init__(self, x, y, size, color, text):
        self.x = x
        self.y = y
        self.size = 40  # For collision threshold (~10 pixels)
        self.color = color
        self.original_text = text
        self.text = text
        self.is_target = False
        self.position_index = 0
        self.dx = 0
        self.dy = 0
        self.is_moving = True  # O1 orbits, O2 starts static
        self.stopped = False
        self.last_move_time = -float('inf')  # Immediate move
        self.last_item_time = 0
        #1250 / 128
        #3000 / 150
        self.move_interval = 1800 / 128  # 31.25 ms , reduced from 1800 , now it is approx. 7.8ms per step
        self.item_interval = 300  # 300 ms per digit
        print(f"Initialized {text} at ({x:.2f}, {y:.2f}), move_interval: {self.move_interval}")

    def move(self, current_time):
        if self.stopped:
            print(f"{self.original_text} stopped at ({self.x:.2f}, {self.y:.2f}) at {current_time} ms")
            return
        if not self.is_target and current_time >= self.last_item_time + self.item_interval:
            self.text = random_digit()
            self.last_item_time = current_time

        if self.is_moving and self.position_index is not None:
            if current_time >= self.last_move_time + self.move_interval:
                self.position_index = (self.position_index + 1) % len(POSITIONS)
                self.x, self.y = POSITIONS[self.position_index]
                self.last_move_time = current_time
        elif self.is_moving:
            self.x += self.dx
            self.y += self.dy
        if current_time >= self.last_item_time + self.item_interval and not self.is_target:
            self.text = random_digit()
            #self.text = random_letter() #for random letters , do check random digit as well , KAE
            self.last_item_time = current_time

    def change(self, letter):
        self.text = letter
        self.is_target = True
        print(f"Changed {self.original_text} to target {letter}")

    def reset(self):
        self.text = self.original_text
        self.is_target = False
        print(f"Reset {self.original_text} to {self.text}")

    def distance_to(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx**2 + dy**2)**0.5