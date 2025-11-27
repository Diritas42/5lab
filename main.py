import pygame
import sys
from game import Game

def main():
    # Инициализация Pygame
    pygame.init()
    
    # Создание экземпляра игры
    game = Game()
    
    # Главный игровой цикл
    running = True
    while running:
        running = game.handle_events()
        game.update()
        game.render()
        
        # Контроль FPS
        game.clock.tick(60)
    
    # Завершение работы
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
