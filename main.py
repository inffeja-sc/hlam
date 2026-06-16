from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.core.text import Label as CoreLabel
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
import random


class CoordinateSystem(BoxLayout):
    grid_size = NumericProperty(8)
    scale = NumericProperty(45) # УВЕЛИЧИЛ МАСШТАБ (было 30)
    
    target_x = NumericProperty(0)
    target_y = NumericProperty(0)
    show_point = BooleanProperty(False) 
    
    user_x = NumericProperty(None, allownone=True)
    user_y = NumericProperty(None, allownone=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.update_canvas, pos=self.update_canvas)
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            app = App.get_running_app()
            if app.mode == 'set_point':
                center_x = self.x + self.width / 2
                center_y = self.y + self.height / 2
                
                gx = round((touch.x - center_x) / self.scale)
                gy = round((touch.y - center_y) / self.scale)
                
                gx = max(-self.grid_size, min(self.grid_size, gx))
                gy = max(-self.grid_size, min(self.grid_size, gy))
                
                self.user_x = gx
                self.user_y = gy
                self.update_canvas()
                return True 
        return super().on_touch_down(touch)
        
    def update_canvas(self, *args):
        self.canvas.clear()
        center_x = self.x + self.width / 2
        center_y = self.y + self.height / 2
        
        with self.canvas:
            # Сетка
            Color(0.9, 0.9, 0.9, 1) 
            for i in range(-self.grid_size, self.grid_size + 1):
                x = center_x + i * self.scale
                Line(points=[x, self.y, x, self.y + self.height], width=1)
            
            for i in range(-self.grid_size, self.grid_size + 1):
                y = center_y + i * self.scale
                Line(points=[self.x, y, self.x + self.width, y], width=1)
            
            # Оси
            Color(0, 0, 0, 1) 
            Line(points=[self.x, center_y, self.x + self.width, center_y], width=3) # Чуть жирнее
            Line(points=[center_x, self.y, center_x, self.y + self.height], width=3)
            
            # Подписи на осях (УВЕЛИЧЕН ШРИФТ)
            font_size = 20 # Было 14
            Color(0.2, 0.2, 0.2, 1) 
            
            for i in range(-self.grid_size, self.grid_size + 1):
                if i == 0: continue 
                
                txt_x = str(i)
                label_x = CoreLabel(text=txt_x, font_size=font_size)
                label_x.refresh()
                tx = center_x + i * self.scale - label_x.texture.width / 2
                ty = center_y - 30 # Чуть ниже оси X
                Rectangle(texture=label_x.texture, pos=(tx, ty), size=label_x.texture.size)
                
                txt_y = str(i)
                label_y = CoreLabel(text=txt_y, font_size=font_size)
                label_y.refresh()
                ty_pos = center_y + i * self.scale - label_y.texture.height / 2
                tx_pos = center_x - 30 # Чуть левее оси Y
                Rectangle(texture=label_y.texture, pos=(tx_pos, ty_pos), size=label_y.texture.size)

            # Красная точка (Цель) - УВЕЛИЧЕН РАЗМЕР
            if self.show_point:
                Color(1, 0, 0, 1)
                px = center_x + self.target_x * self.scale
                py = center_y + self.target_y * self.scale
                Ellipse(pos=(px - 12, py - 12), size=(24, 24)) # Было 16
            
            # Синяя точка (Клик) - УВЕЛИЧЕН РАЗМЕР
            if not self.show_point and self.user_x is not None:
                Color(0, 0, 1, 1) 
                px = center_x + self.user_x * self.scale
                py = center_y + self.user_y * self.scale
                Rectangle(pos=(px - 10, py - 10), size=(20, 20)) # Было 12


class TrainerApp(App):
    mode = StringProperty('set_point') 
    
    task_x = NumericProperty(0)
    task_y = NumericProperty(0)
    task_hint_text = StringProperty('')
    
    input_x = StringProperty('')
    input_y = StringProperty('')
    
    result_message = StringProperty('')
    score = NumericProperty(0)
    total_tasks = NumericProperty(0)
    
    def build(self):
        return TrainerLayout()
    
    def on_start(self):
        self.generate_new_task()
    
    def generate_new_task(self):
        x = random.randint(-6, 6)
        y = random.randint(-6, 6)
        
        self.task_x = x
        self.task_y = y
        self.task_hint_text = f'>>> ПОСТАВЬ ТОЧКУ: ({x}, {y}) <<<'
        
        self.result_message = ''
        self.input_x = ''
        self.input_y = ''
        
        root = self.root
        if root and hasattr(root, 'coord_system'):
            cs = root.coord_system
            cs.target_x = x
            cs.target_y = y
            cs.user_x = None
            cs.user_y = None
            
            if self.mode == 'find_coords':
                cs.show_point = True 
            else:
                cs.show_point = False 
                
            cs.update_canvas()
    
    def check_answer(self):
        user_x, user_y = 0, 0
        
        if self.mode == 'find_coords':
            try:
                user_x = int(self.input_x) if self.input_x else 0
                user_y = int(self.input_y) if self.input_y else 0
            except ValueError:
                self.result_message = 'Введите числа!'
                return
        else:
            cs = self.root.coord_system
            if cs.user_x is None:
                self.result_message = 'Сначала кликните по сетке!'
                return
            user_x = cs.user_x
            user_y = cs.user_y
        
        self.total_tasks += 1
        
        if user_x == self.task_x and user_y == self.task_y:
            self.result_message = f'Верно! ({self.task_x}, {self.task_y})'
            self.score += 1
        else:
            self.result_message = f'Неверно. Ответ: ({self.task_x}, {self.task_y})'
    
    def next_task(self):
        self.generate_new_task()
    
    def toggle_mode(self):
        self.mode = 'find_coords' if self.mode == 'set_point' else 'set_point'
        self.generate_new_task()
    
    def get_mode_text(self):
        if self.mode == 'set_point':
            return 'Режим: Кликни в точку\n(Задание: см. ниже)'
        else:
            return 'Режим: Найди координаты\n(Смотри на красную точку)'


class TrainerLayout(BoxLayout):
    pass

if __name__ == '__main__':
    TrainerApp().run()
