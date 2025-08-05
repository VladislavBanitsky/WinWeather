import tkinter as tk
from tkinter import ttk
from datetime import datetime
import requests
from urllib.request import urlopen
from PIL import Image, ImageTk
import json
import sys
import os
import pygame  # для работы со звуком
from pygame import mixer


HEIGHT = 400
WIDTH = 320


# Настройки по умолчанию
DEFAULT_SETTINGS = {
    "API_WEATHER_KEY": "c866db0d4955404eb89124646253007",
    "CITY": "Санкт-Петербург",
    "TEMP_UNIT": "°C",
    "TIME_FORMAT": "%H:%M:%S    %d.%m.%Y",
    "LANGUAGE": "ru",
    "THEME": "light",
    "VOLUME": 0.5
}


# Цветовые схемы для тем
THEMES = {
    "light": {
        "bg": "#f0f0f0",
        "fg": "#000000",
        "button_active": "#e0e0e0"
    },
    "dark": {
        "bg": "#2d2d2d",
        "fg": "#ffffff",
        "button_active": "#5d5d5d"
    }
}


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
    current_theme = THEMES[THEME]
    root.configure(bg=current_theme["bg"])
    
    for widget in [time_label, city_label, temper_label, condition_label, author_label]:
        widget.configure(bg=current_theme["bg"], fg=current_theme["fg"])
    
    icon_label.configure(bg=current_theme["bg"])
    settings_button.configure(
        bg=current_theme["bg"],
        activebackground=current_theme["button_active"]
    )
    settings_frame.configure(bg=current_theme["bg"])


# Функция для воспроизведения звуков погоды
def play_weather_sounds(condition):
    global current_sound
    
    # Если произошда ошибка - звук не включаем
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
            sound_file = resource_path('thunder.wav')
        elif "лед" in condition_lower or "град" in condition_lower or "ice pellets" in condition_lower:
            # Воспроизводим звук града
            sound_file = resource_path('ice_pellets.wav')
        elif "дожд" in condition_lower or "лив" in condition_lower or "rain" in condition_lower:
            # Воспроизводим звук дождя
            sound_file = resource_path('rain.wav')
        elif "сне" in condition_lower or "snow" in condition_lower or "blizzard" in condition_lower:
            # Воспроизводим звук снега
            sound_file = resource_path('snow.wav')
        
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
    try:  # если API доступен
        r = requests.get(f"https://api.weatherapi.com/v1/current.json?key={API_WEATHER_KEY}&q={CITY}&aqi=yes&lang={LANGUAGE}")
        current_weather = r.json()
        temper = int(current_weather["current"]["temp_c"]) if TEMP_UNIT == "°C" else int(current_weather["current"]["temp_f"])
        condition = current_weather["current"]["condition"]["text"]
        icon = urlopen("https:" + current_weather["current"]["condition"]["icon"]) 
        # Воспроизводим звуки в соответствии с погодой
        play_weather_sounds(condition)
        
    except:  # иначе отображаем сообщение об ошибке
        temper = 0
        condition = "Нет связи :(" if LANGUAGE == "ru" else "No connection :("
        icon = None
            
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
    
    if icon:  # только если иконка доступна
        # Считываем данные и создаем изображение
        image_data = icon.read()
        img = ImageTk.PhotoImage(data=image_data)
        icon_label.config(image=img)
        # Сохраняем ссылку на изображение, чтобы оно не удалилось
        icon_label.image = img
    
    condition_label.after(60000, update_weather_data)  # Планируем обновление через 1 минуту


def update_city():
    city_label.config(text=f"{CITY}")  # Обновляем текст Label


# Функция для отображения окна Настройки
def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("WinWeather Настройки" if LANGUAGE == "ru" else "WinWeather Settings")
    center_window(settings_window, HEIGHT, WIDTH)
    settings_window.resizable(width=False, height=False)
    settings_window.iconbitmap(resource_path('WinWeather.ico'))
    
    # Применяем текущую тему к окну настроек
    current_theme = THEMES[THEME]
    settings_window.configure(bg=current_theme["bg"])
    
    # Улучшение стилей ползунка громкости и галочки включения/отключения звука
    style = ttk.Style()
    style.configure('TScale', background=current_theme["bg"], troughcolor=current_theme["bg"])
    
    city_var = tk.StringVar(value=CITY)
    time_format_var = tk.StringVar(value=TIME_FORMAT)
    temp_unit_var = tk.StringVar(value=TEMP_UNIT)
    language_var = tk.StringVar(value=LANGUAGE)
    theme_var = tk.StringVar(value=THEME)
    volume_var = tk.DoubleVar(value=VOLUME)
    
    # Создаем элементы управления с использованием grid
    row = 0
    
    # Город
    tk.Label(settings_window, text="Город:" if LANGUAGE == "ru" else "City:", 
            bg=current_theme["bg"], fg=current_theme["fg"]).grid(row=row, column=0, padx=10, pady=(50, 5), sticky='w')
    ttk.Entry(settings_window, textvariable=city_var, width=20).grid(row=row, column=1, padx=10, pady=(50, 5), sticky='ew')
    row += 1
    
    # Формат времени
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
    row += 1
    
    # Единицы температуры
    tk.Label(settings_window, text="Единицы температуры:" if LANGUAGE == "ru" else "Temperature units:", 
            bg=current_theme["bg"], fg=current_theme["fg"]).grid(row=row, column=0, padx=10, pady=5, sticky='w')
    ttk.Combobox(settings_window, textvariable=temp_unit_var, 
                values=["°C", "°F"], state="readonly", width=18).grid(row=row, column=1, padx=10, pady=5, sticky='ew')
    row += 1
    
    # Язык
    tk.Label(settings_window, text="Язык:" if LANGUAGE == "ru" else "Language:", 
            bg=current_theme["bg"], fg=current_theme["fg"]).grid(row=row, column=0, padx=10, pady=5, sticky='w')
    ttk.Combobox(settings_window, textvariable=language_var, 
                values=["ru", "en"], state="readonly", width=18).grid(row=row, column=1, padx=10, pady=5, sticky='ew')
    row += 1
    
    # Тема
    tk.Label(settings_window, text="Тема:" if LANGUAGE == "ru" else "Theme:", 
            bg=current_theme["bg"], fg=current_theme["fg"]).grid(row=row, column=0, padx=10, pady=5, sticky='w')
    ttk.Combobox(settings_window, textvariable=theme_var, 
                values=["light", "dark"], state="readonly", width=18).grid(row=row, column=1, padx=10, pady=5, sticky='ew')
    row += 1
    
    # Громкость
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
    row += 1
    
    # Кнопка сохранения
    save_button = ttk.Button(settings_window, 
                           text="Сохранить" if LANGUAGE == "ru" else "Save", 
                           command=lambda: save_settings_by_button(
                               city_var, temp_unit_var, time_format_var, 
                               language_var, theme_var, volume_var, 
                               settings_window))
    save_button.grid(row=row, column=0, columnspan=2, pady=10)
    
    # Настройка веса столбцов для правильного растяжения
    settings_window.columnconfigure(0, weight=1)
    settings_window.columnconfigure(1, weight=2)

    
# Функция для кнопки сохранения
def save_settings_by_button(city_var, temp_unit_var, time_format_var, language_var, theme_var, volume_var, settings_window):
    global CITY, TEMP_UNIT, TIME_FORMAT, LANGUAGE, THEME, VOLUME, current_sound   # сохраняем изменения глобально
    CITY = city_var.get()
    TEMP_UNIT = temp_unit_var.get()
    TIME_FORMAT = time_format_var.get()
    LANGUAGE = language_var.get()
    THEME = theme_var.get()
    VOLUME = volume_var.get()
    
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
        "VOLUME": VOLUME
    }
    save_settings(settings_to_save)
    
    apply_theme()
    update_city()
    update_weather_data()
    settings_window.destroy()


# Эффект при наведении для кнопки Настройки
def on_enter(e):
    settings_button['bg'] = THEMES[THEME]["button_active"]


def on_leave(e):
    settings_button['bg'] = THEMES[THEME]["bg"]


# Загружаем настройки при старте
settings = load_settings()
API_WEATHER_KEY = settings["API_WEATHER_KEY"]
CITY = settings["CITY"]
TEMP_UNIT = settings["TEMP_UNIT"]
TIME_FORMAT = settings["TIME_FORMAT"]
LANGUAGE = settings["LANGUAGE"]
THEME = settings["THEME"]
VOLUME = settings.get("VOLUME", 0.5)

SOUND_INITIALIZED = init_sound()
current_sound = None  # глобальная переменная для хранения текущего звука

# Создаем окно
root = tk.Tk()
root.title("WinWeather")
center_window(root, HEIGHT, WIDTH)  # root.geometry("330x280")
root.resizable(width=False, height=False)
root.iconbitmap(resource_path('WinWeather.ico'))  

# Применяем тему сразу после создания окна
current_theme = THEMES[THEME]
root.configure(bg=current_theme["bg"])

# Создаем Labelы для отображения данных
time_label = tk.Label(root, text="", font=("Arial", 18), bg=current_theme["bg"], fg=current_theme["fg"])
time_label.pack(pady=3)
city_label = tk.Label(root, text=CITY, font=("Arial", 18, 'italic'), bg=current_theme["bg"], fg=current_theme["fg"])
city_label.pack(pady=3)
temper_label = tk.Label(root, text="", font=("Arial", 24), bg=current_theme["bg"], fg=current_theme["fg"])
temper_label.pack(pady=3)
condition_label = tk.Label(root, text="", font=("Arial", 18, 'italic'), wraplength=380, justify='center', bg=current_theme["bg"], fg=current_theme["fg"])
condition_label.pack(pady=3)
icon_label = tk.Label(root, image="", bg=current_theme["bg"])
icon_label.pack(pady=3)
author_label = tk.Label(root, text="2025, Vladislav Banitsky, v. 1.0.4", font=("Arial", 9, 'italic'), bg=current_theme["bg"], fg=current_theme["fg"])
author_label.pack(pady=3, side = tk.BOTTOM)

# Создаём кнопку настроек
settings_frame = tk.Frame(root, bg=current_theme["bg"], bd=0, highlightthickness=0)
settings_frame.place(x=360, y=280, width=30, height=30)
settings_img = Image.open(resource_path("settings_icon.ico"))
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
settings_button.bind("<Enter>", on_enter)
settings_button.bind("<Leave>", on_leave)

# Запускаем обновление
update_time()
update_weather_data()

# Запуск основного цикла приложения
root.mainloop()

# При выходе из приложения останавливаем все звуки
if SOUND_INITIALIZED:
    mixer.quit()
pygame.quit()


