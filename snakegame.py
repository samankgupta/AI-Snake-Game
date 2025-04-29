import random
import heapq
import argparse
import pygame
from enum import Enum

# Game Constants
GRID_WIDTH = 15
GRID_HEIGHT = 15
CELL_SIZE = 20
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 10

# Colors
BLACK = (10, 10, 10)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
FOOD_COLOR = (255, 50, 50)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

pygame.font.init()
font = pygame.font.SysFont('Arial', 24)


# Direction Enum
class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

# GameState Class
class GameState:
    def __init__(self):
        self.reset()
        self.enemy_snake = []    # List of 3 parts
        self.enemy_timer = 0     # Lifetime timer (in frames)
        self.enemy_move_timer = 0  # Time until next enemy move
        self.enemy_exists = False
        self.enemy_spawned_once = False


    def reset(self):
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = Direction.RIGHT
        self.food = self.generate_food()
        self.grow_snake = False

    def generate_food(self):
        while True:
            food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if food not in self.snake:
                return food
            
    def spawn_enemy(self):
        for _ in range(100):
            orientation = random.choice(["horizontal", "vertical"])
            if orientation == "horizontal":
                x = random.randint(0, GRID_WIDTH - 3)
                y = random.randint(0, GRID_HEIGHT - 1)
                positions = [(x+i, y) for i in range(3)]
            else:
                x = random.randint(0, GRID_WIDTH - 1)
                y = random.randint(0, GRID_HEIGHT - 3)
                positions = [(x, y+i) for i in range(3)]

            if all(pos not in self.snake for pos in positions):
                self.enemy_snake = positions
                self.enemy_timer = FPS * 5  # 5 seconds lifetime
                self.enemy_move_timer = FPS  # Move every 1 second
                self.enemy_exists = True
                break

            
    def move_enemy(self):
        if not self.enemy_exists:
            return

        self.enemy_move_timer -= 1
        if self.enemy_move_timer > 0:
            return  # Not time to move yet

        self.enemy_move_timer = FPS  # Reset move timer for next second

        move_dir = random.choice(["up", "down", "left", "right"])
        head_x, head_y = self.enemy_snake[0]

        if move_dir == "up":
            head_y = (head_y - 1) % GRID_HEIGHT
        elif move_dir == "down":
            head_y = (head_y + 1) % GRID_HEIGHT
        elif move_dir == "left":
            head_x = (head_x - 1) % GRID_WIDTH
        elif move_dir == "right":
            head_x = (head_x + 1) % GRID_WIDTH

        new_head = (head_x, head_y)
        self.enemy_snake = [new_head] + self.enemy_snake[:-1]



    def move(self):
        head_x, head_y = self.snake[0]
        if self.direction == Direction.UP:
            head_y -= 1
        elif self.direction == Direction.DOWN:
            head_y += 1
        elif self.direction == Direction.LEFT:
            head_x -= 1
        elif self.direction == Direction.RIGHT:
            head_x += 1

        head_x %= GRID_WIDTH
        head_y %= GRID_HEIGHT

        new_head = (head_x, head_y)

        # Check collision with self
        if new_head in self.snake:
            return False, False  # Game Over, no food eaten
        
        if new_head in self.enemy_snake:
            return False, False  # Dead if touch enemy

        self.snake.insert(0, new_head)

        ate_food = False
        if new_head == self.food:
            self.grow_snake = True
            self.food = self.generate_food()
            ate_food = True

        if not self.grow_snake:
            self.snake.pop()
        else:
            self.grow_snake = False

        return True, ate_food

    def change_direction(self, new_direction):
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        if new_direction != opposite[self.direction]:
            self.direction = new_direction

# A* Pathfinding
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def show_message(text):
    big_font = pygame.font.SysFont('Arial', 36)
    message = big_font.render(text, True, (0, 255, 0))
    rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    screen.fill(BLACK)
    screen.blit(message, rect)
    pygame.display.flip()

    pygame.time.delay(3000)  # pause for 3 seconds


def find_path(start, goal, obstacles):
    heap = []
    heapq.heappush(heap, (0 + heuristic(start, goal), 0, start, []))
    visited = set()

    while heap:
        f, cost, current, path = heapq.heappop(heap)

        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            return path

        x, y = current
        neighbors = [
            ((x-1)%GRID_WIDTH, y), ((x+1)%GRID_WIDTH, y),
            (x, (y-1)%GRID_HEIGHT), (x, (y+1)%GRID_HEIGHT)
        ]
        directions = [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]

        for (nx, ny), dir in zip(neighbors, directions):
            if (nx, ny) not in obstacles:
                heapq.heappush(heap, (cost + 1 + heuristic((nx, ny), goal), cost + 1, (nx, ny), path + [dir.name]))

    return None

def draw(state, score):
    screen.fill(BLACK)
    for (x, y) in state.snake:
        pygame.draw.rect(screen, GREEN, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1))
    fx, fy = state.food
    pygame.draw.rect(screen, FOOD_COLOR, (fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1))

    # Draw score counter
    score_text = font.render(f"Score: {score}/25", True, (255, 255, 255))
    screen.blit(score_text, (8, 8))

    if state.enemy_exists:
        for (x, y) in state.enemy_snake:
            pygame.draw.rect(screen, (0, 0, 255), (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1))

    pygame.display.flip()

# Main function
def main(mode):
    state = GameState()
    path = []
    score = 0
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if mode == "manual" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    state.change_direction(Direction.UP)
                elif event.key == pygame.K_DOWN:
                    state.change_direction(Direction.DOWN)
                elif event.key == pygame.K_LEFT:
                    state.change_direction(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    state.change_direction(Direction.RIGHT)

        if mode == "auto":
            obstacles = set(state.snake[1:])
            path = find_path(state.snake[0], state.food, obstacles)

            if path:
                next_move = path[0]  # Only the next move
                state.change_direction(Direction[next_move])
            else:
                # If no safe path found, move forward or turn
                state.change_direction(random.choice([Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]))

        # Enemy spawning
        if not state.enemy_spawned_once and pygame.time.get_ticks() > 5000:
            state.spawn_enemy()
            state.enemy_spawned_once = True


        # Enemy moving
        if state.enemy_exists:
            state.move_enemy()
            state.enemy_timer -= 1
            if state.enemy_timer <= 0:
                state.enemy_exists = False


        alive, ate_food = state.move()

        if ate_food:
            score += 1
            if score >= 25:
                show_message("YOU WIN!")
                running = False


        draw(state, score)

        if not alive:
            show_message("GAME OVER!")
            running = False

    pygame.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["manual", "auto"], default="auto", help="Choose mode: manual or auto")
    args = parser.parse_args()

    main(args.mode)
