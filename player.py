import pygame
from settings import *

class Player:
    def __init__(self, x, y, debug_mode=False):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.run_speed = PLAYER_RUN_SPEED
        self.color = GREEN
        self.direction = 0  # 0: вправо, 1: влево, 2: вверх, 3: вниз
        self.debug_mode = debug_mode
        self.collision_count = 0
    
    def update(self, keys, walls):
        move_x = 0
        move_y = 0
        speed = self.run_speed if keys[pygame.K_LSHIFT] else self.speed
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_y = -speed
            self.direction = 2
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y = speed
            self.direction = 3
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x = -speed
            self.direction = 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x = speed
            self.direction = 0
        
        # Применение движения с проверкой коллизий
        self.move_with_collision(move_x, move_y, walls)
    
    def move_with_collision(self, move_x, move_y, walls):
        # Проверка коллизий по X
        self.x += move_x
        for wall in walls:
            if self.check_collision(wall):
                self.x -= move_x
                if self.debug_mode:
                    self.report_collision(wall, 'X')
                break
        
        # Проверка коллизий по Y
        self.y += move_y
        for wall in walls:
            if self.check_collision(wall):
                self.y -= move_y
                if self.debug_mode:
                    self.report_collision(wall, 'Y')
                break
        
        # Ограничение движения в пределах экрана
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
    
    def report_collision(self, wall, axis):
        self.collision_count += 1
        print(f"Игрок столкнулся со стеной! Позиция: [{int(self.x)}, {int(self.y)}], Стена: {wall}, Ось: {axis}, Всего столкновений: {self.collision_count}")
    
    def check_collision(self, wall):
        wall_rect = pygame.Rect(wall[0], wall[1], wall[2], wall[3])
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return player_rect.colliderect(wall_rect)
    
    def render(self, screen):
        # Тело игрока
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.color, player_rect)
        
        # Голова (показывает направление)
        head_color = DARK_GREEN
        if self.direction == 0:  # вправо
            head_rect = pygame.Rect(self.x + self.width - 5, self.y + 5, 5, 10)
        elif self.direction == 1:  # влево
            head_rect = pygame.Rect(self.x, self.y + 5, 5, 10)
        elif self.direction == 2:  # вверх
            head_rect = pygame.Rect(self.x + 5, self.y, 10, 5)
        else:  # вниз
            head_rect = pygame.Rect(self.x + 5, self.y + self.height - 5, 10, 5)
        
        pygame.draw.rect(screen, head_color, head_rect)
