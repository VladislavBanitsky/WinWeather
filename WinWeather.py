# ==============================================================================================
# Простое оконное приложение для просмотра погоды, даты и времени.
# Поддерживаются два режима работы: оконное приложение (главное окно и окно настроек) и виджет.
# GitHub: https://github.com/VladislavBanitsky/WinWeather
# Разработчик: Владислав Баницкий
# Версия: 1.1.3
# Обновлено: 03.12.2025  
# ==============================================================================================

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import requests
from urllib.request import  Request, urlopen
from PIL import Image, ImageTk
import json
import sys
import os
import pygame  # для работы со звуком
from pygame import mixer
from SnowOnDesktop import SnowDesktopOverlay

snow_overlay = None  # Глобальная переменная для снега

WIDTH = 400
HEIGHT = 320

W_WIDTH  = 250
W_HEIGHT = 100

VERSION = "1.1.3"
ABOUT = f"2025, Vladislav Banitsky, v. {VERSION}"

# Настройки по умолчанию
DEFAULT_SETTINGS = {
    "API_WEATHER_KEY": "c866db0d4955404eb89124646253007",
    "CITY": "Санкт-Петербург",
    "TEMP_UNIT": "°C",
    "TIME_FORMAT": "%H:%M:%S    %d.%m.%Y",
    "LANGUAGE": "ru",
    "THEME": "auto",
    "VOLUME": 0.5,
    "WIDGET_ALWAYS_ON_TOP": False,
    "AUTO_DETECT_SETTINGS": True,
    "SNOW_IS_ON": True
}

# Цветовые схемы для тем
THEMES = {
    "light": {
        "bg": "#f0f0f0",
        "fg": "#000000",
        "button_active": "#e0e0e0",
        "splash_bg": "#ffffff"
    },
    "dark": {
        "bg": "#2d2d2d",
        "fg": "#ffffff",
        "button_active": "#5d5d5d",
        "splash_bg": "#1a1a1a"
    }
}


# Функция для автоматического переключения темы в зависимости от времени суток
def get_auto_theme():
    current_hour = datetime.now().hour  # получаем текущий час    
    if 5 <= current_hour < 17:  # утро и день: 5:00 - 16:59
        return "light"
    else:  # вечер и ночь: 17:00 - 4:59
        return "dark"


# Функция для получения приветствия в зависимости от времени суток
def get_greeting():
    current_hour = datetime.now().hour  # получаем текущий час    
    if 5 <= current_hour < 11:  # Утро: 5:00 - 10:59
        return "Доброе утро!" if LANGUAGE == "ru" else "Good morning!"
    elif 11 <= current_hour < 17:  # День: 11:00 - 16:59
        return "Добрый день!" if LANGUAGE == "ru" else "Good afternoon!"
    elif 17 <= current_hour < 23:  # Вечер: 17:00 - 22:59
        return "Добрый вечер!" if LANGUAGE == "ru" else "Good evening!"
    else:  # Ночь: 23:00 - 4:59
        return "Доброй ночи!" if LANGUAGE == "ru" else "Goodnight!"


# Функция для отображения заставки
def show_splash():
    # Загружаем и отображаем логотип
    logo_img = Image.open(resource_path('./resources/images/WinWeather_512.png'))
    logo_img = logo_img.resize((200, 200), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(root, image=logo_photo, bg=current_theme["bg"])
    logo_label.image = logo_photo  # сохраняем ссылку
    logo_label.pack(pady=20)
    # Добавляем приветствие
    title_label = author_label = tk.Label(root, text=get_greeting(), font=("Arial", 20, 'italic'), bg=current_theme["bg"], fg=current_theme["fg"])
    title_label.pack(pady=5)
    # Добавляем версию
    version_label = tk.Label(root, text=ABOUT, font=("Arial", 9, 'italic'), bg=current_theme["bg"], fg=current_theme["fg"])
    version_label.pack(pady=5)
    # Обновляем окно, чтобы оно появилось сразу
    root.update()
    # Убираем заставку через 3 секунды
    root.after(1000, logo_label.destroy)
    root.after(1000, title_label.destroy)
    root.after(1000, version_label.destroy)


# Функция для инициализации звуковой системы
def init_sound():
    try:
        pygame.init()
        mixer.init()
        print("Звуковая система успешно инициализирована")
        return True
    except Exception as e:
        print(f"Ошибка инициализации звука: {e}")
        return False
        

# Функция для загрузки настроек из файла или использования значений по умолчанию
def load_settings():
    if os.path.exists('settings.json'):
        try:
            with open('settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Проверяем, что все необходимые ключи присутствуют
                for key in DEFAULT_SETTINGS:
                    if key not in settings:
                        settings[key] = DEFAULT_SETTINGS[key]
                return settings
        except (json.JSONDecodeError, IOError):
            return DEFAULT_SETTINGS
    return DEFAULT_SETTINGS


# Функция для сохранения настроек в файл
def save_settings(settings):
    with open('settings.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)


# Функция для центрирования окон
def center_window(window, width, height):
    # Получаем размеры экрана
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Вычисляем координаты для центрирования окна
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    
    # Устанавливаем положение окна
    window.geometry(f'{width}x{height}+{x}+{y}')
    

# Функция для корректного поиска файлов
def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсу, работает для dev и для PyInstaller """
    if hasattr(sys, '_MEIPASS'):  # Если запущено из EXE
        base_path = sys._MEIPASS
    else:  # Если запущено из скрипта
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Функция для изменения темы
def apply_theme(): 
    global current_theme_name  # применяем изменения по всему интерфейсу
    
    if THEME == "auto":  # тема автоматическая?
        if current_theme_name == get_auto_theme():  # если текущая тема уже совпадает с необходимой
            return  # ничего не делаем (экономия ресурсов)
        else:  # иначе
            current_theme_name = get_auto_theme()  # перерисовываем интерфейс в нужной теме
    else:  # иначе тема статическая
        current_theme_name = THEME  # просто применяем статическую тему
    
    current_theme = THEMES[current_theme_name]
    
    root.configure(bg=current_theme["bg"])
    
    for widget in [time_label, city_label, temper_label, condition_label, author_label]:
        widget.configure(bg=current_theme["bg"], fg=current_theme["fg"])
    
    icon_label.configure(bg=current_theme["bg"])
    
    # Обновляем фон для кнопок
    settings_button.configure(
        bg=current_theme["bg"],
        activebackground=current_theme["button_active"]
    )
    settings_frame.configure(bg=current_theme["bg"])
    pin_button.configure(
        bg=current_theme["bg"],
        activebackground=current_theme["button_active"]
    )
    pin_frame.configure(bg=current_theme["bg"])
    
    # Обновляем прозрачность в режиме виджета
    if WIDGET_MODE:
        root.attributes('-alpha', WIDGET_TRANSPARENCY)


# Функция для воспроизведения звуков погоды
def play_weather_sounds(condition):
    global current_sound
    
    # Если произошла ошибка - звук не включаем
    if not SOUND_INITIALIZED:
        if current_sound:
            current_sound.stop()
        return
        
    # Останавливаем предыдущий звук
    if current_sound:
        current_sound.stop()
    
    # Определяем, какие звуки нужно воспроизвести
    condition_lower = condition.lower()
    sound_file = None
    
    try:
        sound_file = None
        
        if "гроз" in condition_lower or "thunder" in condition_lower:
            # Воспроизводим звук грозы
            sound_file = resource_path('./resources/sounds/thunder.wav')
        elif "лед" in condition_lower or "град" in condition_lower or "ice pellets" in condition_lower:
            # Воспроизводим звук града
            sound_file = resource_path('./resources/sounds/ice_pellets.wav')
        elif "дожд" in condition_lower or "лив" in condition_lower or "rain" in condition_lower:
            # Воспроизводим звук дождя
            sound_file = resource_path('./resources/sounds/rain.wav')
        elif "сне" in condition_lower or "snow" in condition_lower or "blizzard" in condition_lower:
            # Воспроизводим звук снега
            sound_file = resource_path('./resources/sounds/snow.wav')
        
        if sound_file and os.path.exists(sound_file):
            try:
                current_sound  = mixer.Sound(sound_file)
                current_sound.set_volume(VOLUME)  # устанавливаем громкость
                current_sound.play(loops=-1)  # Бесконечный цикл
            except Exception as e:
                print(f"Ошибка воспроизведения звука: {e}")
        else:
            print(f"Звуковой файл не найден: {sound_file}")
    except Exception as e:
        print(f"Общая ошибка в play_weather_sounds: {e}")


# Функция запроса погодных данных
def get_weather_data():
    global CITY
    try:  # если API доступен
        
        if AUTO_DETECT_SETTINGS:  # если данные получаются по IP
            ip = urlopen(Request("https://ifconfig.me/ip")).read().decode('utf-8', errors='ignore')  # узнаём IP адрес
            CITY = ip
        
        r = requests.get(f"https://api.weatherapi.com/v1/current.json?key={API_WEATHER_KEY}&q={CITY}&aqi=yes&lang={LANGUAGE}")
        current_weather = r.json()
        
        if AUTO_DETECT_SETTINGS:  # если данные получаются по IP
            CITY = current_weather["location"]["name"] # сохраняем название из ответа API
            update_city()  # и заменяем IP адрес на город
        
        # Добавляем знак для красивого вывода положительной температуры
        sign = ""
        if current_weather["current"]["temp_c"] > 0:
            sign = "+"    
        temper = sign + str(int(current_weather["current"]["temp_c"]) if TEMP_UNIT == "°C" else int(current_weather["current"]["temp_f"]))
        condition = current_weather["current"]["condition"]["text"]
        icon = urlopen("https:" + current_weather["current"]["condition"]["icon"]) 
        # Воспроизводим звуки в соответствии с погодой
        play_weather_sounds(condition)
        
    except:  # иначе отображаем сообщение об ошибке
        temper = ""
        condition = "Нет связи :(" if LANGUAGE == "ru" else "No connection :("
        icon = resource_path('./resources/images/no_connection.png')
            
    return temper, condition, icon


# Функция для обновления даты и времени
def update_time():
    current_time = datetime.now().strftime(TIME_FORMAT)  # Получаем текущее время
    time_label.config(text=f"{current_time}")  # Обновляем текст Label
    time_label.after(1000, update_time)  # Планируем обновление через 1 секунду


# Функция для обновления данных о погоде
def update_weather_data():
    temper, condition, icon = get_weather_data()  # Получаем текущие данные
    
    temper_label.config(text=f"{temper}{TEMP_UNIT}")  # Обновляем текст Label
    condition_label.config(text=f"{condition}")  # Обновляем текст Label
    
    if icon!=resource_path('./resources/images/no_connection.png'):  # только если иконка доступна
        # Считываем данные и создаем изображение
        image_data = icon.read()
        img = ImageTk.PhotoImage(data=image_data)
        icon_label.config(image=img)
        # Сохраняем ссылку на изображение, чтобы оно не удалилось
        icon_label.image = img
    else:  # нет соединения с API
        # Загружаем и отображаем логотип
        image_data = Image.open(resource_path('./resources/images/no_connection.png'))
        image_data = image_data.resize((80, 80), Image.LANCZOS)
        img = ImageTk.PhotoImage(image_data)
        icon_label.config(image=img)
        icon_label.image = img        
        
    
    condition_label.after(60000, update_weather_data)  # Планируем обновление через 1 минуту


# Функция для обновления данных о городе
def update_city():
    city_label.config(text=f"{CITY}")  # Обновляем текст Label


# Функция для обновления автоматической темы
def update_auto_theme():
    if THEME == "auto":
        apply_theme()
    root.after(60000, update_auto_theme)  # Проверяем каждую минуту


# Функция для переключения режима виджета
def toggle_widget_mode():
    global WIDGET_MODE
    
    WIDGET_MODE = not WIDGET_MODE  # меняем состояние на противоположное (вкл./выкл.)
    
    if WIDGET_MODE:
        # Включаем режим виджета
        root.overrideredirect(True)  # Убираем рамку окна
        root.attributes('-topmost', WIDGET_ALWAYS_ON_TOP)
        root.attributes('-alpha', WIDGET_TRANSPARENCY)
        
        # Скрываем все элементы
        time_label.pack_forget()
        city_label.pack_forget()
        temper_label.pack_forget()
        condition_label.pack_forget()
        icon_label.pack_forget()
        author_label.pack_forget()
        settings_frame.place_forget()
        pin_frame.place_forget()
        
        # Перерисовываем элементы компактно
        pin_frame.pack(pady=10, padx=10, side="left")
        temper_label.pack(pady=10, padx=10, side="right")
        icon_label.pack(pady=10, padx=10, side="right")
        
        # Уменьшаем размер окна
        root.geometry(f"{W_WIDTH}x{W_HEIGHT}")
        
        # Добавляем возможность перемещения окна
        root.bind('<Button-1>', start_move)
        root.bind('<B1-Motion>', on_move)
        
    else:
        # Выключаем режим виджета
        root.overrideredirect(False)  # Возвращаем рамку окна
        root.attributes('-topmost', False)
        root.attributes('-alpha', 1.0)
        
        # Скрываем отрисованные элементы
        temper_label.pack_forget()
        icon_label.pack_forget()
        
        # Показываем все элементы в привычном виде
        time_label.pack(pady=3)
        city_label.pack(pady=3)
        temper_label.pack(pady=3)
        condition_label.pack(pady=3)
        icon_label.pack(pady=3)
        author_label.pack(pady=3, side=tk.BOTTOM)
        settings_frame.place(x=360, y=280, width=30, height=30)
        pin_frame.place(x=10, y=10, width=30, height=30)
        # Возвращаем стандартные шрифты
        time_label.config(font=("Arial", 18, 'italic'))
        city_label.config(font=("Arial", 18, 'italic'))
        temper_label.config(font=("Arial", 24))
        condition_label.config(font=("Arial", 18, 'italic'))
        
        # Возвращаем стандартный размер окна
        center_window(root, WIDTH, HEIGHT)
        
        # Убираем обработчики перемещения
        root.unbind('<Button-1>')
        root.unbind('<B1-Motion>')
        

# Функция для начала перемещения окна в режиме виджета
def start_move(event):
    global x, y
    x = event.x
    y = event.y

# Функция для окончания перемещения окна в режиме виджета
def on_move(event):
    deltax = event.x - x
    deltay = event.y - y
    x_pos = root.winfo_x() + deltax
    y_pos = root.winfo_y() + deltay
    root.geometry(f"+{x_pos}+{y_pos}")

# Функция для отображения окна Настройки
def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title(f"WinWeather {VERSION} Настройки" if LANGUAGE == "ru" else f"WinWeather {VERSION} Settings")
    center_window(settings_window, WIDTH, HEIGHT)
    settings_window.resizable(width=False, height=False)
    settings_window.iconbitmap(resource_path('./resources/images/WinWeather.ico'))
    settings_window.grab_set()  # блокировка основного окна, пока открыты настройки
    
    # Применяем текущую тему к окну настроек   
    current_theme = THEMES[current_theme_name] 
    settings_window.configure(bg=current_theme["bg"])
    
    # Улучшение стилей ползунка громкости звука
    style = ttk.Style()
    style.configure('TScale', background=current_theme["bg"], troughcolor=current_theme["bg"])
    
    city_var = tk.StringVar(value=CITY)
    time_format_var = tk.StringVar(value=TIME_FORMAT)
    temp_unit_var = tk.StringVar(value=TEMP_UNIT)
    language_var = tk.StringVar(value=LANGUAGE)
    theme_var = tk.StringVar(value=THEME)
    volume_var = tk.DoubleVar(value=VOLUME)
    widget_top_var = tk.StringVar()
    snow_is_on_var = tk.StringVar(value=SNOW_IS_ON)
    
    # Выводим название темы на нужном языке (но в переменных всё на английском)
    if THEME == "auto":
        theme_var.set("авто" if LANGUAGE == "ru" else "auto")
    elif THEME == "light":
        theme_var.set("светлая" if LANGUAGE == "ru" else "light")
    elif THEME == "dark":
        theme_var.set("тёмная" if LANGUAGE == "ru" else "dark")
    
    # Выводим название настройки словами (но в переменных True или False)
    if WIDGET_ALWAYS_ON_TOP == True:
        widget_top_var.set("всех окон" if LANGUAGE == "ru" else "all windows")
    else:
        widget_top_var.set("рабочего стола" if LANGUAGE == "ru" else "desktop")
    
    if SNOW_IS_ON == True:
        snow_is_on_var.set("да" if LANGUAGE == "ru" else "yes")
    else:
        snow_is_on_var.set("нет" if LANGUAGE == "ru" else "no")
        
    # Создаем элементы управления с использованием grid    
    # Город
    row = 0
    tk.Label(settings_window, text="Город:" if LANGUAGE == "ru" else "City:", 
            bg=current_theme["bg"], fg=current_theme["fg"]).grid(row=row, column=0, padx=10, pady=(20, 5), sticky='w')
    ttk.Combobox(settings_window, textvariable=city_var, width=20,
                 values=["определить по IP" if LANGUAGE == "ru" else "identify by IP"]).grid(row=row, column=1, padx=10, pady=(20, 5), sticky='ew')
    
    # Формат времени
    row += 1
    tk.Label(settings_window, text="Формат времени:" if LANGUAGE == "ru" else "Time format:", 
            bg=current_theme["bg"], fg=current_theme["fg"]).grid(row=row, column=0, padx=10, pady=5, sticky='w')
    ttk.Combobox(settings_window, textvariable=time_format_var, 
                values=["%H:%M:%S    %d.%m.%y",
                        "%H:%M:%S    %d.%m.%Y",
                        "%H:%M:%S    %m/%d/%y",
                        "%H:%M:%S    %m/%d/%Y",
                        "%H:%M:%S    %y-%m-%d",
                        "%H:%M:%S    %Y-%m-%d"],
                state="readonly").grid(row=row, column=1, padx=10, pady=5, sticky='ew')
    
    # Единицы температуры
    row += 1
    tk.Label(settings_window, text="Единицы температуры:" if LANGUAGE == "ru" else "Temperature units:", 
            bg=current_theme["bg"], fg=current_theme["fg"]).grid(row=row, column=0, padx=10, pady=5, sticky='w')
    ttk.Combobox(settings_window, textvariable=temp_unit_var, 
                values=["°C", "°F"], state="readonly", width=18).grid(row=row, column=1, padx=10, pady=5, sticky='ew')
    
    # Язык
    row += 1
    tk.Label(settings_window, text="Язык:" if LANGUAGE == "ru" else "Language:", 
            bg=current_theme["bg"], fg=current_theme["fg"]).grid(row=row, column=0, padx=10, pady=5, sticky='w')
    ttk.Combobox(settings_window, textvariable=language_var, 
                values=["ru", "en"], state="readonly", width=18).grid(row=row, column=1, padx=10, pady=5, sticky='ew')
    
    # Тема
    row += 1
    tk.Label(settings_window, text="Тема:" if LANGUAGE == "ru" else "Theme:", 
            bg=current_theme["bg"], fg=current_theme["fg"]).grid(row=row, column=0, padx=10, pady=5, sticky='w')
    ttk.Combobox(settings_window, textvariable=theme_var, 
                 values=["авто" if LANGUAGE == "ru" else "auto",
                         "светлая" if LANGUAGE == "ru" else "light",
                         "тёмная" if LANGUAGE == "ru" else "dark"], state="readonly", width=18).grid(row=row, column=1, padx=10, pady=5, sticky='ew')
    
    # Громкость
    row += 1
    tk.Label(settings_window, text="Громкость звуков погоды:" if LANGUAGE == "ru" else "Volume of weather sounds:", 
            bg=current_theme["bg"], fg=current_theme["fg"]).grid(row=row, column=0, padx=10, pady=5, sticky='w')
    
    # Фрейм для ползунка и значения
    volume_frame = tk.Frame(settings_window, bg=current_theme["bg"])
    volume_frame.grid(row=row, column=1, padx=10, pady=5, sticky='ew')
    
    ttk.Scale(volume_frame, from_=0, to=1, variable=volume_var, 
             command=lambda v: volume_var.set(float(v))).pack(side='left', expand=True, fill='x')
    
    value_label = tk.Label(volume_frame, text=f"{int(volume_var.get()*100)}%", 
                          bg=current_theme["bg"], fg=current_theme["fg"], width=5)
    value_label.pack(side='left', padx=5)
    
    def update_volume_label(val):
        value_label.config(text=f"{int(float(val)*100)}%")
        if current_sound:
            current_sound.set_volume(float(val))
    
    volume_var.trace_add("write", lambda *_: update_volume_label(volume_var.get()))
    
    # Виджет
    row += 1
    tk.Label(settings_window, text="Виджет поверх:" if LANGUAGE == "ru" else "Widget on top of:", 
            bg=current_theme["bg"], fg=current_theme["fg"]).grid(row=row, column=0, padx=10, pady=5, sticky='w')
    ttk.Combobox(settings_window, textvariable=widget_top_var, 
                 values=["всех окон" if LANGUAGE == "ru" else "all windows",
                         "рабочего стола" if LANGUAGE == "ru" else "desktop"], state="readonly", width=18).grid(row=row, column=1, padx=10, pady=5, sticky='ew')
    
    # Падающий снег поверх рабочего стола
    row += 1
    tk.Label(settings_window, text="Включить снег:" if LANGUAGE == "ru" else "Turn on snow:", 
            bg=current_theme["bg"], fg=current_theme["fg"]).grid(row=row, column=0, padx=10, pady=5, sticky='w')
    ttk.Combobox(settings_window, textvariable=snow_is_on_var, 
                 values=["да" if LANGUAGE == "ru" else "yes",
                         "нет" if LANGUAGE == "ru" else "no"], state="readonly", width=18).grid(row=row, column=1, padx=10, pady=5, sticky='ew')    
    
    # Кнопка сохранения
    row += 1
    save_button = ttk.Button(settings_window, 
                             text="Сохранить" if LANGUAGE == "ru" else "Save", 
                             command=lambda: save_settings_by_button(city_var, temp_unit_var, time_format_var, language_var,
                                                                     theme_var, volume_var, widget_top_var, settings_window, snow_is_on_var))
    save_button.grid(row=row, column=0, columnspan=2, pady=20)
    
    # Настройка веса столбцов для правильного растяжения
    settings_window.columnconfigure(0, weight=1)
    settings_window.columnconfigure(1, weight=2)

    
# Функция для кнопки сохранения
def save_settings_by_button(city_var, temp_unit_var, time_format_var, language_var, theme_var, volume_var, widget_top_var, settings_window, snow_is_on_var):
    global CITY, TEMP_UNIT, TIME_FORMAT, LANGUAGE, THEME, VOLUME, current_sound, AUTO_DETECT_SETTINGS, WIDGET_ALWAYS_ON_TOP, SNOW_IS_ON, snow_overlay
    
    TEMP_UNIT = temp_unit_var.get()
    TIME_FORMAT = time_format_var.get()
    LANGUAGE = language_var.get()
    THEME = theme_var.get()
    VOLUME = volume_var.get()
        
    # Проверяем, как будет определяться местоположение для запроса к API
    if city_var.get() == "определить по IP" or city_var.get() == "identify by IP":
        AUTO_DETECT_SETTINGS = True  # определяем автоматически
    else:
        AUTO_DETECT_SETTINGS = False  # определяем по вводу пользователя
        CITY = city_var.get()  # сохраняем нужный город
    
    # Если в переменной сохранены названия темы на русском - сохраняем в переменную на английском
    if theme_var.get() == "авто":
        THEME = "auto"
    elif theme_var.get() == "светлая":
        THEME = "light"
    elif theme_var.get() == "тёмная":
        THEME = "dark"
        
    # Переводим название настроек в True или False
    if widget_top_var.get() == "всех окон" or widget_top_var.get() == "all windows":
        WIDGET_ALWAYS_ON_TOP = True
    else:
        WIDGET_ALWAYS_ON_TOP = False
    
    if snow_is_on_var.get() == "да" or snow_is_on_var.get() == "yes":
        SNOW_IS_ON = True
    else:
        SNOW_IS_ON = False
        
    # Обработка настроек снега
    if SNOW_IS_ON:
        if snow_overlay is None:
            # Создаем снег, если его еще нет
            snow_overlay = SnowDesktopOverlay(root)
            snow_overlay.show()
        else:
            # Показываем снег, если он уже создан
            snow_overlay.show()
    else:
        if snow_overlay is not None:
            # Скрываем снег, если он есть
            snow_overlay.hide()
    
    # Обновляем громкость текущего звука
    if current_sound:
        current_sound.set_volume(VOLUME)
    
    # Сохраняем настройки в файл
    settings_to_save = {
        "API_WEATHER_KEY": API_WEATHER_KEY,
        "CITY": CITY,
        "TEMP_UNIT": TEMP_UNIT,
        "TIME_FORMAT": TIME_FORMAT,
        "LANGUAGE": LANGUAGE,
        "THEME": THEME,
        "VOLUME": VOLUME,
        "WIDGET_ALWAYS_ON_TOP": WIDGET_ALWAYS_ON_TOP,
        "SNOW_IS_ON": SNOW_IS_ON,
        "AUTO_DETECT_SETTINGS": AUTO_DETECT_SETTINGS  # теперь считываем настройки пользователя
    }
    save_settings(settings_to_save)
    
    apply_theme()
    update_city()
    update_weather_data()
    
    settings_window.destroy()


# Эффект при наведении для кнопки Настройки
def on_enter_settings(e):
    settings_button['bg'] = THEMES[current_theme_name]["button_active"]


def on_leave_settings(e):
    settings_button['bg'] = THEMES[current_theme_name]["bg"]


# Эффект при наведении для кнопки переключения в режим виджета и обратно
def on_enter_pin(e):
    pin_button['bg'] = THEMES[current_theme_name]["button_active"]


def on_leave_pin(e):
    pin_button['bg'] = THEMES[current_theme_name]["bg"]

# Загружаем настройки при старте
settings = load_settings()
API_WEATHER_KEY = settings["API_WEATHER_KEY"]
CITY = settings["CITY"]
TEMP_UNIT = settings["TEMP_UNIT"]
TIME_FORMAT = settings["TIME_FORMAT"]
LANGUAGE = settings["LANGUAGE"]
THEME = settings["THEME"]
VOLUME = settings.get("VOLUME", 0.5)
SNOW_IS_ON = settings.get("SNOW_IS_ON", True)
WIDGET_MODE = False
WIDGET_ALWAYS_ON_TOP = settings.get("WIDGET_ALWAYS_ON_TOP", True)
WIDGET_TRANSPARENCY = 0.9
AUTO_DETECT_SETTINGS = settings.get("AUTO_DETECT_SETTINGS", True)  # до изменения настроек местоположение определяется автоматически
SOUND_INITIALIZED = init_sound()
current_sound = None  # глобальная переменная для хранения текущего звука
current_theme_name = THEME  # глобальная переменная для хранения названия темы

# Применяем автоопределение настроек, если включено
if AUTO_DETECT_SETTINGS:
    try:
        ip = urlopen(Request("https://ifconfig.me/ip")).read().decode('utf-8', errors='ignore')
        CITY = ip
    except Exception as e:
        print(f"Не удалось получить IP: {e}")

# Создаем главное окно
root = tk.Tk()
root.title(f"WinWeather {VERSION}")
center_window(root, WIDTH, HEIGHT)
root.resizable(width=False, height=False)
root.iconbitmap(resource_path('./resources/images/WinWeather.ico'))  

# Применяем тему сразу после создания окна
if THEME == "auto":  # тема автоматическая?
    current_theme_name = get_auto_theme()  # тогда узнаём нужную
else:  # иначе тема статическая
    current_theme_name = THEME  # просто сохраняем статическую тему 

if SNOW_IS_ON:
    snow_overlay = SnowDesktopOverlay(root)
    snow_overlay.show()

current_theme = THEMES[current_theme_name]  # получаем нужные цвета в глобальную переменную

root.configure(bg=current_theme["bg"])

show_splash()

# Создаем Labelы для отображения данных
time_label = tk.Label(root, text="", font=("Arial", 18), bg=current_theme["bg"], fg=current_theme["fg"])
city_label = tk.Label(root, text=CITY, font=("Arial", 18, 'italic'), bg=current_theme["bg"], fg=current_theme["fg"])
temper_label = tk.Label(root, text="", font=("Arial", 24), bg=current_theme["bg"], fg=current_theme["fg"])
condition_label = tk.Label(root, text="", font=("Arial", 18, 'italic'), wraplength=380, justify='center', bg=current_theme["bg"], fg=current_theme["fg"])
icon_label = tk.Label(root, image="", bg=current_theme["bg"])
author_label = tk.Label(root, text=ABOUT, font=("Arial", 9, 'italic'), bg=current_theme["bg"], fg=current_theme["fg"])

# Создаём кнопку настроек
settings_frame = tk.Frame(root, bg=current_theme["bg"], bd=0, highlightthickness=0)
settings_frame.place(x=360, y=280, width=30, height=30)
settings_img = Image.open(resource_path("./resources/images/settings_icon.ico"))
settings_img = settings_img.resize((30, 30), Image.LANCZOS)
settings_photo = ImageTk.PhotoImage(settings_img)

settings_button = tk.Button(
    settings_frame,
    image=settings_photo,
    bg=current_theme["bg"],
    activebackground=current_theme["button_active"],
    bd=0,
    highlightthickness=0,
    relief='flat',
    command=open_settings
)

settings_button.image = settings_photo  # Сохраняем ссылку на изображение
settings_button.pack(fill='both', expand=True)
settings_button.bind("<Enter>", on_enter_settings)
settings_button.bind("<Leave>", on_leave_settings)

# Создаём кнопку переключения в режим виджета и обратно
pin_frame = tk.Frame(root, bg=current_theme["bg"], bd=0, highlightthickness=0)
pin_frame.place(x=10, y=10, width=30, height=30)
pin_img = Image.open(resource_path("./resources/images/pin_icon.ico"))
pin_img = pin_img.resize((30, 30), Image.LANCZOS)
pin_photo = ImageTk.PhotoImage(pin_img)

pin_button = tk.Button(
   pin_frame,
   image=pin_photo,
   bg=current_theme["bg"],
   activebackground=current_theme["button_active"],
   bd=0,
   highlightthickness=0,
   relief='flat',
   command=toggle_widget_mode
)

pin_button.image = pin_photo  # Сохраняем ссылку на изображение
pin_button.pack(fill='both', expand=True)
pin_button.bind("<Enter>", on_enter_pin)
pin_button.bind("<Leave>", on_leave_pin)

# Запускаем обновление
update_time()
update_weather_data()
update_auto_theme()

# Показываем элементы если не в режиме виджета
if not WIDGET_MODE:
    time_label.pack(pady=3)
    city_label.pack(pady=3)
    temper_label.pack(pady=3)
    condition_label.pack(pady=3)
    icon_label.pack(pady=3)
    author_label.pack(pady=3, side=tk.BOTTOM)

# Запуск основного цикла приложения
try:
    root.mainloop()
finally:
    # При выходе из приложения останавливаем все звуки
    if SOUND_INITIALIZED:
        mixer.quit()
    pygame.quit()
    # Останавливаем снег, если он запущен
    if snow_overlay is not None:
        snow_overlay.quit()