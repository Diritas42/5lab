import pygame
from settings import *

class Level:
    def __init__(self, number, walls, enemies, exit_pos, start_position, documents):
        self.number = number
        self.walls = walls
        self.enemies = enemies  # данные для создания врагов
        self.exit = exit_pos
        self.start_position = start_position
        self.documents = documents  # данные для создания документов
    
    def render(self, screen):
        # Отрисовка стен
        for wall in self.walls:
            wall_rect = pygame.Rect(wall[0], wall[1], wall[2], wall[3])
            pygame.draw.rect(screen, GRAY, wall_rect)
        
        # Отрисовка выхода
        exit_rect = pygame.Rect(self.exit[0], self.exit[1], EXIT_SIZE, EXIT_SIZE)
        pygame.draw.rect(screen, BLUE, exit_rect)
        
        # Текст "ВЫХОД"
        font = pygame.font.SysFont('Arial', 12)
        text = font.render('ВЫХОД', True, WHITE)
        text_rect = text.get_rect(center=(self.exit[0] + EXIT_SIZE/2, self.exit[1] - 5))
        screen.blit(text, text_rect)
