import pygame
import math
from settings import *

class Enemy:
    def __init__(self, x, y, patrol_path, walls, debug_mode=False):
        self.x = x
        self.y = y
        self.width = ENEMY_SIZE
        self.height = ENEMY_SIZE
        self.patrol_path = patrol_path
        self.current_target = 0
        self.speed = ENEMY_SPEED
        self.alert_speed = ENEMY_ALERT_SPEED
        self.color = RED
        self.alert_color = LIGHT_RED
        self.enhanced_color = DARK_RED
        self.detection_range = DETECTION_RANGE
        self.detection_angle = math.radians(DETECTION_ANGLE)  # преобразуем в радианы
        self.blind_spot_angle = math.pi  # 180 градусов для полной задней полусферы
        self.direction = 0  # Направление взгляда
        self.is_alerted = False
        self.is_eliminated = False
        self.is_vigilance_enhanced = False
        self.walls = walls
        self.chase_target = None
        self.debug_mode = debug_mode
        self.collision_count = 0
        self.last_collision_report = 0
        self.is_chasing = False
    
    def update(self, player_x, player_y, is_global_alert, all_enemies, enable_enemy_collisions=False):
        if self.is_eliminated:
            return
        
        # Если глобальная тревога или враг уже был предупрежден
        if is_global_alert or self.is_alerted:
            self.is_chasing = True
            self.chase_player(player_x, player_y)
        else:
            self.is_chasing = False
            self.patrol()
        
        # Проверка коллизий с другими врагами только если включено
        if enable_enemy_collisions:
            self.check_enemy_collisions(all_enemies)
    
    def check_enemy_collisions(self, all_enemies):
        for enemy in all_enemies:
            if enemy != self and not enemy.is_eliminated and self.check_collision_with_enemy(enemy):
                # Отталкивание от другого врага
                dx = self.x - enemy.x
                dy = self.y - enemy.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance > 0:
                    push_force = 0.8
                    self.x += (dx / distance) * push_force
                    self.y += (dy / distance) * push_force
                    
                    # Проверка коллизий со стенами после отталкивания
                    for wall in self.walls:
                        if self.check_collision(wall):
                            self.x -= (dx / distance) * push_force
                            self.y -= (dy / distance) * push_force
                            if self.debug_mode:
                                self.report_collision(wall, 'ENEMY_PUSH')
                            break
    
    def check_collision_with_enemy(self, enemy):
        enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
        self_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return self_rect.colliderect(enemy_rect)
    
    def patrol(self):
        if self.patrol_path and len(self.patrol_path) > 1:
            target = self.patrol_path[self.current_target]
            dx = target[0] - self.x
            dy = target[1] - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < 5:
                self.current_target = (self.current_target + 1) % len(self.patrol_path)
            else:
                self.move_towards(target[0], target[1], self.speed)
                
                # Обновление направления взгляда
                self.direction = math.atan2(dy, dx)
    
    def chase_player(self, player_x, player_y):
        self.is_alerted = True
        self.move_towards(player_x, player_y, self.alert_speed)
        self.direction = math.atan2(player_y - self.y, player_x - self.x)
    
    def move_towards(self, target_x, target_y, speed):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            move_x = (dx / distance) * speed
            move_y = (dy / distance) * speed
            
            # Проверка коллизий при движении
            self.move_with_collision(move_x, move_y)
    
    def move_with_collision(self, move_x, move_y):
        # Сохраняем исходные позиции
        original_x = self.x
        original_y = self.y
        
        # Пробуем двигаться по X
        self.x += move_x
        collision_x = False
        
        for wall in self.walls:
            if self.check_collision(wall):
                collision_x = True
                self.x = original_x
                if self.debug_mode:
                    self.report_collision(wall, 'X')
                break
        
        # Пробуем двигаться по Y
        self.y += move_y
        collision_y = False
        
        for wall in self.walls:
            if self.check_collision(wall):
                collision_y = True
                self.y = original_y
                if self.debug_mode:
                    self.report_collision(wall, 'Y')
                break
        
        # Если есть коллизия по обеим осям, враг останавливается
        if collision_x and collision_y and self.is_chasing:
            # Враг останавливается при погоне
            self.x = original_x
            self.y = original_y
            
            if self.debug_mode:
                print(f"Враг остановился из-за столкновения со стеной во время погони!")
        
        # Ограничение движения в пределах экрана
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
    
    def report_collision(self, wall, axis):
        self.collision_count += 1
        
        # Ограничиваем частоту сообщений чтобы не заспамить консоль
        import time
        now = time.time() * 1000  # в миллисекундах
        if now - self.last_collision_report > 1000:  # Не чаще чем раз в 1 секунду
            print(f"Враг столкнулся со стеной! Позиция: [{int(self.x)}, {int(self.y)}], Стена: {wall}, Ось: {axis}, Всего столкновений: {self.collision_count}")
            self.last_collision_report = now
    
    def check_collision(self, wall):
        wall_rect = pygame.Rect(wall[0], wall[1], wall[2], wall[3])
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return enemy_rect.colliderect(wall_rect)
    
    def detect_player(self, player_x, player_y, walls):
        if self.is_eliminated:
            return False
        
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Проверка расстояния
        if distance > self.detection_range:
            return False
        
        # Проверка угла обзора
        angle_to_player = math.atan2(dy, dx)
        angle_diff = abs(self.direction - angle_to_player)
        normalized_angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))
        
        if abs(normalized_angle_diff) > self.detection_angle / 2:
            return False
        
        # Проверка прямой видимости (нет стен между врагом и игроком)
        return self.has_line_of_sight(player_x, player_y, walls)
    
    def has_line_of_sight(self, player_x, player_y, walls):
        # Упрощенная проверка прямой видимости
        for wall in walls:
            if self.line_intersects_rect(
                self.x + self.width/2, self.y + self.height/2,
                player_x + 10, player_y + 10, wall
            ):
                return False
        return True
    
    def line_intersects_rect(self, x1, y1, x2, y2, rect):
        rx, ry, rw, rh = rect
        
        # Проверка пересечения с каждой стороной прямоугольника
        return (
            self.line_intersects_line(x1, y1, x2, y2, rx, ry, rx + rw, ry) or  # верх
            self.line_intersects_line(x1, y1, x2, y2, rx + rw, ry, rx + rw, ry + rh) or  # право
            self.line_intersects_line(x1, y1, x2, y2, rx, ry + rh, rx + rw, ry + rh) or  # низ
            self.line_intersects_line(x1, y1, x2, y2, rx, ry, rx, ry + rh)  # лево
        )
    
    def line_intersects_line(self, x1, y1, x2, y2, x3, y3, x4, y4):
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if den == 0:
            return False
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
        
        return 0 <= t <= 1 and 0 <= u <= 1
    
    def can_be_eliminated(self, player_x, player_y, player_direction):
        if self.is_eliminated or self.is_alerted or self.is_vigilance_enhanced:
            return False
        
        # Проверка расстояния - уменьшена дистанция устранения
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > ELIMINATION_DISTANCE:
            return False
        
        # Проверка, что игрок находится сзади врага
        # Используем полную заднюю полусферу (180 градусов)
        angle_to_player = math.atan2(dy, dx)
        angle_diff = abs(self.direction - angle_to_player)
        normalized_angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))
        
        # Упрощенная проверка - игрок должен быть в задней полусфере врага
        return abs(normalized_angle_diff) > math.pi / 2
    
    def check_collision_with_player(self, player):
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return player_rect.colliderect(enemy_rect)
    
    def eliminate(self):
        self.is_eliminated = True
        if self.debug_mode:
            print(f"Враг устранен! Позиция: [{int(self.x)}, {int(self.y)}]")
    
    def alert(self, player_x, player_y):
        self.is_alerted = True
        self.chase_target = {'x': player_x, 'y': player_y}
    
    def enhance_vigilance(self):
        self.is_vigilance_enhanced = True
        self.detection_range *= 1.2  # Увеличиваем дальность обнаружения
    
    def render(self, screen, is_alert_mode):
        if self.is_eliminated:
            return
        
        # Тело врага
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if self.is_vigilance_enhanced:
            color = self.enhanced_color
        else:
            color = self.alert_color if self.is_alerted else self.color
        
        pygame.draw.rect(screen, color, enemy_rect)
        
        # Область видимости (для отладки)
        if not is_alert_mode:
            # Рисуем сектор обзора
            center_x = self.x + self.width/2
            center_y = self.y + self.height/2
            
            # Создаем поверхность для полупрозрачного сектора
            sector_surface = pygame.Surface((self.detection_range * 2, self.detection_range * 2), pygame.SRCALPHA)
            sector_color = (255, 100, 100, 50) if self.is_vigilance_enhanced else (255, 0, 0, 25)
            
            # Рисуем сектор
            start_angle = self.direction - self.detection_angle/2
            end_angle = self.direction + self.detection_angle/2
            
            pygame.draw.arc(sector_surface, sector_color, 
                           (0, 0, self.detection_range * 2, self.detection_range * 2),
                           start_angle, end_angle, self.detection_range)
            
            # Рисуем линии от центра к краям сектора
            pygame.draw.line(sector_surface, sector_color, 
                            (self.detection_range, self.detection_range),
                            (self.detection_range + self.detection_range * math.cos(start_angle),
                             self.detection_range + self.detection_range * math.sin(start_angle)), 1)
            pygame.draw.line(sector_surface, sector_color, 
                            (self.detection_range, self.detection_range),
                            (self.detection_range + self.detection_range * math.cos(end_angle),
                             self.detection_range + self.detection_range * math.sin(end_angle)), 1)
            
            # Накладываем поверхность на экран
            screen.blit(sector_surface, (center_x - self.detection_range, center_y - self.detection_range))
        
        # Глаза (направление взгляда)
        eye_x = self.x + self.width/2 + math.cos(self.direction) * 8
        eye_y = self.y + self.height/2 + math.sin(self.direction) * 8
        pygame.draw.circle(screen, BLACK, (int(eye_x), int(eye_y)), 4)
        
        # Отображение состояния (тревога или усиленная бдительность)
        if self.is_alerted:
            pygame.draw.circle(screen, ALERT_YELLOW, (int(self.x + self.width/2), int(self.y - 10)), 5)
        elif self.is_vigilance_enhanced:
            pygame.draw.circle(screen, ALERT_RED, (int(self.x + self.width/2), int(self.y - 10)), 5)
