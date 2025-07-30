import tkinter as tk
from datetime import datetime
import requests
from urllib.request import urlopen
from PIL import ImageTk

API_WEATHER_KEY = "c866db0d4955404eb89124646253007"
CITY = "Санкт-Петербург"

def get_weather_data():
    try:  # если API доступен
        r = requests.get(f"https://api.weatherapi.com/v1/current.json?key={API_WEATHER_KEY}&q={CITY}&aqi=yes&lang=ru")
        current_weather = r.json()
        temper = int(current_weather["current"]["temp_c"])
        condition = current_weather["current"]["condition"]["text"]
        icon = urlopen("https:" + current_weather["current"]["condition"]["icon"])
    except:  # иначе отображаем сообщение об ошибке
        temper = 0
        condition = "Нет связи :("
        icon = None
    return temper, condition, icon


# Функция для обновления времени
def update_time():
    current_time = datetime.now().strftime("%d.%m.%y    %H:%M:%S")  # Получаем текущее время
    time_label.config(text=f"{current_time}")  # Обновляем текст Label
    time_label.after(1000, update_time)  # Планируем обновление через 1 секунду


def update_waether_data():
    temper, condition, icon = get_weather_data()  # Получаем текущую температуру
    
    temper_label.config(text=f"{temper}°C")  # Обновляем текст Label
    condition_label.config(text=f"{condition}")  # Обновляем текст Label
    
    if icon:  # только если иконка доступна
        # Считываем данные и создаем изображение
        image_data = icon.read()
        img = ImageTk.PhotoImage(data=image_data)
        icon_label.config(image=img)
        # Сохраняем ссылку на изображение, чтобы оно не удалилось
        icon_label.image = img
    
    condition_label.after(60000, update_waether_data)  # Планируем обновление через 1 минуту

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

# Запускаем обновление
update_time()
update_waether_data()

# Запуск основного цикла приложения
root.mainloop()


