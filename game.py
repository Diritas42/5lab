import pygame
import sys
import time
from settings import *
from player import Player
from enemy import Enemy
from level import Level
from document import Document

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("METAL GEAR PYTHON")
        self.clock = pygame.time.Clock()
        
        self.game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        
        self.font = pygame.font.SysFont('Courier New', 16)
        self.title_font = pygame.font.SysFont('Courier New', 36)
        self.alert_font = pygame.font.SysFont('Courier New', 32)
        self.small_font = pygame.font.SysFont('Courier New', 14)
        
        self.player = None
        self.enemies = []
        self.documents = []
        self.current_level = 0
        self.level = None
        self.levels = []
        
        self.game_state = 'playing'
        self.detection_level = 0
        self.is_alert_mode = False
        self.mass_elimination_detected = False
        self.debug_mode = True
        
        self.alert_time = 0
        self.mass_elimination_time = 0
        
        self.init_levels()
        self.start_level(self.current_level)
    
    def init_levels(self):
        # Уровень 1
        self.levels.append(Level(
            1,
            [
                [0, 0, 800, 15],
                [0, 0, 15, 500],
                [0, 485, 800, 15],
                [785, 0, 15, 500],
                [180, 100, 20, 150],
                [380, 200, 20, 120],
                [580, 150, 20, 100]
            ],
            [
                [250, 200, [[250, 200], [350, 200]]],
                [400, 350, [[400, 350], [400, 450]]],
                [600, 300, [[600, 300], [600, 250]]]
            ],
            [750, 50],
            [50, 50],
            [
                [220, 150],
                [500, 300],
                [650, 100]
            ]
        ))
        
        # Уровень 2
        self.levels.append(Level(
            2,
            [
                [0, 0, 800, 15],
                [0, 0, 15, 500],
                [0, 485, 800, 15],
                [785, 0, 15, 500],
                [100, 100, 20, 80],
                [100, 220, 20, 80],
                [200, 50, 100, 20],
                [200, 180, 100, 20],
                [200, 310, 100, 20],
                [200, 430, 100, 20],
                [350, 150, 20, 200],
                [500, 100, 20, 80],
                [500, 220, 20, 80],
                [600, 50, 100, 20],
                [600, 180, 100, 20],
                [600, 310, 100, 20],
                [600, 430, 100, 20]
            ],
            [
                [150, 150, [[150, 150], [150, 120], [180, 120], [180, 150]]],
                [150, 350, [[150, 350], [150, 380], [180, 380], [180, 350]]],
                [650, 150, [[650, 150], [650, 120], [620, 120], [620, 150]]],
                [650, 350, [[650, 350], [650, 380], [620, 380], [620, 350]]],
                [400, 250, [[400, 250], [400, 200], [370, 200], [370, 250]]]
            ],
            [750, 450],
            [50, 450],
            [
                [150, 80],
                [150, 400],
                [650, 80],
                [650, 400],
                [400, 400]
            ]
        ))
        
        # Уровень 3
        self.levels.append(Level(
            3,
            [
                [0, 0, 800, 15],
                [0, 0, 15, 500],
                [0, 485, 800, 15],
                [785, 0, 15, 500],
                [100, 100, 20, 120],
                [300, 150, 20, 80],
                [500, 200, 20, 150],
                [200, 250, 100, 20],
                [400, 300, 120, 20],
                [600, 350, 20, 100],
                [250, 100, 20, 50],
                [450, 150, 20, 80],
                [650, 200, 20, 80]
            ],
            [
                [150, 150, [[150, 150], [150, 350]]],
                [270, 270, [[270, 270], [320, 270]]],
                [350, 150, [[350, 150], [430, 150]]],
                [450, 350, [[450, 350], [530, 350]]],
                [550, 250, [[550, 250], [550, 400]]]
            ],
            [750, 250],
            [50, 450],
            [
                [150, 300],
                [280, 150],
                [500, 150],
                [400, 400],
                [650, 300]
            ]
        ))
    
    def start_level(self, level_index):
        self.current_level = level_index
        self.level = self.levels[level_index]
        self.player = Player(self.level.start_position[0], self.level.start_position[1], self.debug_mode)
        
        self.enemies = []
        for data in self.level.enemies:
            self.enemies.append(Enemy(data[0], data[1], data[2], self.level.walls, self.debug_mode))
        
        self.documents = []
        for data in self.level.documents:
            self.documents.append(Document(data[0], data[1]))
        
        self.detection_level = 0
        self.is_alert_mode = False
        self.mass_elimination_detected = False
        self.game_state = 'playing'
        
        if self.debug_mode:
            print(f"\n=== ЗАПУСК УРОВНЯ {self.level.number} ===")
            print(f"Стен: {len(self.level.walls)}")
            print(f"Врагов: {len(self.enemies)}")
            print(f"Документов: {len(self.documents)}")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.restart_level()
                if event.key == pygame.K_F3:
                    self.debug_mode = not self.debug_mode
                    print(f"Режим отладки: {'ВКЛ' if self.debug_mode else 'ВЫКЛ'}")
                if event.key == pygame.K_n and self.game_state == 'levelComplete':
                    self.next_level()
        
        return True
    
    def update(self):
        if self.game_state != 'playing':
            return
        
        pressed_keys = pygame.key.get_pressed()
        self.player.update(pressed_keys, self.level.walls)
        self.auto_eliminate_enemies()
        
        detected = False
        detection_multiplier = 2 if self.mass_elimination_detected else 1
        
        for enemy in self.enemies:
            if not enemy.is_eliminated:
                enemy.update(self.player.x, self.player.y, self.is_alert_mode, self.enemies, self.is_alert_mode)
                
                if enemy.detect_player(self.player.x, self.player.y, self.level.walls):
                    detected = True
                    if not self.is_alert_mode:
                        self.detection_level = min(100, self.detection_level + 3 * detection_multiplier)
                
                if enemy.check_collision_with_player(self.player) and not enemy.is_eliminated:
                    self.game_over()
        
        if detected and not self.is_alert_mode:
            self.detection_level = min(100, self.detection_level + 2 * detection_multiplier)
        elif not self.is_alert_mode:
            self.detection_level = max(0, self.detection_level - 1)
        
        if self.detection_level >= 100 and not self.is_alert_mode:
            self.activate_alert_mode()
        
        for doc in self.documents:
            if not doc.is_collected and doc.check_collision(self.player):
                doc.collect()
        
        exit_rect = pygame.Rect(self.level.exit[0], self.level.exit[1], EXIT_SIZE, EXIT_SIZE)
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        
        if player_rect.colliderect(exit_rect):
            self.check_level_completion()
        
        current_time = time.time()
        if self.is_alert_mode and current_time - self.alert_time > 2:
            self.is_alert_mode = False
        
        if self.mass_elimination_detected and current_time - self.mass_elimination_time > 3:
            self.mass_elimination_detected = False
    
    def auto_eliminate_enemies(self):
        for enemy in self.enemies:
            if not enemy.is_eliminated and enemy.can_be_eliminated(self.player.x, self.player.y, self.player.direction):
                enemy.eliminate()
                self.check_mass_elimination()
    
    def check_mass_elimination(self):
        total_enemies = len(self.enemies)
        eliminated_enemies = sum(1 for enemy in self.enemies if enemy.is_eliminated)
        
        if eliminated_enemies > total_enemies / 2 and not self.mass_elimination_detected:
            self.mass_elimination_detected = True
            self.mass_elimination_time = time.time()
            
            for enemy in self.enemies:
                if not enemy.is_eliminated:
                    enemy.enhance_vigilance()
    
    def activate_alert_mode(self):
        self.is_alert_mode = True
        self.alert_time = time.time()
        self.detection_level = 100
        
        for enemy in self.enemies:
            if not enemy.is_eliminated:
                enemy.alert(self.player.x, self.player.y)
    
    def check_level_completion(self):
        all_documents_collected = all(doc.is_collected for doc in self.documents)
        
        if all_documents_collected:
            self.level_complete()
        else:
            print("СОБЕРИТЕ ВСЕ ДОКУМЕНТЫ!")
    
    def level_complete(self):
        self.game_state = 'levelComplete'
        print("УРОВЕНЬ ЗАВЕРШЕН!")
        
        if self.current_level < len(self.levels) - 1:
            print("Нажмите N для перехода на следующий уровень")
        else:
            print("МИССИЯ ВЫПОЛНЕНА!")
    
    def game_over(self):
        self.game_state = 'gameOver'
        print("МИССИЯ ПРОВАЛЕНА! Нажмите R для перезапуска уровня")
    
    def restart_level(self):
        self.start_level(self.current_level)
    
    def next_level(self):
        if self.current_level < len(self.levels) - 1:
            self.start_level(self.current_level + 1)
    
    def render(self):
        self.screen.fill(DARKER_BLUE)
        self.game_surface.fill(BLACK)
        
        self.level.render(self.game_surface)
        
        for doc in self.documents:
            doc.render(self.game_surface)
        
        for enemy in self.enemies:
            enemy.render(self.game_surface, self.is_alert_mode)
        
        self.player.render(self.game_surface)
        
        if self.detection_level > 0:
            alpha = 0.3 if self.is_alert_mode else self.detection_level/200
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, int(alpha * 255)))
            self.game_surface.blit(overlay, (0, 0))
        
        self.screen.blit(self.game_surface, (GAME_OFFSET_X, GAME_OFFSET_Y))
        pygame.draw.rect(self.screen, GREEN, 
                        (GAME_OFFSET_X - 2, GAME_OFFSET_Y - 2, 
                         GAME_WIDTH + 4, GAME_HEIGHT + 4), 2)
        
        self.render_ui()
        
        if self.debug_mode:
            self.render_debug_info()
        
        pygame.display.flip()
    
    def render_ui(self):
        # Верхняя панель с заголовком и информацией
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, GAME_OFFSET_Y - 20)
        pygame.draw.rect(self.screen, DARK_BLUE, header_rect)
        pygame.draw.line(self.screen, GREEN, (0, GAME_OFFSET_Y - 20), (SCREEN_WIDTH, GAME_OFFSET_Y - 20), 2)
        
        # Заголовок (опущен ниже)
        title_text = self.title_font.render("METAL GEAR PYTHON", True, GREEN)
        subtitle_text = self.font.render("Стелс-миссия", True, LIGHT_GRAY)
        
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))
        self.screen.blit(subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, 80))
        
        # Панели информации (увеличены и опущены ниже)
        info_panel_1 = pygame.Rect(GAME_OFFSET_X, 110, 280, 50)
        info_panel_2 = pygame.Rect(GAME_OFFSET_X + 290, 110, 280, 50)
        info_panel_3 = pygame.Rect(GAME_OFFSET_X + 580, 110, 280, 50)
        
        pygame.draw.rect(self.screen, PANEL_BG, info_panel_1)
        pygame.draw.rect(self.screen, PANEL_BG, info_panel_2)
        pygame.draw.rect(self.screen, PANEL_BG, info_panel_3)
        pygame.draw.rect(self.screen, GREEN, info_panel_1, 1)
        pygame.draw.rect(self.screen, GREEN, info_panel_2, 1)
        pygame.draw.rect(self.screen, GREEN, info_panel_3, 1)
        
        # Текст информации
        level_text = self.font.render(f"Уровень: {self.level.number}", True, LIGHT_GRAY)
        detection_text = self.font.render(f"Обнаружение: {self.detection_level}%", True, LIGHT_GRAY)
        
        collected_count = sum(1 for doc in self.documents if doc.is_collected)
        documents_text = self.font.render(f"Документы: {collected_count}/{len(self.documents)}", True, LIGHT_GRAY)
        controls_text = self.font.render("Управление: WASD + Shift", True, LIGHT_GRAY)
        
        restart_text = self.font.render("R - Перезапуск уровня", True, LIGHT_GRAY)
        debug_text = self.font.render("F3 - Режим отладки", True, LIGHT_GRAY)
        
        self.screen.blit(level_text, (GAME_OFFSET_X + 10, 120))
        self.screen.blit(detection_text, (GAME_OFFSET_X + 10, 140))
        self.screen.blit(documents_text, (GAME_OFFSET_X + 300, 120))
        self.screen.blit(controls_text, (GAME_OFFSET_X + 300, 140))
        self.screen.blit(restart_text, (GAME_OFFSET_X + 590, 120))
        self.screen.blit(debug_text, (GAME_OFFSET_X + 590, 140))
        
        # Нижняя панель с инструкциями
        footer_rect = pygame.Rect(0, GAME_OFFSET_Y + GAME_HEIGHT + 10, SCREEN_WIDTH, 
                                 SCREEN_HEIGHT - (GAME_OFFSET_Y + GAME_HEIGHT + 10))
        pygame.draw.rect(self.screen, DARK_BLUE, footer_rect)
        pygame.draw.line(self.screen, GREEN, 
                        (0, GAME_OFFSET_Y + GAME_HEIGHT + 10), 
                        (SCREEN_WIDTH, GAME_OFFSET_Y + GAME_HEIGHT + 10), 2)
        
        # Инструкции
        instructions_title = self.font.render("Инструкция:", True, GREEN)
        self.screen.blit(instructions_title, (GAME_OFFSET_X, GAME_OFFSET_Y + GAME_HEIGHT + 25))
        
        instructions = [
            "• Используйте WASD для движения и Shift для бега",
            "• Подходите к врагам сзади для автоматического устранения",
            "• Соберите все секретные документы (жёлтые) и достигните выхода (синий)",
            "• Красные зоны - зоны видимости врагов",
            "• При полном обнаружении начинается погоня!",
            "• Если устранить более 50% врагов, оставшиеся получат усиленную бдительность"
        ]
        
        for i, line in enumerate(instructions):
            text = self.small_font.render(line, True, LIGHT_GRAY)
            self.screen.blit(text, (GAME_OFFSET_X, GAME_OFFSET_Y + GAME_HEIGHT + 50 + i * 20))
        
        # Алерты
        alert_y = GAME_OFFSET_Y + GAME_HEIGHT // 2 - 30
        
        if self.game_state == 'gameOver':
            alert_text = self.alert_font.render("МИССИЯ ПРОВАЛЕНА!", True, ALERT_RED)
            subtext = self.font.render("Нажмите R для перезапуска уровня", True, LIGHT_GRAY)
            
            self.screen.blit(alert_text, (GAME_OFFSET_X + GAME_WIDTH // 2 - alert_text.get_width() // 2, alert_y))
            self.screen.blit(subtext, (GAME_OFFSET_X + GAME_WIDTH // 2 - subtext.get_width() // 2, alert_y + 50))
        
        elif self.game_state == 'levelComplete':
            if self.current_level < len(self.levels) - 1:
                alert_text = self.alert_font.render("УРОВЕНЬ ЗАВЕРШЕН!", True, GREEN)
                subtext = self.font.render("Нажмите N для следующего уровня", True, LIGHT_GRAY)
            else:
                alert_text = self.alert_font.render("МИССИЯ ВЫПОЛНЕНА!", True, GREEN)
                subtext = self.font.render("Поздравляем!", True, LIGHT_GRAY)
            
            self.screen.blit(alert_text, (GAME_OFFSET_X + GAME_WIDTH // 2 - alert_text.get_width() // 2, alert_y))
            self.screen.blit(subtext, (GAME_OFFSET_X + GAME_WIDTH // 2 - subtext.get_width() // 2, alert_y + 50))
        
        elif self.is_alert_mode:
            alert_text = self.alert_font.render("ТРЕВОГА!", True, ALERT_RED)
            self.screen.blit(alert_text, (GAME_OFFSET_X + GAME_WIDTH // 2 - alert_text.get_width() // 2, alert_y))
        
        elif self.mass_elimination_detected:
            alert_text = self.alert_font.render("ОБНАРУЖЕНА АКТИВНОСТЬ АГЕНТА!", True, ALERT_YELLOW)
            self.screen.blit(alert_text, (GAME_OFFSET_X + GAME_WIDTH // 2 - alert_text.get_width() // 2, alert_y))
    
    def render_debug_info(self):
        debug_panel = pygame.Rect(GAME_OFFSET_X + GAME_WIDTH + 10, GAME_OFFSET_Y, 
                                 SCREEN_WIDTH - (GAME_OFFSET_X + GAME_WIDTH + 20), GAME_HEIGHT)
        pygame.draw.rect(self.screen, PANEL_BG, debug_panel)
        pygame.draw.rect(self.screen, GREEN, debug_panel, 1)
        
        debug_title = self.font.render("Отладочная информация:", True, GREEN)
        self.screen.blit(debug_title, (GAME_OFFSET_X + GAME_WIDTH + 20, GAME_OFFSET_Y + 10))
        
        player_info = [
            f"Игрок: [{int(self.player.x)}, {int(self.player.y)}]",
            f"Направление: {self.player.direction}",
            f"Столкновений: {self.player.collision_count}"
        ]
        
        for i, line in enumerate(player_info):
            text = self.small_font.render(line, True, WHITE)
            self.screen.blit(text, (GAME_OFFSET_X + GAME_WIDTH + 20, GAME_OFFSET_Y + 40 + i * 20))
        
        enemy_title = self.small_font.render("Враги:", True, GREEN)
        self.screen.blit(enemy_title, (GAME_OFFSET_X + GAME_WIDTH + 20, GAME_OFFSET_Y + 110))
        
        for i, enemy in enumerate(self.enemies):
            if not enemy.is_eliminated:
                text = self.small_font.render(f"Враг {i}: [{int(enemy.x)}, {int(enemy.y)}]", True, WHITE)
                self.screen.blit(text, (GAME_OFFSET_X + GAME_WIDTH + 20, GAME_OFFSET_Y + 130 + i * 15))
                
                if enemy.collision_count > 0:
                    collision_text = self.small_font.render(f"Столкновений: {enemy.collision_count}", True, ALERT_RED)
                    self.screen.blit(collision_text, (GAME_OFFSET_X + GAME_WIDTH + 120, GAME_OFFSET_Y + 130 + i * 15))
        
        level_text = self.small_font.render(f"Уровень: {self.current_level + 1}", True, WHITE)
        debug_status = self.small_font.render("Режим отладки: ВКЛ (F3 для выключения)", True, WHITE)
        
        self.screen.blit(level_text, (GAME_OFFSET_X + GAME_WIDTH + 20, GAME_OFFSET_Y + GAME_HEIGHT - 40))
        self.screen.blit(debug_status, (GAME_OFFSET_X + GAME_WIDTH + 20, GAME_OFFSET_Y + GAME_HEIGHT - 20))
