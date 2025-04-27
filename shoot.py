import pygame
import random
import math
from collections import deque

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BUBBLE_RADIUS = 20
LAUNCHER_WIDTH = 10
LAUNCHER_LENGTH = 40
LAUNCHER_POS = (WIDTH // 2, HEIGHT - 50)
BUBBLE_SPEED = 10
GRID_OFFSET_X = BUBBLE_RADIUS
GRID_OFFSET_Y = 50
GRID_ROWS = 10
GRID_COLS = 15

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE]

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Shooter")
clock = pygame.time.Clock()

class Bubble:
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        self.radius = BUBBLE_RADIUS
        self.color = color if color else random.choice(COLORS)
        self.dx = 0
        self.dy = 0
        self.moving = False
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 1)
    
    def move(self):
        if self.moving:
            self.x += self.dx
            self.y += self.dy
            
            # Wall collision
            if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
                self.dx *= -1
    
    def snap_to_grid(self, grid):
        # Find the closest grid position
        min_dist = float('inf')
        closest_pos = None
        
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                if grid[row][col] is not None:
                    continue
                    
                # Calculate position for this grid cell
                offset = 0 if row % 2 == 0 else BUBBLE_RADIUS
                grid_x = GRID_OFFSET_X + col * (BUBBLE_RADIUS * 2) + offset
                grid_y = GRID_OFFSET_Y + row * (BUBBLE_RADIUS * 1.8)
                
                # Calculate distance
                dist = math.sqrt((self.x - grid_x)**2 + (self.y - grid_y)**2)
                
                if dist < min_dist:
                    min_dist = dist
                    closest_pos = (row, col, grid_x, grid_y)
        
        if closest_pos and min_dist < BUBBLE_RADIUS * 1.5:
            row, col, grid_x, grid_y = closest_pos
            self.x, self.y = grid_x, grid_y
            self.moving = False
            self.dx, self.dy = 0, 0
            return row, col
        
        return None, None

def create_grid():
    grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    
    # Fill the top few rows with random bubbles
    for row in range(3):
        for col in range(GRID_COLS):
            if row % 2 == 1 and col == GRID_COLS - 1:
                continue  # Skip last column in odd rows
            grid[row][col] = Bubble(0, 0, random.choice(COLORS))
    
    return grid

def draw_grid(grid):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            if grid[row][col] is not None:
                offset = 0 if row % 2 == 0 else BUBBLE_RADIUS
                grid[row][col].x = GRID_OFFSET_X + col * (BUBBLE_RADIUS * 2) + offset
                grid[row][col].y = GRID_OFFSET_Y + row * (BUBBLE_RADIUS * 1.8)
                grid[row][col].draw()

def draw_launcher(angle):
    end_x = LAUNCHER_POS[0] + LAUNCHER_LENGTH * math.sin(angle)
    end_y = LAUNCHER_POS[1] - LAUNCHER_LENGTH * math.cos(angle)
    pygame.draw.line(screen, WHITE, LAUNCHER_POS, (end_x, end_y), LAUNCHER_WIDTH)
    pygame.draw.circle(screen, WHITE, LAUNCHER_POS, BUBBLE_RADIUS)

def find_connected_bubbles(grid, row, col, color):
    directions_even = [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)]
    directions_odd = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)]
    
    visited = set()
    queue = deque()
    queue.append((row, col))
    connected = []
    
    while queue:
        r, c = queue.popleft()
        if (r, c) in visited:
            continue
        visited.add((r, c))
        
        if r < 0 or r >= GRID_ROWS or c < 0 or c >= GRID_COLS:
            continue
            
        if grid[r][c] is None or grid[r][c].color != color:
            continue
            
        connected.append((r, c))
        directions = directions_even if r % 2 == 0 else directions_odd
        
        for dr, dc in directions:
            queue.append((r + dr, c + dc))
    
    return connected

def check_for_matches(grid, row, col):
    if grid[row][col] is None:
        return []
    
    color = grid[row][col].color
    connected = find_connected_bubbles(grid, row, col, color)
    
    if len(connected) >= 3:
        return connected
    return []

def remove_bubbles(grid, positions):
    for row, col in positions:
        grid[row][col] = None

def main():
    running = True
    angle = 0  # Angle in radians (0 points straight up)
    grid = create_grid()
    current_bubble = Bubble(LAUNCHER_POS[0], LAUNCHER_POS[1])
    next_bubble = Bubble(0, 0, random.choice(COLORS))
    shooting = False
    
    while running:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEMOTION and not shooting:
                # Calculate angle based on mouse position
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx = mouse_x - LAUNCHER_POS[0]
                dy = LAUNCHER_POS[1] - mouse_y
                angle = math.atan2(dx, dy)
            elif event.type == pygame.MOUSEBUTTONDOWN and not shooting:
                shooting = True
                current_bubble.moving = True
                current_bubble.dx = BUBBLE_SPEED * math.sin(angle)
                current_bubble.dy = -BUBBLE_SPEED * math.cos(angle)
        
        # Update current bubble
        if shooting:
            current_bubble.move()
            
            # Check if bubble hit the top
            if current_bubble.y - current_bubble.radius <= 0:
                current_bubble.dy *= -1
            
            # Check if bubble should snap to grid
            row, col = current_bubble.snap_to_grid(grid)
            if row is not None and col is not None:
                shooting = False
                grid[row][col] = current_bubble
                
                # Check for matches
                matches = check_for_matches(grid, row, col)
                if matches:
                    remove_bubbles(grid, matches)
                
                # Prepare next bubble
                current_bubble = Bubble(LAUNCHER_POS[0], LAUNCHER_POS[1], next_bubble.color)
                next_bubble = Bubble(0, 0, random.choice(COLORS))
        
        # Draw everything
        draw_grid(grid)
        draw_launcher(angle)
        current_bubble.draw()
        
        # Draw next bubble preview
        pygame.draw.circle(screen, next_bubble.color, (50, HEIGHT - 50), BUBBLE_RADIUS)
        pygame.draw.circle(screen, WHITE, (50, HEIGHT - 50), BUBBLE_RADIUS, 1)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()