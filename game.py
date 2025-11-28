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
        # Инициализация Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("METAL GEAR PYTHON")
        self.clock = pygame.time.Clock()
        
        # Создаем поверхность для игрового поля
        self.game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        
        # Шрифты для UI
        self.font = pygame.font.SysFont('Courier New', 16)
        self.title_font = pygame.font.SysFont('Courier New', 36)
        self.alert_font = pygame.font.SysFont('Courier New', 32)
        self.small_font = pygame.font.SysFont('Courier New', 14)
        
        # Игровые объекты
        self.player = None
        self.enemies = []
        self.documents = []
        self.current_level = 0
        self.level = None
        self.levels = []
        
        # Состояние игры
        self.game_state = 'playing'  # playing, detected, levelComplete, gameOver
        self.detection_level = 0
        self.is_alert_mode = False
        self.mass_elimination_detected = False
        self.debug_mode = True
        
        # Время для таймеров
        self.alert_time = 0
        self.mass_elimination_time = 0
        
        # Инициализация уровней
        self.init_levels()
        self.start_level(self.current_level)
    
    def init_levels(self):
        # Уровень 1 - Простой с препятствиями для обзора
        self.levels.append(Level(
            1,
            [
                # Внешние стены
                [0, 0, 800, 15],
                [0, 0, 15, 500],
                [0, 485, 800, 15],
                [785, 0, 15, 500],
                
                # Внутренние препятствия
                [180, 100, 20, 150],
                [380, 200, 20, 120],
                [580, 150, 20, 100]
            ],
            [
                # Враги: [x, y, patrolPath]
                [250, 200, [[250, 200], [350, 200]]],
                [400, 350, [[400, 350], [400, 450]]],
                [600, 300, [[600, 300], [600, 250]]]
            ],
            [750, 50],  # Выход
            [50, 50],   # Стартовая позиция игрока
            [
                # Документы: [x, y]
                [220, 150],
                [500, 300],
                [650, 100]
            ]
        ))
        
        # Уровень 2 - Лабиринт с патрулирующими врагами
        self.levels.append(Level(
            2,
            [
                # Внешние стены
                [0, 0, 800, 15],
                [0, 0, 15, 500],
                [0, 485, 800, 15],
                [785, 0, 15, 500],
                
                # Внутренние препятствия
                [100, 100, 20, 80],
                [100, 220, 20, 80],
                [200, 50, 100, 20],
                [200, 180, 100, 20],
                [200, 310, 100, 20],
                [200, 430, 100, 20],
                
                # Центральная перегородка
                [350, 150, 20, 200],
                
                # Правая сторона
                [500, 100, 20, 80],
                [500, 220, 20, 80],
                [600, 50, 100, 20],
                [600, 180, 100, 20],
                [600, 310, 100, 20],
                [600, 430, 100, 20]
            ],
            [
                # Враги с исправленными путями патрулирования
                [150, 150, [[150, 150], [150, 120], [180, 120], [180, 150]]],
                [150, 350, [[150, 350], [150, 380], [180, 380], [180, 350]]],
                [650, 150, [[650, 150], [650, 120], [620, 120], [620, 150]]],
                [650, 350, [[650, 350], [650, 380], [620, 380], [620, 350]]],
                [400, 250, [[400, 250], [400, 200], [370, 200], [370, 250]]]
            ],
            [750, 450],  # Выход
            [50, 450],   # Старт
            [
                # Документы в безопасных местах
                [150, 80],
                [150, 400],
                [650, 80],
                [650, 400],
                [400, 400]
            ]
        ))
        
        # Уровень 3 - Сложный с большим количеством врагов
        self.levels.append(Level(
            3,
            [
                # Внешние стены
                [0, 0, 800, 15],
                [0, 0, 15, 500],
                [0, 485, 800, 15],
                [785, 0, 15, 500],
                
                # Внутренние препятствия
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
                # Враги: [x, y, patrolPath]
                [150, 150, [[150, 150], [150, 350]]],
                [270, 270, [[270, 270], [320, 270]]],
                [350, 150, [[350, 150], [430, 150]]],
                [450, 350, [[450, 350], [530, 350]]],
                [550, 250, [[550, 250], [550, 400]]]
            ],
            [750, 250],  # Выход
            [50, 450],
            [
                # Документы: [x, y]
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
        
        # Создание врагов
        self.enemies = []
        for data in self.level.enemies:
            self.enemies.append(Enemy(data[0], data[1], data[2], self.level.walls, self.debug_mode))
        
        # Создание документов
        self.documents = []
        for data in self.level.documents:
            self.documents.append(Document(data[0], data[1]))
        
        self.detection_level = 0
        self.is_alert_mode = False
        self.mass_elimination_detected = False
        self.game_state = 'playing'
        
        # Отладочная информация при старте уровня
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
                # Перезапуск уровня по R
                if event.key == pygame.K_r:
                    self.restart_level()
                
                # Переключение режима отладки по F3
                if event.key == pygame.K_F3:
                    self.debug_mode = not self.debug_mode
                    print(f"Режим отладки: {'ВКЛ' if self.debug_mode else 'ВЫКЛ'}")
                
                # Переход на следующий уровень по N
                if event.key == pygame.K_n and self.game_state == 'levelComplete':
                    self.next_level()
        
        return True
    
    def update(self):
        if self.game_state != 'playing':
            return
        
        # Получаем текущее состояние всех клавиш
        pressed_keys = pygame.key.get_pressed()
        
        # Обновление игрока
        self.player.update(pressed_keys, self.level.walls)
        
        # Автоматическое устранение врагов
        self.auto_eliminate_enemies()
        
        # Обновление врагов и проверка обнаружения
        detected = False
        detection_multiplier = 2 if self.mass_elimination_detected else 1
        
        for enemy in self.enemies:
            if not enemy.is_eliminated:
                enemy.update(self.player.x, self.player.y, self.is_alert_mode, self.enemies, self.is_alert_mode)
                
                # Проверка обнаружения игрока
                if enemy.detect_player(self.player.x, self.player.y, self.level.walls):
                    detected = True
                    
                    # Если враг обнаружил игрока, переводим в режим тревоги
                    if not self.is_alert_mode:
                        self.detection_level = min(100, self.detection_level + 3 * detection_multiplier)
                
                # Проверка столкновения с игроком
                if enemy.check_collision_with_player(self.player) and not enemy.is_eliminated:
                    self.game_over()
        
        # Обновление уровня обнаружения
        if detected and not self.is_alert_mode:
            self.detection_level = min(100, self.detection_level + 2 * detection_multiplier)
        elif not self.is_alert_mode:
            self.detection_level = max(0, self.detection_level - 1)
        
        # Активация режима тревоги
        if self.detection_level >= 100 and not self.is_alert_mode:
            self.activate_alert_mode()
        
        # Проверка сбора документов
        for doc in self.documents:
            if not doc.is_collected and doc.check_collision(self.player):
                doc.collect()
        
        # Проверка достижения выхода
        exit_rect = pygame.Rect(self.level.exit[0], self.level.exit[1], EXIT_SIZE, EXIT_SIZE)
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        
        if player_rect.colliderect(exit_rect):
            self.check_level_completion()
        
        # Проверка таймеров для скрытия алертов
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
        
        # Если устранено более 50% врагов
        if eliminated_enemies > total_enemies / 2 and not self.mass_elimination_detected:
            self.mass_elimination_detected = True
            self.mass_elimination_time = time.time()
            
            # Усиление бдительности оставшихся врагов
            for enemy in self.enemies:
                if not enemy.is_eliminated:
                    enemy.enhance_vigilance()
    
    def activate_alert_mode(self):
        self.is_alert_mode = True
        self.alert_time = time.time()
        self.detection_level = 100
        
        # Все враги переходят в режим преследования
        for enemy in self.enemies:
            if not enemy.is_eliminated:
                enemy.alert(self.player.x, self.player.y)
    
    def check_level_completion(self):
        # Проверяем, собраны ли все документы
        all_documents_collected = all(doc.is_collected for doc in self.documents)
        
        if all_documents_collected:
            self.level_complete()
        else:
            # В Python версии просто выводим сообщение в консоль
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
        # Очистка экрана
        self.screen.fill(DARKER_BLUE)
        
        # Очистка игровой поверхности
        self.game_surface.fill(BLACK)
        
        # Отрисовка уровня на игровой поверхности
        self.level.render(self.game_surface)
        
        # Отрисовка документов на игровой поверхности
        for doc in self.documents:
            doc.render(self.game_surface)
        
        # Отрисовка врагов на игровой поверхности
        for enemy in self.enemies:
            enemy.render(self.game_surface, self.is_alert_mode)
        
        # Отрисовка игрока на игровой поверхности
        self.player.render(self.game_surface)
        
        # Отрисовка индикатора обнаружения
        if self.detection_level > 0:
            alpha = 0.3 if self.is_alert_mode else self.detection_level/200
            overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, int(alpha * 255)))
            self.game_surface.blit(overlay, (0, 0))
        
        # Отображаем игровую поверхность на основном экране
        self.screen.blit(self.game_surface, (GAME_OFFSET_X, GAME_OFFSET_Y))
        
        # Рамка вокруг игрового поля
        pygame.draw.rect(self.screen, GREEN, 
                        (GAME_OFFSET_X - 2, GAME_OFFSET_Y - 2, 
                         GAME_WIDTH + 4, GAME_HEIGHT + 4), 2)
        
        # Отрисовка UI
        self.render_ui()
        
        # Отрисовка отладочной информации
        if self.debug_mode:
            self.render_debug_info()
        
        # Обновление экрана
        pygame.display.flip()
    
    def render_ui(self):
        # Верхняя панель с заголовком и информацией
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, GAME_OFFSET_Y - 10)
        pygame.draw.rect(self.screen, DARK_BLUE, header_rect)
        pygame.draw.line(self.screen, GREEN, (0, GAME_OFFSET_Y - 10), (SCREEN_WIDTH, GAME_OFFSET_Y - 10), 2)
        
        # Заголовок
        title_text = self.title_font.render("METAL GEAR PYTHON", True, GREEN)
        subtitle_text = self.font.render("Стелс-миссия", True, LIGHT_GRAY)
        
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 20))
        self.screen.blit(subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, 60))
        
        # Панели информации
        info_panel_1 = pygame.Rect(GAME_OFFSET_X, 10, 200, 40)
        info_panel_2 = pygame.Rect(GAME_OFFSET_X + 220, 10, 200, 40)
        info_panel_3 = pygame.Rect(GAME_OFFSET_X + 440, 10, 200, 40)
        
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
        
        self.screen.blit(level_text, (GAME_OFFSET_X + 10, 20))
        self.screen.blit(detection_text, (GAME_OFFSET_X + 10, 40))
        self.screen.blit(documents_text, (GAME_OFFSET_X + 230, 20))
        self.screen.blit(controls_text, (GAME_OFFSET_X + 230, 40))
        
        # Кнопки управления
        restart_text = self.font.render("R - Перезапуск", True, LIGHT_GRAY)
        debug_text = self.font.render("F3 - Отладка", True, LIGHT_GRAY)
        
        self.screen.blit(restart_text, (GAME_OFFSET_X + 450, 20))
        self.screen.blit(debug_text, (GAME_OFFSET_X + 450, 40))
        
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
        
        # Алерты (центрируем на игровом поле)
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
        # Панель отладки справа от игрового поля
        debug_panel = pygame.Rect(GAME_OFFSET_X + GAME_WIDTH + 10, GAME_OFFSET_Y, 
                                 SCREEN_WIDTH - (GAME_OFFSET_X + GAME_WIDTH + 20), GAME_HEIGHT)
        pygame.draw.rect(self.screen, PANEL_BG, debug_panel)
        pygame.draw.rect(self.screen, GREEN, debug_panel, 1)
        
        # Заголовок отладки
        debug_title = self.font.render("Отладочная информация:", True, GREEN)
        self.screen.blit(debug_title, (GAME_OFFSET_X + GAME_WIDTH + 20, GAME_OFFSET_Y + 10))
        
        # Информация об игроке
        player_info = [
            f"Игрок: [{int(self.player.x)}, {int(self.player.y)}]",
            f"Направление: {self.player.direction}",
            f"Столкновений: {self.player.collision_count}"
        ]
        
        for i, line in enumerate(player_info):
            text = self.small_font.render(line, True, WHITE)
            self.screen.blit(text, (GAME_OFFSET_X + GAME_WIDTH + 20, GAME_OFFSET_Y + 40 + i * 20))
        
        # Информация о врагах
        enemy_title = self.small_font.render("Враги:", True, GREEN)
        self.screen.blit(enemy_title, (GAME_OFFSET_X + GAME_WIDTH + 20, GAME_OFFSET_Y + 110))
        
        for i, enemy in enumerate(self.enemies):
            if not enemy.is_eliminated:
                text = self.small_font.render(f"Враг {i}: [{int(enemy.x)}, {int(enemy.y)}]", True, WHITE)
                self.screen.blit(text, (GAME_OFFSET_X + GAME_WIDTH + 20, GAME_OFFSET_Y + 130 + i * 15))
                
                if enemy.collision_count > 0:
                    collision_text = self.small_font.render(f"Столкновений: {enemy.collision_count}", True, ALERT_RED)
                    self.screen.blit(collision_text, (GAME_OFFSET_X + GAME_WIDTH + 120, GAME_OFFSET_Y + 130 + i * 15))
        
        # Общая информация
        level_text = self.small_font.render(f"Уровень: {self.current_level + 1}", True, WHITE)
        debug_status = self.small_font.render("Режим отладки: ВКЛ (F3 для выключения)", True, WHITE)
        
        self.screen.blit(level_text, (GAME_OFFSET_X + GAME_WIDTH + 20, GAME_OFFSET_Y + GAME_HEIGHT - 40))
        self.screen.blit(debug_status, (GAME_OFFSET_X + GAME_WIDTH + 20, GAME_OFFSET_Y + GAME_HEIGHT - 20))
