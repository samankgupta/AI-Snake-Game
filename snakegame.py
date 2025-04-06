import pygame
import random
from enum import Enum
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = 600
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE

# Colors
BLACK = (10, 10, 10)  # Very dark grey, almost black like Nokia screen
RED = (255, 0, 0)
DARK_RED = (200, 0, 0)  # For snake body
FOOD_COLOR = (255, 50, 50)

class Direction(Enum):
    """Enum for storing directional constants"""
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class SnakeSegment:
    """Class representing a segment of the snake"""
    def __init__(self, position: Tuple[int, int]):
        self.position = position

    def draw(self, surface: pygame.Surface):
        """Draw the snake segment"""
        rect = pygame.Rect(
            self.position[0] * GRID_SIZE,
            self.position[1] * GRID_SIZE,
            GRID_SIZE - 1,
            GRID_SIZE - 1
        )
        pygame.draw.rect(surface, RED, rect)

class Food:
    """Class representing the food"""
    def __init__(self):
        self.position = self.generate_position()

    def generate_position(self) -> Tuple[int, int]:
        """Generate a random position for the food"""
        return (
            random.randint(0, GRID_COUNT - 1),
            random.randint(0, GRID_COUNT - 1)
        )

    def draw(self, surface: pygame.Surface):
        """Draw the food"""
        rect = pygame.Rect(
            self.position[0] * GRID_SIZE,
            self.position[1] * GRID_SIZE,
            GRID_SIZE - 1,
            GRID_SIZE - 1
        )
        pygame.draw.rect(surface, FOOD_COLOR, rect)

class Snake:
    """Class representing the snake"""
    def __init__(self):
        self.reset()

    def reset(self):
        """Reset the snake to initial state"""
        self.direction = Direction.RIGHT
        self.segments = [
            SnakeSegment((GRID_COUNT // 2, GRID_COUNT // 2))
        ]
        self.growing = False

    def update(self) -> bool:
        """Update snake position and return True if game should continue"""
        # Get the current head position
        head = self.segments[0].position
        
        # Calculate new head position based on direction
        new_head = list(head)
        if self.direction == Direction.UP:
            new_head[1] -= 1
        elif self.direction == Direction.DOWN:
            new_head[1] += 1
        elif self.direction == Direction.LEFT:
            new_head[0] -= 1
        elif self.direction == Direction.RIGHT:
            new_head[0] += 1

        # Wrap around screen
        new_head[0] = new_head[0] % GRID_COUNT
        new_head[1] = new_head[1] % GRID_COUNT
        
        # Check for collision with self
        if tuple(new_head) in [segment.position for segment in self.segments]:
            return False

        # Add new head
        self.segments.insert(0, SnakeSegment(tuple(new_head)))
        
        # Remove tail if not growing
        if not self.growing:
            self.segments.pop()
        else:
            self.growing = False
            
        return True

    def draw(self, surface: pygame.Surface):
        """Draw the snake"""
        for segment in self.segments:
            segment.draw(surface)

    def grow(self):
        """Mark the snake to grow on next update"""
        self.growing = True

    def change_direction(self, new_direction: Direction):
        """Change the snake's direction if valid"""
        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        if new_direction != opposite_directions.get(self.direction):
            self.direction = new_direction

class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption('Nokia Snake Game')
        self.clock = pygame.time.Clock()
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_speed = 10

    def handle_input(self):
        """Handle keyboard input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.snake.change_direction(Direction.UP)
                elif event.key == pygame.K_DOWN:
                    self.snake.change_direction(Direction.DOWN)
                elif event.key == pygame.K_LEFT:
                    self.snake.change_direction(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.snake.change_direction(Direction.RIGHT)
        return True

    def update(self):
        """Update game state"""
        if not self.snake.update():
            self.reset_game()
            return

        # Check for food collision
        if self.snake.segments[0].position == self.food.position:
            self.snake.grow()
            self.food.position = self.food.generate_position()
            self.score += 1
            # Increase game speed every 5 points
            if self.score % 5 == 0:
                self.game_speed += 1

    def draw(self):
        """Draw the game state"""
        self.screen.fill(BLACK)
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        pygame.display.flip()

    def reset_game(self):
        """Reset the game state"""
        self.snake.reset()
        self.food = Food()
        self.score = 0
        self.game_speed = 10

    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.game_speed)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()