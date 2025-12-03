import tkinter as tk
from tkinter import *
import random
import math
import time
import threading

class SnowDesktopOverlay:
    def __init__(self, parent_root=None):
        self.parent_root = parent_root
        
        if parent_root:
            # Если есть родительское окно, создаем Toplevel
            self.root = tk.Toplevel(parent_root)
        else:
            # Иначе создаем основное окно
            self.root = tk.Tk()
        
        # Настраиваем окно снега
        self.setup_window()
        
        # Создаем снежинки
        self.snowflakes = []
        self.snow_count = 80
        self.create_snowflakes()
        
        # Флаг для остановки анимации
        self.running = True
        
        # Запускаем анимацию в отдельном потоке
        self.animate()
        
    def setup_window(self):
        """Настройка окна снега"""
        # Получаем размеры экрана
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Настройки окна для оверлея поверх рабочего стола
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', False)  # Важно: поверх всех окон!
        self.root.attributes('-transparentcolor', 'black')
        self.root.attributes('-alpha', 0.9)  # Полупрозрачность
        self.root.config(bg='black')
        self.root.overrideredirect(True)  # Убираем рамки
        
        # Создаем холст
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=True)
        
        # Отключаем взаимодействие с окном снега (чтобы можно было кликать сквозь него)
        self.root.attributes('-disabled', True)
        
        # Скрываем окно из панели задач
        if hasattr(self.root, 'wm_withdraw'):
            self.root.wm_withdraw()
        if hasattr(self.root, 'withdraw'):
            self.root.withdraw()
        
            
    def create_snowflakes(self):
        """Создание снежинок"""
        for _ in range(self.snow_count):
            flake = {
                'x': random.randint(0, self.screen_width),
                'y': random.randint(-100, 0),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.5, 2),
                'wind': random.uniform(-0.2, 0.2),
                'oscillation': random.uniform(0.01, 0.05),
                'offset': random.uniform(0, 6.28),
                'id': None
            }
            self.snowflakes.append(flake)
    
    def animate(self):
        """Анимация снежинок"""
        if not self.running:
            return
            
        try:
            # Очищаем холст
            self.canvas.delete("snow")
            
            # Обновляем позиции снежинок
            for flake in self.snowflakes:
                # Движение вниз
                flake['y'] += flake['speed']
                
                # Колебания вбок
                oscillation = math.sin(time.time() * flake['oscillation'] + flake['offset']) * 0.5
                flake['x'] += flake['wind'] + oscillation
                
                # Если снежинка упала, возвращаем наверх
                if flake['y'] > self.screen_height:
                    flake['y'] = random.randint(-100, -10)
                    flake['x'] = random.randint(0, self.screen_width)
                
                # Рисуем снежинку
                x1 = flake['x'] - flake['size']
                y1 = flake['y'] - flake['size']
                x2 = flake['x'] + flake['size']
                y2 = flake['y'] + flake['size']
                
                # Создаем снежинку
                flake['id'] = self.canvas.create_oval(
                    x1, y1, x2, y2,
                    fill='white',
                    outline='white',
                    tags='snow'
                )
            
            # Обновляем окно
            self.root.update_idletasks()
            self.root.update()
            
            # Планируем следующее обновление
            self.root.after(30, self.animate)
            
        except tk.TclError:
            # Окно было закрыто
            pass
    
    def show(self):
        """Показать снег"""
        self.running = True
        self.root.deiconify() if hasattr(self.root, 'deiconify') else self.root.wm_deiconify()
        self.animate()
    
    def hide(self):
        """Скрыть снег"""
        self.running = False
        self.root.withdraw() if hasattr(self.root, 'withdraw') else self.root.wm_withdraw()
    
    def toggle(self):
        """Переключить видимость снега"""
        if self.running:
            self.hide()
        else:
            self.show()
        return self.running
    
    def quit(self):
        """Завершить работу снега"""
        self.running = False
        try:
            self.root.destroy()
        except:
            pass
    
    def run(self):
        """Основной цикл (только если нет родительского окна)"""
        if not self.parent_root:
            self.root.mainloop()

# Функция для тестирования
if __name__ == "__main__":
    app = SnowDesktopOverlay()
    app.run()