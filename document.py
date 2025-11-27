import pygame
from settings import *

class Document:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = DOCUMENT_WIDTH
        self.height = DOCUMENT_HEIGHT
        self.color = YELLOW
        self.is_collected = False
    
    def check_collision(self, player):
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        document_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return player_rect.colliderect(document_rect)
    
    def collect(self):
        self.is_collected = True
    
    def render(self, screen):
        if self.is_collected:
            return
        
        # Основной прямоугольник документа
        document_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.color, document_rect)
        
        # Текст на документе
        font = pygame.font.SysFont('Arial', 8)
        text = font.render('DOC', True, BLACK)
        text_rect = text.get_rect(center=(self.x + self.width/2, self.y + self.height/2))
        screen.blit(text, text_rect)
        
        # Блеск
        shine_rect = pygame.Rect(self.x + 2, self.y + 2, 5, 3)
        pygame.draw.rect(screen, (255, 255, 255, 128), shine_rect)
