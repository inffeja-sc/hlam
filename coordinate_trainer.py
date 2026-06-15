import tkinter as tk
from tkinter import ttk, messagebox
import random
import math

class FullCoordinateTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("Тренажёр координат - Полная система координат")
        self.root.geometry("950x800")
        self.root.configure(bg='#f0f0f0')
        
        # Размеры координатной плоскости
        self.width = 700
        self.height = 500
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        
        # Масштаб: 1 единица = 30 пикселей
        self.scale = 30
        self.range_x = 11
        self.range_y = 8
        
        # Переменные тренажёра
        self.mode = "point_to_coords"
        self.current_point = None
        self.user_point = None
        self.score = 0
        self.attempts = 0
        self.after_id = None
        
        self.setup_ui()
        self.new_task()
    
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Верхняя панель
        control_frame = tk.Frame(main_frame, bg='#f0f0f0')
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        mode_frame = tk.LabelFrame(control_frame, text="Режим работы", font=("Arial", 10, "bold"), bg='#f0f0f0')
        mode_frame.pack(side=tk.LEFT, padx=5)
        
        self.mode_var = tk.StringVar(value="Определение координат")
        rb1 = tk.Radiobutton(mode_frame, text="📖 Определение координат (по картинке)", 
                            variable=self.mode_var, value="Определение координат",
                            command=self.change_mode, bg='#f0f0f0')
        rb1.pack(anchor=tk.W, padx=5, pady=2)
        
        rb2 = tk.Radiobutton(mode_frame, text="✏️ Построение точки (по координатам)", 
                            variable=self.mode_var, value="Построение точки",
                            command=self.change_mode, bg='#f0f0f0')
        rb2.pack(anchor=tk.W, padx=5, pady=2)
        
        stats_frame = tk.LabelFrame(control_frame, text="Статистика", font=("Arial", 10, "bold"), bg='#f0f0f0')
        stats_frame.pack(side=tk.LEFT, padx=20)
        
        self.score_label = tk.Label(stats_frame, text=f"✅ Правильно: {self.score}", 
                                    font=("Arial", 11), bg='#f0f0f0', fg='green')
        self.score_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.attempts_label = tk.Label(stats_frame, text=f"📊 Всего заданий: {self.attempts}", 
                                       font=("Arial", 11), bg='#f0f0f0')
        self.attempts_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.new_task_btn = tk.Button(control_frame, text="🎲 Новое задание", 
                                      command=self.manual_new_task, font=("Arial", 10, "bold"),
                                      bg='#4CAF50', fg='white', padx=15, pady=5)
        self.new_task_btn.pack(side=tk.RIGHT, padx=10)
        
        canvas_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        canvas_frame.pack(pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, width=self.width, height=self.height, 
                                bg='white', highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        task_frame = tk.Frame(main_frame, bg='#f0f0f0')
        task_frame.pack(fill=tk.X, pady=10)
        
        self.task_label = tk.Label(task_frame, text="", font=("Arial", 14, "bold"), 
                                   bg='#f0f0f0', fg='#2196F3')
        self.task_label.pack(pady=5)
        
        # Панель ввода ответа
        input_frame = tk.Frame(main_frame, bg='#f0f0f0')
        input_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(input_frame, text="Ваш ответ:", font=("Arial", 12, "bold"), bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        
        # Поле ввода
        self.answer_entry = tk.Entry(input_frame, font=("Arial", 14), width=25, relief=tk.SUNKEN, bd=2)
        self.answer_entry.pack(side=tk.LEFT, padx=10)
        self.answer_entry.bind("<Return>", lambda event: self.check_answer())
        
        self.check_btn = tk.Button(input_frame, text="✅ Проверить", command=self.check_answer,
                                   font=("Arial", 11, "bold"), bg='#FF9800', fg='white', padx=20, pady=5)
        self.check_btn.pack(side=tk.LEFT, padx=10)
        
        # Подсказка под полем ввода
        hint_frame = tk.Frame(main_frame, bg='#f0f0f0')
        hint_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.hint_label = tk.Label(hint_frame, text="💡 Пример ввода: 3, -2  (сначала X, потом Y, через запятую)", 
                                   font=("Arial", 10, "italic"), bg='#f0f0f0', fg='#666')
        self.hint_label.pack()
        
        # Панель обратной связи
        self.feedback_label = tk.Label(main_frame, text="", font=("Arial", 12), 
                                       bg='#f0f0f0', wraplength=800)
        self.feedback_label.pack(pady=10)
        
        # Информационная панель
        info_frame = tk.Frame(main_frame, bg='#e0e0e0', relief=tk.GROOVE, bd=1)
        info_frame.pack(fill=tk.X, pady=10)
        
        info_text = "📐 Система координат: центр (0,0) | Оси X (горизонталь) и Y (вертикаль) | "
        info_text += "Каждое деление = 1 единица\n⌨️ Нажмите Enter для быстрой проверки ответа"
        tk.Label(info_frame, text=info_text, font=("Arial", 9), bg='#e0e0e0', justify=tk.LEFT).pack(pady=5)
        
        self.draw_coordinate_system()
    
    def draw_coordinate_system(self):
        self.canvas.delete("all")
        
        for i in range(-self.range_x, self.range_x + 1):
            x = self.center_x + i * self.scale
            if 0 <= x <= self.width:
                self.canvas.create_line(x, 0, x, self.height, fill='#e0e0e0', width=1)
                y = self.center_y + i * self.scale
                if 0 <= y <= self.height:
                    self.canvas.create_line(0, y, self.width, y, fill='#e0e0e0', width=1)
        
        self.canvas.create_line(0, self.center_y, self.width, self.center_y, fill='black', width=3, arrow=tk.LAST, arrowshape=(10,12,5))
        self.canvas.create_line(self.center_x, self.height, self.center_x, 0, fill='black', width=3, arrow=tk.LAST, arrowshape=(10,12,5))
        
        self.canvas.create_text(self.width - 20, self.center_y - 15, text="X", font=("Arial", 14, "bold"), fill='black')
        self.canvas.create_text(self.center_x + 20, 15, text="Y", font=("Arial", 14, "bold"), fill='black')
        self.canvas.create_text(self.center_x - 10, self.center_y + 10, text="0", font=("Arial", 12, "bold"), fill='red')
        
        for i in range(-self.range_x, self.range_x + 1):
            if i == 0:
                continue
            x = self.center_x + i * self.scale
            if 0 <= x <= self.width:
                self.canvas.create_line(x, self.center_y - 5, x, self.center_y + 5, fill='black', width=2)
                if abs(i) <= 10:
                    self.canvas.create_text(x, self.center_y + 15, text=str(i), font=("Arial", 9), fill='blue')
            y = self.center_y - i * self.scale
            if 0 <= y <= self.height:
                self.canvas.create_line(self.center_x - 5, y, self.center_x + 5, y, fill='black', width=2)
                if abs(i) <= 7:
                    self.canvas.create_text(self.center_x - 15, y, text=str(i), font=("Arial", 9), fill='blue')
        
        self.canvas.create_polygon(self.width-10, self.center_y-5, self.width, self.center_y, self.width-10, self.center_y+5, fill='black')
        self.canvas.create_polygon(self.center_x-5, 10, self.center_x, 0, self.center_x+5, 10, fill='black')
    
    def draw_point(self, x, y, color, show_label=False):
        px = self.center_x + x * self.scale
        py = self.center_y - y * self.scale
        radius = 7
        self.canvas.create_oval(px - radius, py - radius, px + radius, py + radius, fill=color, outline=color, width=2)
        if show_label:
            offset_x = 12 if x >= 0 else -45
            offset_y = -15 if y >= 0 else 15
            self.canvas.create_text(px + offset_x, py + offset_y, text=f"({x},{y})", font=("Arial", 10, "bold"), fill=color)
    
    def change_mode(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.mode = "point_to_coords" if self.mode_var.get() == "Определение координат" else "coords_to_point"
        self.new_task()
    
    def new_task(self):
        print("new_task вызван")
        
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
            
        x = random.randint(-8, 8)
        y = random.randint(-6, 6)
        self.current_point = (x, y)
        self.user_point = None
        
        self.draw_coordinate_system()
        
        if self.mode == "point_to_coords":
            self.draw_point(x, y, 'red', show_label=False)
            self.task_label.config(text="📌 Определите координаты красной точки")
            self.answer_entry.config(state=tk.NORMAL)
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.focus()
            self.check_btn.config(state=tk.NORMAL, text="✅ Проверить")
            # Меняем подсказку для режима определения координат
            self.hint_label.config(text="💡 Пример ввода: 3, -2  (сначала X, потом Y, через запятую)", fg='#666')
        else:
            self.task_label.config(text=f"🎯 Поставьте точку с координатами ({x}, {y})")
            self.answer_entry.config(state=tk.DISABLED)
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.insert(0, "Кликните на график")
            self.answer_entry.config(fg='grey')
            self.check_btn.config(state=tk.NORMAL, text="✅ Проверить")
            # Меняем подсказку для режима построения
            self.hint_label.config(text="💡 Кликните мышкой на координатной плоскости в нужном месте", fg='#666')
        
        self.feedback_label.config(text="")
    
    def manual_new_task(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.new_task()
    
    def on_canvas_click(self, event):
        if self.mode == "coords_to_point" and self.user_point is None:
            x_pixel = event.x - self.center_x
            y_pixel = self.center_y - event.y
            x = round(x_pixel / self.scale)
            y = round(y_pixel / self.scale)
            
            if -10 <= x <= 10 and -7 <= y <= 7:
                self.user_point = (x, y)
                self.draw_point(x, y, 'blue', show_label=False)
                self.check_answer()
            else:
                self.feedback_label.config(text="⚠️ Точка выходит за пределы координатной плоскости! (X от -10 до 10, Y от -7 до 7)", fg='orange')
    
    def check_answer(self):
        print("check_answer вызван")
        
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        
        self.attempts += 1
        
        if self.mode == "point_to_coords":
            answer = self.answer_entry.get().strip()
            
            if answer == "":
                self.feedback_label.config(text="❌ Введите координаты! Например: 3, -2", fg='red')
                self.attempts -= 1
                self.update_score_display()
                return
            
            try:
                # Очищаем от скобок и пробелов
                answer = answer.replace('(', '').replace(')', '').replace(' ', '')
                if ',' in answer:
                    x_str, y_str = answer.split(',')
                    x = int(x_str)
                    y = int(y_str)
                    
                    if (x, y) == self.current_point:
                        self.score += 1
                        self.feedback_label.config(text=f"✅ ПРАВИЛЬНО! Точка имеет координаты ({x},{y})", fg='green')
                        self.draw_point(self.current_point[0], self.current_point[1], 'red', show_label=True)
                        self.answer_entry.config(state=tk.DISABLED)
                        self.check_btn.config(state=tk.DISABLED)
                        self.update_score_display()
                        # Показываем временную подсказку
                        self.hint_label.config(text="🎉 Отлично! Следующее задание через 2 секунды...", fg='green')
                        print("Запланирован переход через 2 секунды")
                        self.after_id = self.root.after(2000, self.new_task)
                    else:
                        self.feedback_label.config(text=f"❌ НЕПРАВИЛЬНО! Попробуйте ещё раз. (Ожидалось {self.current_point})", fg='red')
                        self.attempts -= 1
                        self.update_score_display()
                        self.answer_entry.delete(0, tk.END)
                        self.answer_entry.focus()
                        return
                else:
                    self.feedback_label.config(text="❌ Неверный формат! Используйте: x, y (например: 3, -2)", fg='red')
                    self.attempts -= 1
                    self.update_score_display()
                    self.answer_entry.delete(0, tk.END)
                    self.answer_entry.focus()
                    return
            except ValueError:
                self.feedback_label.config(text="❌ Ошибка! Введите целые числа через запятую. Например: -3, 5", fg='red')
                self.attempts -= 1
                self.update_score_display()
                self.answer_entry.delete(0, tk.END)
                self.answer_entry.focus()
                return
        else:
            # Режим построения точки
            if self.user_point is None:
                self.feedback_label.config(text="⚠️ Сначала поставьте точку на координатной плоскости!", fg='orange')
                self.attempts -= 1
                self.update_score_display()
                return
            
            if self.user_point == self.current_point:
                self.score += 1
                self.feedback_label.config(text=f"✅ ПРАВИЛЬНО! Точка в ({self.user_point[0]},{self.user_point[1]})", fg='green')
                self.draw_point(self.current_point[0], self.current_point[1], 'blue', show_label=True)
                self.check_btn.config(state=tk.DISABLED)
                self.update_score_display()
                self.hint_label.config(text="🎉 Отлично! Следующее задание через 2 секунды...", fg='green')
                print("Запланирован переход через 2 секунды")
                self.after_id = self.root.after(2000, self.new_task)
            else:
                self.feedback_label.config(text=f"❌ НЕПРАВИЛЬНО! Нужно было поставить точку в {self.current_point}", fg='red')
                self.draw_point(self.current_point[0], self.current_point[1], 'green', show_label=True)
                self.check_btn.config(state=tk.DISABLED)
                self.update_score_display()
                self.hint_label.config(text="💡 Следующее задание через 2 секунды...", fg='orange')
                print("Запланирован переход через 2 секунды")
                self.after_id = self.root.after(2000, self.new_task)
    
    def update_score_display(self):
        self.score_label.config(text=f"✅ Правильно: {self.score}")
        self.attempts_label.config(text=f"📊 Всего заданий: {self.attempts}")

# Версия для Android
class AndroidCoordinateTrainer(FullCoordinateTrainer):
    def __init__(self, root):
        self.width = 550
        self.height = 450
        self.scale = 30
        super().__init__(root)
        self.root.geometry("900x950")
    
    def setup_ui(self):
        super().setup_ui()
        self.check_btn.config(height=2, width=15, font=("Arial", 14, "bold"))
        self.new_task_btn.config(height=2, width=15, font=("Arial", 12, "bold"))
        self.answer_entry.config(font=("Arial", 18), height=2)
        self.task_label.config(font=("Arial", 16, "bold"))
        self.feedback_label.config(font=("Arial", 14))
        self.hint_label.config(font=("Arial", 12, "italic"))

if __name__ == "__main__":
    root = tk.Tk()
    import sys
    if 'android' in sys.platform or 'linux' in sys.platform:
        app = AndroidCoordinateTrainer(root)
    else:
        app = FullCoordinateTrainer(root)
    root.mainloop()
