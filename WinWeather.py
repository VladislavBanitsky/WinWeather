import tkinter as tk
from tkinter import ttk
from datetime import datetime
import requests
from urllib.request import urlopen
from PIL import Image, ImageTk

API_WEATHER_KEY = "c866db0d4955404eb89124646253007"
CITY = "Санкт-Петербург"  # город
TEMP_UNIT = "°C"  # единица измерения температуры
TIME_FORMAT = "%H:%M:%S    %d.%m.%Y"  # формат времени
LANGUAGE = "ru"  # язык
THEME = "light"  # тема


# Цветовые схемы для тем
THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#000000",
        "secondary_bg": "#f0f0f0",
        "button_bg": "#f0f0f0",
        "button_fg": "#555555",
        "button_active": "#e0e0e0",
        "text_highlight": "#333333"
    },
    "dark": {
        "bg": "#2d2d2d",
        "fg": "#ffffff",
        "secondary_bg": "#3d3d3d",
        "button_bg": "#4d4d4d",
        "button_fg": "#dddddd",
        "button_active": "#5d5d5d",
        "text_highlight": "#eeeeee"
    }
}


# Функция для изменения темы
def apply_theme():
    current_theme = THEMES[THEME]
    root.configure(bg=current_theme["bg"])
    
    for widget in [time_label, temper_label, condition_label, author_label]:
        widget.configure(bg=current_theme["bg"], fg=current_theme["fg"])
    
    icon_label.configure(bg=current_theme["bg"])
    settings_button.configure(
        bg=current_theme["button_bg"],
        activebackground=current_theme["button_active"]
    )


# Функция запроса погодных данных
def get_weather_data():
    try:  # если API доступен
        r = requests.get(f"https://api.weatherapi.com/v1/current.json?key={API_WEATHER_KEY}&q={CITY}&aqi=yes&lang={LANGUAGE}")
        current_weather = r.json()
        temper = int(current_weather["current"]["temp_c"]) if TEMP_UNIT == "°C" else int(current_weather["current"]["temp_f"])
        condition = current_weather["current"]["condition"]["text"]
        icon = urlopen("https:" + current_weather["current"]["condition"]["icon"])
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


# Функция для отображения окна Настройки
def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Настройки" if LANGUAGE == "ru" else "Settings")
    settings_window.geometry("300x300")
    settings_window.resizable(width=False, height=False)
    
    # Применяем текущую тему к окну настроек
    current_theme = THEMES[THEME]
    settings_window.configure(bg=current_theme["bg"])
    
    city_var = tk.StringVar(value=CITY)
    time_format_var = tk.StringVar(value=TIME_FORMAT)
    temp_unit_var = tk.StringVar(value=TEMP_UNIT)
    language_var = tk.StringVar(value=LANGUAGE)
    theme_var = tk.StringVar(value=THEME)
    
    # Функция для создания стилизованных элементов
    def create_setting_row(parent, label_text, control_widget):
        frame = ttk.Frame(parent)
        frame.pack(pady=5, fill='x', padx=10)
        
        label = tk.Label(frame, text=label_text, bg=current_theme["bg"], fg=current_theme["fg"])
        label.pack(side='left')
        
        control_widget(frame).pack(side='right', expand=True, fill='x')
        return frame
    
    # Город
    create_setting_row(settings_window, 
                      "Город:" if LANGUAGE == "ru" else "City:",
                      lambda f: ttk.Entry(f, textvariable=city_var))
    
    # Формат времени
    create_setting_row(settings_window, 
                       "Формат времени:" if LANGUAGE == "ru" else "Time format:",
                       lambda f: ttk.Combobox(f, textvariable=time_format_var, 
                                              values=["%H:%M:%S    %d.%m.%y",
                                                      "%H:%M:%S    %d.%m.%Y",
                                                      "%H:%M:%S    %m/%d/%y",
                                                      "%H:%M:%S    %m/%d/%Y",
                                                      "%H:%M:%S    %y-%m-%d",
                                                      "%H:%M:%S    %Y-%m-%d"],
                                              state="readonly"))
    
    # Единицы температуры
    create_setting_row(settings_window, 
                      "Единицы температуры:" if LANGUAGE == "ru" else "Temperature units:",
                      lambda f: ttk.Combobox(f, textvariable=temp_unit_var, 
                                            values=["°C", "°F"], state="readonly"))
    
    # Язык
    create_setting_row(settings_window, 
                      "Язык:" if LANGUAGE == "ru" else "Language:",
                      lambda f: ttk.Combobox(f, textvariable=language_var, 
                                           values=["ru", "en"], state="readonly"))
    
    # Тема
    create_setting_row(settings_window, 
                      "Тема:" if LANGUAGE == "ru" else "Theme:",
                      lambda f: ttk.Combobox(f, textvariable=theme_var, 
                                           values=["light", "dark"], state="readonly"))
    
    # Кнопка сохранения
    def save_settings():
        global CITY, TEMP_UNIT, TIME_FORMAT, LANGUAGE, THEME
        CITY = city_var.get()
        TEMP_UNIT = temp_unit_var.get()
        TIME_FORMAT = time_format_var.get()
        LANGUAGE = language_var.get()
        THEME = theme_var.get()
        apply_theme()
        update_weather_data()
        settings_window.destroy()
    
    save_button = ttk.Button(settings_window, 
                            text="Сохранить" if LANGUAGE == "ru" else "Save", 
                            command=save_settings)
    save_button.pack(pady=10)


# Эффект при наведении для кнопки Настройки
def on_enter(e):
    settings_button['bg'] = THEMES[THEME]["button_active"]


def on_leave(e):
    settings_button['bg'] = THEMES[THEME]["button_bg"]


# Создаем окно
root = tk.Tk()
root.title("WinWeather")
root.geometry("330x230")
root.resizable(width=False, height=False)
root.iconbitmap('WinWeather.ico')  

# Создаем Labelы для отображения данных
time_label = tk.Label(root, text="", font=("Arial", 18))
time_label.pack(pady=3)
temper_label = tk.Label(root, text="", font=("Arial", 24))
temper_label.pack(pady=3)
condition_label = tk.Label(root, text="", font=("Arial", 18, 'italic'))
condition_label.pack(pady=3)
icon_label = tk.Label(root, image="")
icon_label.pack(pady=3)
author_label = tk.Label(root, text="Vladislav Banitsky", font=("Arial", 9, 'italic'))
author_label.pack(pady=3, side = tk.BOTTOM)

# Создаём кнопку настроек
settings_frame = tk.Frame(root, bg='#f0f0f0', bd=0, highlightthickness=0)
settings_frame.place(x=290, y=190, width=30, height=30)
settings_img = Image.open("settings_icon.ico")
settings_img = settings_img.resize((30, 30), Image.LANCZOS)
settings_photo = ImageTk.PhotoImage(settings_img)

settings_button = tk.Button(
    settings_frame,
    image=settings_photo,
    bg='#f0f0f0',
    activebackground='#e0e0e0',
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


