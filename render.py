import pygame
import asyncio
from grid import Grid

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
CELL_SIZE = 20

def draw_grid(grid):
    print(1)
    for x in range(grid.width):
        for y in range(grid.height):
            print(grid.grid[x][y].content)
            pygame.draw.rect(screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
            for obj in grid.grid[x][y].content:
                if obj.type == GridObjType.CARGO:
                    pygame.draw.circle(screen, RED, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)
                elif obj.type == GridObjType.DESTINATION:
                    pygame.draw.circle(screen, BLUE, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)
                elif obj.type == GridObjType.PORTER:
                    pygame.draw.circle(screen, GREEN, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)

def web_render(width, height, n_porters, n_cargos, n_dests, min_weight, max_weight):
    WINDOW_SIZE = (width * CELL_SIZE, height * CELL_SIZE)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("ANTS")
    clock = pygame.time.Clock()
    screen.fill(WHITE)
    
    grid = Grid(width, height)
    grid.random_intialize(n_porters, n_cargos, n_dests, min_weight, max_weight)
    draw_grid(grid)
    print(11111111)
    
    while True:
        print(2)
        draw_grid(grid)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        pygame.display.update()
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(web_render(10, 10, 5, 5, 5, 1, 10))