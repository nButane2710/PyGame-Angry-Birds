import pygame
import math
import sys
import random

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 1800, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Game")

# Clock
clock = pygame.time.Clock()

# Constants
GRAVITY = 0.5
POWER_SCALE = 0.35
GROUND_LEVEL = HEIGHT - 100


NOOFCOLLISIONS=0

CATAPULT_POS = [(400, GROUND_LEVEL - 200), (1400, GROUND_LEVEL - 200)]

BIRD_RADIUS = 10

MAX_DRAG_DISTANCE = 100

BIRD_TYPES = ['ChuckBird', 'BluesBird', 'BombBird', 'BaseBird']

HAND_POSITIONS = [[], []]

ROWS_BLOCKS = 10
'''
COLUMNS_BLOCKS = 4
'''
# BIRD_DAMAGE_PROFILE = {
#     'BaseBird':   {'wood': 50, 'stone': 50, 'ice': 50},
#     'ChuckBird':  {'wood': 75, 'stone': 25, 'ice': 25},
#     'BombBird':   {'wood': 25, 'stone': 75, 'ice': 25},
#     'BluesBird':  {'wood': 25, 'stone': 25, 'ice': 50}
# }
#
BIRD_DAMAGE_PROFILE = {
    'BaseBird':   {'wood': 200, 'stone': 200, 'ice': 200},
    'ChuckBird':  {'wood': 200, 'stone': 200, 'ice': 200},
    'BombBird':   {'wood': 200, 'stone': 200, 'ice': 200},
    'BluesBird':  {'wood': 200, 'stone': 200, 'ice': 200}
}
# 

# Player class
class Player:
    def __init__(self, name, index):
        self.name = name
        self.index = index
        self.available_birds = random.choices(BIRD_TYPES, k=3)  # list of Bird instances
        self.blocks = []  # fortress blocks

    def get_next_bird(self):
        bird_type = self.available_birds.pop(0)
        self.available_birds.append(random.choice(BIRD_TYPES))
        return bird_type


# Bird class
class Bird:
    def __init__(self, x, y, vx, vy, player, colour=(255, 0, 0)):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.player = player
        self.radius = 10
        self.alive = True

 
        self.collisions=0
        self.colour = colour


    def update(self):
        if not self.alive:
            return
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY


        if self.y + self.radius >= GROUND_LEVEL:
            self.y = GROUND_LEVEL - self.radius


            if  self.collisions < NOOFCOLLISIONS:
                self.vy *= -0.9
                self.collisions+=1
            else:
                self.vy = 0
                self.vx = 0
                self.alive = False



    def draw(self, surface):
        bird_colour = self.colour
        pygame.draw.circle(surface, bird_colour, (int(self.x), int(self.y)), self.radius)

    def activate(self):
        pass

class BaseBird(Bird):
    colour = (255, 0, 0)

    def __init__(self, x, y, vx, vy, player):
        super().__init__(x, y, vx, vy, player, colour=self.colour)

    def activate(self):
        pass

class ChuckBird(Bird):
    colour=(255, 255, 0)

    def __init__(self, x, y, vx, vy, player):
        super().__init__(x, y, vx, vy, player, colour=self.colour)

    def activate(self):
        pass

class BluesBird(Bird):
    colour=(0, 0, 255)

    def __init__(self, x, y, vx, vy, player):
        super().__init__(x, y, vx, vy, player, colour=self.colour)

    def activate(self):

        pass

class BombBird(Bird):
    colour=(0, 0, 0)

    def __init__(self, x, y, vx, vy, player):
        super().__init__(x, y, vx, vy, player, colour=self.colour)

    def activate(self):

        pass


class Block:
    def __init__(self, x, y, width, height, material):
        self.rect = pygame.Rect(x, y, width, height)
        self.material = material  # "wood", "stone", "ice"
        self.max_hp = {"wood": 100, "stone": 200, "ice": 50}[material]
        self.hp = self.max_hp
        self.color = {"wood": (139, 69, 19), "stone": (128, 128, 128), "ice": (135, 206, 235)}[material]


    def draw(self, surface):
        # Draw filled block
        pygame.draw.rect(surface, self.color, self.rect)

        # Draw border (black outline)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)  # 2 = border thickness

        # Draw health bar if not full
        health_ratio = self.hp / self.max_hp
        if health_ratio < 1:
            bar_width = self.rect.width * health_ratio
            pygame.draw.rect(surface, (255, 0, 0), (self.rect.x, self.rect.y - 6, bar_width, 5))

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            return True  # Block is destroyed
        return False


def generate_random_fortress(player, num_blocks=20):
    x_range = (100, 300) if player.index == 0 else (1500, 1700)
    block_width = 50
    block_height = 50

    for row in range(ROWS_BLOCKS):
        for column in range(4):
            material = random.choice(["wood", "stone", "ice"])
            x = x_range[0] + column * block_width
            y = GROUND_LEVEL - (row + 1) * block_height
            block = Block(x, y, block_width, block_height, material)
            player.blocks.append(block)






def switch_turn():
    global current_player_index
    current_player_index = (current_player_index+1)%2


def draw_hand(player):
    x_start = CATAPULT_POS[player.index][0] 
    y_start = GROUND_LEVEL + 40
    HAND_POSITIONS[player.index] = []

    direction = -1 if player.index == 0 else +1

    for i, bird_type_name in enumerate(player.available_birds):
        x = x_start + direction*(100 + i*50)
        y = y_start
        bird_class = globals()[bird_type_name]
        pygame.draw.circle(screen, bird_class.colour, (x, y), BIRD_RADIUS )
        HAND_POSITIONS[player.index].append((x, y))


def draw_catapult_base(surface, pos):
    x, y = pos  # catapult base center

    brown = (139, 69, 19)  # wood brown

    arm_length = 120
    arm_thickness = 7
    vertical_length = 100

    # Left arm
    pygame.draw.line(surface, brown, (x, y), (x - 12, y - arm_length), arm_thickness)

    # Right arm
    pygame.draw.line(surface, brown, (x, y), (x + 12, y - arm_length), arm_thickness)

    # Vertical base
    pygame.draw.line(surface, brown, (x, y), (x, y + vertical_length), arm_thickness)





# Drag control variables
dragging = False
drag_start = (0, 0)
drag_current = (0, 0)
bird = None
bird_launched = False

players = [Player("Player 1", 0), Player("Player 2", 1)]
current_player_index = 0

generate_random_fortress(players[0])
generate_random_fortress(players[1])

turn_swiched = False

#
show_line_variable = False
#

temp_hand=[]
temp_hand_pos=[]




# Game loop
running = True
while running:
    screen.fill((150, 255, 255))  # Sky blue
    pygame.draw.rect(screen, (50, 200, 50), (0, GROUND_LEVEL, WIDTH, 100))  # Ground

    draw_hand(players[0])
    draw_hand(players[1])

    draw_catapult_base(screen, (CATAPULT_POS[0][0], CATAPULT_POS[0][1]+100))
    draw_catapult_base(screen, (CATAPULT_POS[1][0], CATAPULT_POS[1][1]+100))

    for player in players:
        for block in player.blocks:
            block.draw(screen)


    # Create a bird only if none exists and it's not launched
    if not bird_launched and bird is None:

        bird_type_name = players[current_player_index].get_next_bird()
        bird_class = globals()[bird_type_name]
        bird = bird_class(CATAPULT_POS[current_player_index][0], CATAPULT_POS[current_player_index][1], 0, 0, players[current_player_index])

        ####<<<<<<<<<<<<<<<<<<<<<<<
        temp_hand.clear()
        ####<<<<<<<<<<<<<<<<<<<<<<<
        
        temp_hand.append(bird_type_name)
        temp_hand += players[current_player_index].available_birds




    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Start dragging
        elif event.type == pygame.MOUSEBUTTONDOWN and not bird_launched:
            mouse_pos = pygame.mouse.get_pos()
            mx, my = mouse_pos

            player_index = current_player_index
            catapult_x, catapult_y = CATAPULT_POS[player_index]

            for i, (hx, hy) in enumerate(HAND_POSITIONS[player_index]):
                dx = mx - hx
                dy = my - hy
                if dx*dx + dy*dy <= BIRD_RADIUS*BIRD_RADIUS:
                    players[player_index].available_birds[i] = temp_hand[0]

                    bird_type_name = temp_hand[i+1]
                    bird_class = globals()[bird_type_name]
                    bird = bird_class(catapult_x, catapult_y, 0, 0, players[player_index])

                    temp_hand[0], temp_hand[i+1] = temp_hand[i+1], temp_hand[0]
                    break



            dx = mouse_pos[0] - CATAPULT_POS[current_player_index][0]
            dy = mouse_pos[1] - CATAPULT_POS[current_player_index][1]
            if dx*dx + dy*dy <= BIRD_RADIUS*BIRD_RADIUS:
                dragging = True
                drag_start = CATAPULT_POS[current_player_index]
                drag_current = mouse_pos

                bird = bird_class(drag_current[0], drag_current[1], 0, 0, players[current_player_index])

        # Update drag position
        elif event.type == pygame.MOUSEMOTION and dragging:
            drag_current = pygame.mouse.get_pos()

            raw_mouse_pos = pygame.mouse.get_pos()

            delx = raw_mouse_pos[0] - drag_start[0]
            dely = raw_mouse_pos[1] - drag_start[1]
            distance = math.hypot(delx, dely)

            if distance > MAX_DRAG_DISTANCE:
                scale_factor = MAX_DRAG_DISTANCE / distance
                delx *= scale_factor
                dely *= scale_factor

            drag_current = (drag_start[0] + delx, drag_start[1] + dely)

            #
            show_line_variable = True
            #
            
            bird = bird_class(drag_current[0], drag_current[1], 0, 0, players[current_player_index])


        # Release to launch
        elif event.type == pygame.MOUSEBUTTONUP and dragging:
            dragging = False

            ###^
            raw_mouse_pos = pygame.mouse.get_pos()

            delx = raw_mouse_pos[0] - drag_start[0]
            dely = raw_mouse_pos[1] - drag_start[1]
            distance = math.hypot(delx, dely)
            
            if distance > MAX_DRAG_DISTANCE:
                scale_factor = MAX_DRAG_DISTANCE / distance
                delx *= scale_factor
                dely *= scale_factor

            drag_end = (drag_start[0] + delx, drag_start[1] + dely)

            dx = drag_start[0] - drag_end[0]
            dy = drag_start[1] - drag_end[1]

            power = math.hypot(dx, dy)
            angle = math.atan2(dy, dx)

            vx = math.cos(angle) * power * POWER_SCALE
            vy = math.sin(angle) * power * POWER_SCALE

            bird_launched = True
            bird = bird_class(CATAPULT_POS[current_player_index][0], CATAPULT_POS[current_player_index][1], vx, vy, players[current_player_index])
            

            ###
            turn_swiched = False
            ###

            ###
            show_line_variable = False
            ###

    # Draw drag line
    if show_line_variable:
        pygame.draw.line(screen, (0, 0, 0), (drag_start[0]-10, drag_start[1]), (drag_current[0]-10, drag_current[1]), 3)
        pygame.draw.line(screen, (0, 0, 0), (drag_start[0]+10, drag_start[1]), (drag_current[0]+10, drag_current[1]), 3)

    if bird and not bird_launched:
        bird.draw(screen)

    # Update and draw bird
    if bird and bird_launched:
        bird.update()

        #############-----------------
        # Check collision with opponent blocks
        opponent = players[1 - current_player_index]
        for block in opponent.blocks[:]:  # Use slice to avoid modifying list while iterating
            if block.rect.collidepoint(int(bird.x), int(bird.y)):
                bird_type = type(bird).__name__
                material = block.material
                damage = BIRD_DAMAGE_PROFILE.get(bird_type, {}).get(material, 0)
                destroyed = block.take_damage(damage)

                if destroyed:
                    opponent.blocks.remove(block)

                bird.alive = False  # Stop bird after hitting
                break  # Prevent multiple hits in one frame
        ##############--------------

        bird.draw(screen)
        if not bird.alive:
            bird_launched = False # Allow new launch
            bird = None
            if not turn_swiched:
                switch_turn()
                turn_swiched = True

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
