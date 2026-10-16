# TrinityOS 1.1 - single-file Kivy app for Pydroid 3
# No third-party packages beyond Kivy are required.
import ast
import json
import math
import operator
import random
import time
import webbrowser
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.network.urlrequest import UrlRequest

APP_NAME = 'TrinityOS'
APP_VERSION = '1.3'
BG = (0.055, 0.075, 0.12, 1)
PANEL = (0.10, 0.14, 0.21, 1)
ACCENT = (0.25, 0.72, 0.92, 1)
TEXT = (0.92, 0.95, 1, 1)


def make_label(text='', size=18, height=None, color=TEXT, halign='center'):
    w = Label(text=str(text), font_size=sp(size), color=color, halign=halign,
              valign='middle', size_hint_y=None if height else 1, height=dp(height) if height else 0)
    w.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0] - dp(12), None)))
    return w


def sp(value):
    return dp(value)


def make_button(text, callback=None, height=50):
    b = Button(text=str(text), size_hint_y=None, height=dp(height), font_size=dp(17),
               background_normal='', background_color=PANEL, color=TEXT)
    if callback:
        b.bind(on_release=lambda *_: callback())
    b.bind(on_press=lambda inst: Animation(opacity=0.72, duration=0.06).start(inst))
    b.bind(on_release=lambda inst: Animation(opacity=1, duration=0.12).start(inst))
    return b


def make_input(hint='', text='', multiline=False, height=48, password=False):
    return TextInput(hint_text=hint, text=text, multiline=multiline, password=password,
                     size_hint_y=None, height=dp(height), font_size=dp(17),
                     foreground_color=TEXT, hint_text_color=(0.65, 0.7, 0.78, 1),
                     background_color=PANEL, cursor_color=ACCENT, padding=dp(10))


def make_page_layout():
    root = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(9))
    root.add_widget(Widget(size_hint_y=None, height=dp(2)))
    return root


def add_page_title(layout, title):
    layout.add_widget(make_label(title, 25, 42))


def add_home_button(layout, app):
    layout.add_widget(make_button('Home', app.go_home, 44))


class BaseScreen(Screen):
    def make_page(self, title):
        self.clear_widgets()
        self.root = make_page_layout()
        self.add_widget(self.root)
        add_page_title(self.root, title)
        return self.root

    def add_home(self, layout=None):
        add_home_button(layout or self.root, App.get_running_app())


class StartupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(18))
        root.add_widget(Widget())
        title = make_label('DROPLET OS', 32, 65)
        root.add_widget(title)
        root.add_widget(make_label('Starting system', 17, 36))
        bar = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(12))
        root.add_widget(bar)
        root.add_widget(Widget())
        self.add_widget(root)
        self._bar = bar
        self._elapsed = 0
        self._event = None

    def on_enter(self, *_):
        self._elapsed = 0
        if self._event:
            self._event.cancel()
        self._event = Clock.schedule_interval(self._tick, 0.04)

    def _tick(self, dt):
        self._elapsed += dt
        self._bar.value = min(100, self._elapsed / 2.2 * 100)
        if self._elapsed >= 2.2:
            if self._event:
                self._event.cancel()
                self._event = None
            App.get_running_app().open_screen('lock')
            return False
        return True


class LockScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._clock_event = None

    def on_pre_enter(self, *_):
        root = self.make_page('TrinityOS')
        self.clock_label = make_label('', 34, 58)
        self.date_label = make_label('', 18, 34)
        root.add_widget(Widget())
        root.add_widget(self.clock_label)
        root.add_widget(self.date_label)
        self.pin_input = make_input('Enter 4-digit PIN', password=True)
        app = App.get_running_app()
        if app.pin:
            root.add_widget(self.pin_input)
            root.add_widget(make_button('Unlock', self.unlock))
        else:
            root.add_widget(make_label('Ready when you are', 16, 34))
            root.add_widget(make_button('Unlock', app.go_home))
        root.add_widget(Widget())
        self.update_clock(0)
        if self._clock_event:
            self._clock_event.cancel()
        self._clock_event = Clock.schedule_interval(self.update_clock, 1)

    def on_leave(self, *_):
        if self._clock_event:
            self._clock_event.cancel()
            self._clock_event = None

    def update_clock(self, _dt):
        app = App.get_running_app()
        if hasattr(self, 'clock_label'):
            self.clock_label.text = app.get_time()
            self.date_label.text = app.get_date()

    def unlock(self):
        app = App.get_running_app()
        if self.pin_input.text == app.pin:
            app.go_home()
        else:
            self.pin_input.text = ''
            self.pin_input.hint_text = 'Incorrect PIN'


class HomeScreen(BaseScreen):
    def on_pre_enter(self, *_):
        app = App.get_running_app()
        root = self.make_page('TrinityOS')
        self.clock_label = make_label('', 31, 52)
        self.date_label = make_label('', 17, 30)
        root.add_widget(self.clock_label)
        root.add_widget(self.date_label)
        root.add_widget(make_button('Apps and Games', lambda: app.open_screen('apps')))
        root.add_widget(make_button('Settings', lambda: app.open_screen('settings')))
        root.add_widget(make_button('About TrinityOS', lambda: app.open_screen('about')))
        root.add_widget(make_button('Lock Device', app.lock_device))
        self.update_clock(0)
        self._clock_event = Clock.schedule_interval(self.update_clock, 1)

    def on_leave(self, *_):
        if getattr(self, '_clock_event', None):
            self._clock_event.cancel()

    def update_clock(self, _dt):
        app = App.get_running_app()
        if hasattr(self, 'clock_label'):
            self.clock_label.text = app.get_time()
            self.date_label.text = app.get_date()


class SettingsScreen(BaseScreen):
    def on_pre_enter(self, *_):
        app = App.get_running_app()
        root = self.make_page('Settings')
        root.add_widget(make_button('Time format: ' + ('24-hour' if app.military_time else '12-hour'), self.toggle_time))
        root.add_widget(make_button('Seconds: ' + ('Shown' if app.show_seconds else 'Hidden'), self.toggle_seconds))
        root.add_widget(make_button('Sound: ' + ('On' if app.sound_enabled else 'Off'), self.toggle_sound))
        root.add_widget(make_label('PIN security', 18, 30))
        self.pin_input = make_input('New 4-digit PIN (blank to remove)', password=True)
        root.add_widget(self.pin_input)
        root.add_widget(make_button('Save PIN settings', self.save_pin))
        root.add_widget(make_label('System information', 18, 30))
        root.add_widget(make_label('Estimated minimum: Android 8+, 2 GB RAM. Performance depends on device.', 14, 50))
        self.fps_label = make_label('FPS: measuring...', 14, 28)
        root.add_widget(self.fps_label)
        root.add_widget(make_button('Refresh system info', self.refresh_info))
        add_home_button(root, app)
        self._frames = 0
        self._fps_start = time.time()
        self._fps_event = Clock.schedule_interval(self.measure_fps, 0.1)

    def on_leave(self, *_):
        if getattr(self, '_fps_event', None):
            self._fps_event.cancel()

    def measure_fps(self, _dt):
        self._frames += 1
        elapsed = time.time() - self._fps_start
        if elapsed >= 1:
            if hasattr(self, 'fps_label'):
                self.fps_label.text = 'FPS: ' + str(round(self._frames / elapsed, 1))
            self._frames = 0
            self._fps_start = time.time()

    def toggle_time(self):
        app = App.get_running_app(); app.military_time = not app.military_time; self.on_pre_enter()

    def toggle_seconds(self):
        app = App.get_running_app(); app.show_seconds = not app.show_seconds; self.on_pre_enter()

    def toggle_sound(self):
        app = App.get_running_app(); app.sound_enabled = not app.sound_enabled; self.on_pre_enter()

    def save_pin(self):
        app = App.get_running_app(); value = self.pin_input.text.strip()
        if not value:
            app.pin = None
            self.pin_input.hint_text = 'PIN removed'
        elif len(value) == 4 and value.isdigit():
            app.pin = value
            self.pin_input.text = ''
            self.pin_input.hint_text = 'PIN saved. Lock device to test it.'
        else:
            self.pin_input.text = ''
            self.pin_input.hint_text = 'Use exactly 4 digits'

    def refresh_info(self):
        self.fps_label.text = 'TrinityOS ' + APP_VERSION + ' | Kivy app is running'


class AboutScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root = self.make_page('About')
        root.add_widget(make_label('TrinityOS ' + APP_VERSION, 23, 40))
        root.add_widget(make_label('A small experimental desktop-style system built with Python and Kivy.', 16, 75))
        root.add_widget(make_label('Made for learning, games, and tiny tools.', 15, 45))
        self.add_home()


class AppsScreen(BaseScreen):
    ITEMS = [('Math Quiz','math'),('Pong','pong'),('TPS Tester','tps'),('Tetris','tetris'),('Frogger','frogger'),('Painter','painter'),('Animator','animator'),('Trinity Files','files'),('Morse Code','morse'),('Morse Translator','translator'),('Gospel','gospel'),('Geometry Dash','geometry'),('Racing','racing'),('8-bit CPU','cpu'),('My App','myapp'),('Calculator','calculator'),('crossGPT','crossgpt'),('AI Guidebook','aiguide'),('Internet','internet'),('Football','football')]

    def on_pre_enter(self, *_):
        root = self.make_page('Apps and Games')
        scroll = ScrollView()
        grid = GridLayout(cols=2, spacing=dp(8), padding=dp(3), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        app = App.get_running_app()
        for title, name in self.ITEMS:
            grid.add_widget(make_button(title, lambda n=name: app.open_screen(n), 60))
        scroll.add_widget(grid); root.add_widget(scroll); add_home_button(root, app)


class MathScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root = self.make_page('Math Quiz'); self.score = 0; self.new_question(root)

    def new_question(self, root=None):
        if root is None: root = self.root
        if hasattr(self, 'question_label') and self.question_label.parent: root.remove_widget(self.question_label)
        if hasattr(self, 'answer_input') and self.answer_input.parent: root.remove_widget(self.answer_input)
        if hasattr(self, 'feedback') and self.feedback.parent: root.remove_widget(self.feedback)
        self.a = random.randint(1, 20); self.b = random.randint(1, 20); self.op = random.choice(['+','-','*'])
        self.question_label = make_label(f'{self.a} {self.op} {self.b} = ?', 25, 55); root.add_widget(self.question_label)
        self.answer_input = make_input('Your answer'); root.add_widget(self.answer_input)
        self.feedback = make_label('Score: ' + str(self.score), 16, 35); root.add_widget(self.feedback)
        root.add_widget(make_button('Check answer', self.check))
        root.add_widget(make_button('New question', lambda: self.new_question()))
        add_home_button(root, App.get_running_app())

    def check(self):
        expected = self.a + self.b if self.op == '+' else self.a - self.b if self.op == '-' else self.a * self.b
        try: ok = int(self.answer_input.text.strip()) == expected
        except ValueError: ok = False
        if ok: self.score += 1; self.feedback.text = 'Correct! Score: ' + str(self.score)
        else: self.feedback.text = 'Not quite. Score: ' + str(self.score)


class PongField(Widget):
    """Large Pong field. In 2-player mode each player controls their own half."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mode = 'AI'
        self.left_y = self.right_y = 0.5
        self.ball_x = self.ball_y = 0.5
        self.vx = 0.48
        self.vy = 0.12
        self.player_score = self.opponent_score = 0
        self.running = True
        self.bind(pos=self.draw, size=self.draw)
        self.event = Clock.schedule_interval(self.update, 1/60)
        self.draw()

    def set_mode(self, mode):
        self.mode = mode
        self.restart()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.move_paddle(touch.x, touch.y)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self.move_paddle(touch.x, touch.y)
            return True
        return super().on_touch_move(touch)

    def move_paddle(self, x, y):
        normalized_y = max(0.12, min(0.88, (y-self.y)/max(1, self.height)))
        if self.mode == 'AI' or x < self.center_x:
            self.left_y = normalized_y
        else:
            self.right_y = normalized_y
        self.draw()

    def reset_ball(self, direction=None):
        self.ball_x = self.ball_y = 0.5
        direction = random.choice([-1, 1]) if direction is None else direction
        self.vx = 0.52 * direction
        self.vy = random.uniform(-0.18, 0.18)

    def bounce_from_paddle(self, paddle_y, direction):
        # Contact near the centre produces a nearly horizontal shot; edges add angle.
        offset = max(-1.0, min(1.0, (self.ball_y - paddle_y) / 0.13))
        self.vx = abs(self.vx) * direction * 1.035
        self.vy = offset * 0.72
        self.ball_x = 0.085 if direction > 0 else 0.915

    def update(self, dt):
        if not self.parent or not self.running or self.width < 10 or self.height < 10:
            return
        dt = min(dt, 0.04)
        self.ball_x += self.vx * dt
        self.ball_y += self.vy * dt
        radius = 0.018
        if self.ball_y < radius:
            self.ball_y = radius; self.vy = abs(self.vy)
        elif self.ball_y > 1-radius:
            self.ball_y = 1-radius; self.vy = -abs(self.vy)

        # AI tracks the ball, but deliberately has limited speed and reaction delay.
        if self.mode == 'AI' and self.vx > 0:
            target = self.ball_y + random.uniform(-0.012, 0.012)
            self.right_y += max(-0.43*dt, min(0.43*dt, target-self.right_y))

        half_paddle = 0.13 / 2
        if self.vx < 0 and self.ball_x <= 0.085:
            if abs(self.ball_y-self.left_y) <= half_paddle + radius:
                self.bounce_from_paddle(self.left_y, 1)
        elif self.vx > 0 and self.ball_x >= 0.915:
            if abs(self.ball_y-self.right_y) <= half_paddle + radius:
                self.bounce_from_paddle(self.right_y, -1)

        if self.ball_x < -0.025:
            self.opponent_score += 1; self.reset_ball(1)
        elif self.ball_x > 1.025:
            self.player_score += 1; self.reset_ball(-1)
        if self.player_score >= 5 or self.opponent_score >= 5:
            self.running = False
        self.draw()

    def restart(self):
        self.left_y = self.right_y = 0.5
        self.player_score = self.opponent_score = 0
        self.running = True
        self.reset_ball(random.choice([-1, 1]))
        self.draw()

    def draw(self, *_):
        self.canvas.clear()
        with self.canvas:
            Color(0.025, 0.04, 0.07, 1); Rectangle(pos=self.pos, size=self.size)
            Color(0.22, 0.34, 0.43, 1)
            for i in range(18): Rectangle(pos=(self.center_x-dp(1), self.y+i*self.height/18), size=(dp(2), self.height/36))
            Color(0.25, 0.72, 0.92, 1)
            Rectangle(pos=(self.x+self.width*0.035, self.y+(self.left_y-0.065)*self.height), size=(self.width*0.022, self.height*0.13))
            Color(0.95, 0.55, 0.25, 1)
            Rectangle(pos=(self.x+self.width*0.943, self.y+(self.right_y-0.065)*self.height), size=(self.width*0.022, self.height*0.13))
            Color(1, 1, 1, 1)
            d = min(self.width, self.height)*0.027
            Ellipse(pos=(self.x+self.ball_x*self.width-d/2, self.y+self.ball_y*self.height-d/2), size=(d,d))

    def stop(self):
        self.running = False
        if self.event: self.event.cancel(); self.event = None


class PongScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root = self.make_page('Pong')
        root.add_widget(make_label('Drag on the left to move blue. In 2-player mode, drag on the right for orange.', 13, 34))
        mode_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
        mode_row.add_widget(make_button('Player vs AI', lambda: self.change_mode('AI'), 38))
        mode_row.add_widget(make_button('Player vs Player', lambda: self.change_mode('PVP'), 38))
        root.add_widget(mode_row)
        self.field = PongField(size_hint_y=1)
        root.add_widget(self.field)
        self.score_label = make_label('Blue 0  |  Orange 0', 16, 28); root.add_widget(self.score_label)
        root.add_widget(make_button('Restart match', self.restart, 40)); self.add_home(root)
        self._score_event = Clock.schedule_interval(self.update_score, 0.12)
    def change_mode(self, mode):
        if hasattr(self, 'field'):
            self.field.set_mode(mode)
            self.update_score(0)
    def update_score(self, _dt):
        if hasattr(self, 'field'):
            f = self.field
            opponent = 'AI' if f.mode == 'AI' else 'Player 2'
            status = ' | Match over' if not f.running else ''
            self.score_label.text = f'Blue {f.player_score}  |  {opponent} {f.opponent_score}{status}'
    def restart(self):
        if getattr(self, '_score_event', None): self._score_event.cancel()
        self.on_pre_enter()
    def on_leave(self, *_):
        if getattr(self, '_score_event', None): self._score_event.cancel(); self._score_event = None
        if getattr(self, 'field', None): self.field.stop()


class TPSScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root = self.make_page('TPS Tester'); self.count = 0; self.running = False
        self.info = make_label('Tap Start, then tap as fast as you can for 5 seconds.', 16, 65); root.add_widget(self.info)
        self.count_label = make_label('Taps: 0', 24, 50); root.add_widget(self.count_label)
        root.add_widget(make_button('Start test', self.start)); root.add_widget(make_button('Tap!', self.tap)); self.add_home(root)

    def start(self): self.count = 0; self.running = True; self.end_at = time.time() + 5; self.info.text = 'Go! 5 seconds.'; Clock.schedule_once(self.finish, 5)
    def tap(self):
        if self.running: self.count += 1; self.count_label.text = 'Taps: ' + str(self.count)
    def finish(self, *_):
        self.running = False
        if hasattr(self, 'info'): self.info.text = f'Result: {self.count} taps in 5 seconds ({self.count/5:.1f} taps/sec).'


class TetrisBoard(Widget):
    SHAPES = [
        [(0,0),(0,1),(0,2),(0,3)], [(0,0),(1,0),(1,1),(1,2)],
        [(0,2),(1,0),(1,1),(1,2)], [(0,0),(0,1),(1,0),(1,1)],
        [(0,1),(0,2),(1,0),(1,1)], [(0,1),(1,0),(1,1),(1,2)],
        [(0,0),(0,1),(1,1),(1,2)]
    ]
    COLORS=[(0.2,0.75,0.95,1),(0.95,0.55,0.2,1),(0.35,0.55,1,1),(0.95,0.8,0.2,1),(0.3,0.85,0.5,1),(0.75,0.4,0.95,1),(0.95,0.35,0.45,1)]
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rows=16; self.cols=10; self.board=[[None]*self.cols for _ in range(self.rows)]
        self.score=0; self.lines=0; self.game_over=False; self.new_piece()
        self.bind(pos=self.draw,size=self.draw)
        self.event=Clock.schedule_interval(self.tick,0.55)
        self.draw()
    def new_piece(self):
        self.kind=random.randrange(len(self.SHAPES)); self.shape=[(r,c) for r,c in self.SHAPES[self.kind]]; self.pr=0; self.pc=3
        if self.collides(self.pr,self.pc,self.shape): self.game_over=True
    def collides(self,pr,pc,shape):
        for r,c in shape:
            rr,cc=pr+r,pc+c
            if cc<0 or cc>=self.cols or rr>=self.rows: return True
            if rr>=0 and self.board[rr][cc] is not None: return True
        return False
    def move(self,dr,dc):
        if self.game_over:return
        if not self.collides(self.pr+dr,self.pc+dc,self.shape): self.pr+=dr; self.pc+=dc; self.draw()
        elif dr==1: self.lock_piece()
    def rotate(self):
        if self.game_over:return
        pivot_r,pivot_c=self.shape[1]
        rotated=[(pivot_r+(c-pivot_c),pivot_c-(r-pivot_r)) for r,c in self.shape]
        for kick in (0,-1,1,-2,2):
            if not self.collides(self.pr,self.pc+kick,rotated): self.shape=rotated; self.pc+=kick; break
        self.draw()
    def tick(self,dt):
        if self.parent and not self.game_over:self.move(1,0)
    def drop(self):
        if self.game_over:return
        while not self.collides(self.pr+1,self.pc,self.shape): self.pr+=1
        self.lock_piece()
    def lock_piece(self):
        for r,c in self.shape:
            rr,cc=self.pr+r,self.pc+c
            if 0<=rr<self.rows and 0<=cc<self.cols:self.board[rr][cc]=self.kind
        kept=[row for row in self.board if any(v is None for v in row)]
        cleared=self.rows-len(kept)
        if cleared:
            self.lines+=cleared; self.score += [0,100,300,500,800][min(cleared,4)]
        self.board=[[None]*self.cols for _ in range(cleared)]+kept
        self.new_piece(); self.draw()
    def restart(self):
        self.board=[[None]*self.cols for _ in range(self.rows)]; self.score=0; self.lines=0; self.game_over=False; self.new_piece(); self.draw()
    def draw(self,*_):
        self.canvas.clear()
        cw=self.width/self.cols if self.cols else 1; ch=self.height/self.rows if self.rows else 1
        with self.canvas:
            Color(0.025,0.04,0.07,1); Rectangle(pos=self.pos,size=self.size)
            for r in range(self.rows):
                for c in range(self.cols):
                    val=self.board[r][c]
                    if val is not None:
                        Color(*self.COLORS[val]); Rectangle(pos=(self.x+c*cw+dp(1),self.y+(self.rows-1-r)*ch+dp(1)),size=(max(1,cw-dp(2)),max(1,ch-dp(2))))
            if not self.game_over:
                Color(*self.COLORS[self.kind])
                for r,c in self.shape:
                    rr,cc=self.pr+r,self.pc+c
                    if 0<=rr<self.rows and 0<=cc<self.cols: Rectangle(pos=(self.x+cc*cw+dp(1),self.y+(self.rows-1-rr)*ch+dp(1)),size=(max(1,cw-dp(2)),max(1,ch-dp(2))))
            Color(0.3,0.4,0.5,1); Line(rectangle=(self.x,self.y,self.width,self.height),width=1)
    def stop(self):
        if self.event:self.event.cancel(); self.event=None


class TetrisScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root=self.make_page('Tetris')
        self.stats=make_label('Score: 0  |  Lines: 0',15,30); root.add_widget(self.stats)
        self.board=TetrisBoard(size_hint_y=1); root.add_widget(self.board)
        row=GridLayout(cols=5,spacing=dp(4),size_hint_y=None,height=dp(48))
        for txt,fn in [('Left',lambda:self.board.move(0,-1)),('Rotate',self.board.rotate),('Right',lambda:self.board.move(0,1)),('Down',lambda:self.board.move(1,0)),('Drop',self.board.drop)]: row.add_widget(make_button(txt,fn,46))
        root.add_widget(row); self.status=make_label('Complete horizontal rows to score points.',13,28); root.add_widget(self.status)
        root.add_widget(make_button('Restart',self.restart,42)); self.add_home(root)
        self._stats_event=Clock.schedule_interval(self.update_stats,0.2)
    def update_stats(self,_dt):
        if hasattr(self,'board'):
            self.stats.text=f'Score: {self.board.score}  |  Lines: {self.board.lines}'
            if self.board.game_over:self.status.text='Game over. Tap Restart to play again.'
    def restart(self):
        if getattr(self,'_stats_event',None): self._stats_event.cancel()
        self.on_pre_enter()
    def on_leave(self,*_):
        if getattr(self,'_stats_event',None): self._stats_event.cancel(); self._stats_event=None
        if getattr(self,'board',None): self.board.stop()


class FroggerBoard(Widget):
    def __init__(self,**kwargs):
        super().__init__(**kwargs); self.rows=8; self.cols=7; self.player=[7,3]; self.score=0; self.dead=False
        self.cars=[(1,0),(2,4),(4,2),(5,5)]; self.car_dirs=[1,-1,1,-1]; self.bind(pos=self.draw,size=self.draw)
        self.event=Clock.schedule_interval(self.tick,0.45); self.draw()
    def move(self,dr,dc):
        if self.dead:return
        self.player[0]=max(0,min(self.rows-1,self.player[0]+dr)); self.player[1]=max(0,min(self.cols-1,self.player[1]+dc))
        if self.player[0]==0:self.score+=1; self.player=[7,3]
        self.check_hit(); self.draw()
    def tick(self,dt):
        if not self.parent or self.dead:return
        for i,(r,c) in enumerate(self.cars): self.cars[i]=(r,(c+self.car_dirs[i])%self.cols)
        self.check_hit(); self.draw()
    def check_hit(self):
        if any((self.player[0],self.player[1])==(r,c) for r,c in self.cars): self.dead=True
    def restart(self):
        self.player=[7,3]; self.score=0; self.dead=False; self.cars=[(1,0),(2,4),(4,2),(5,5)]; self.draw()
    def draw(self,*_):
        self.canvas.clear(); cw=self.width/self.cols; ch=self.height/self.rows
        with self.canvas:
            Color(0.06,0.28,0.18,1); Rectangle(pos=self.pos,size=self.size)
            for r in range(self.rows):
                if r in (1,2,4,5): Color(0.16,0.18,0.22,1)
                elif r in (3,): Color(0.1,0.3,0.55,1)
                else: Color(0.12,0.42,0.2,1)
                Rectangle(pos=(self.x,self.y+r*ch),size=(self.width,ch))
                if r in (1,2,4,5):
                    Color(0.32,0.34,0.37,1)
                    for c in range(self.cols): Line(points=[self.x+c*cw,self.y+r*ch,self.x+(c+1)*cw,self.y+r*ch],width=1)
            Color(0.95,0.3,0.18,1)
            for r,c in self.cars: Rectangle(pos=(self.x+c*cw+dp(2),self.y+(self.rows-1-r)*ch+dp(3)),size=(cw-dp(4),ch-dp(6)))
            pr,pc=self.player; Color(0.3,0.95,0.45,1); Ellipse(pos=(self.x+pc*cw+cw*0.15,self.y+(self.rows-1-pr)*ch+ch*0.12),size=(cw*0.7,ch*0.76))
            Color(0.8,0.9,0.95,1); Line(rectangle=(self.x,self.y,self.width,self.height),width=1)
    def stop(self):
        if self.event:self.event.cancel(); self.event=None


class FroggerScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root=self.make_page('Frogger')
        root.add_widget(make_label('Cross the lanes and reach the top. Avoid the moving cars.',14,35))
        self.board=FroggerBoard(size_hint_y=1); root.add_widget(self.board)
        self.score_label=make_label('Crossings: 0',17,30); root.add_widget(self.score_label)
        controls=GridLayout(cols=3,spacing=dp(4),size_hint_y=None,height=dp(96))
        controls.add_widget(Widget()); controls.add_widget(make_button('Up',lambda:self.step(-1,0),44)); controls.add_widget(Widget())
        controls.add_widget(make_button('Left',lambda:self.step(0,-1),44)); controls.add_widget(make_button('Down',lambda:self.step(1,0),44)); controls.add_widget(make_button('Right',lambda:self.step(0,1),44))
        root.add_widget(controls); root.add_widget(make_button('Restart',self.restart,40)); self.add_home(root)
        self._frog_event=Clock.schedule_interval(self.update_score,0.2)
    def step(self,dr,dc): self.board.move(dr,dc); self.update_score(0)
    def update_score(self,_dt):
        if hasattr(self,'board'): self.score_label.text=f'Crossings: {self.board.score}' + ('  |  Hit by traffic! Restart.' if self.board.dead else '')
    def restart(self):
        if getattr(self,'_frog_event',None): self._frog_event.cancel()
        self.on_pre_enter()
    def on_leave(self,*_):
        if getattr(self,'_frog_event',None): self._frog_event.cancel(); self._frog_event=None
        if getattr(self,'board',None): self.board.stop()


class PixelCanvas(Widget):
    pass


class PainterScreen(BaseScreen):
    COLORS=[('Black',(0.05,0.05,0.05,1)),('White',(1,1,1,1)),('Red',(0.9,0.2,0.2,1)),('Green',(0.2,0.8,0.35,1)),('Blue',(0.2,0.4,0.95,1)),('Yellow',(1,0.85,0.15,1))]
    def on_pre_enter(self, *_):
        root=self.make_page('Painter 16 x 16'); self.pixels=[[0 for _ in range(16)] for _ in range(16)]; self.color=0
        self.grid=GridLayout(cols=16,spacing=dp(1),padding=dp(1),size_hint_y=None,height=dp(256))
        self.cells=[]
        for r in range(16):
            row=[]
            for c in range(16):
                b=Button(text='',background_normal='',background_color=self.COLORS[0][1],padding=0)
                b.bind(on_release=lambda inst,rr=r,cc=c:self.paint(rr,cc)); self.grid.add_widget(b); row.append(b)
            self.cells.append(row)
        root.add_widget(self.grid)
        palette=GridLayout(cols=3,spacing=dp(4),size_hint_y=None,height=dp(105))
        for i,(name,_) in enumerate(self.COLORS): palette.add_widget(make_button(name,lambda n=i:self.set_color(n),48))
        root.add_widget(palette); root.add_widget(make_button('Clear canvas',self.clear)); root.add_widget(make_button('Save picture',self.save)); self.status=make_label('',14,26); root.add_widget(self.status); self.add_home(root)
    def set_color(self,n): self.color=n
    def paint(self,r,c): self.pixels[r][c]=self.color; self.cells[r][c].background_color=self.COLORS[self.color][1]
    def clear(self):
        self.pixels=[[0 for _ in range(16)] for _ in range(16)]
        for row in self.cells:
            for b in row: b.background_color=self.COLORS[0][1]
    def save(self):
        app=App.get_running_app(); app.saved_pictures.append({'pixels':[r[:] for r in self.pixels],'colors':self.COLORS[:]}); self.status.text='Picture saved in Trinity Files.'


class AnimatorScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root=self.make_page('Animator'); self.frames=[]; self.playing=False
        self.preview=make_label('No frame yet',18,80); root.add_widget(self.preview)
        self.fps_input=make_input('Playback FPS','4'); root.add_widget(self.fps_input)
        root.add_widget(make_button('Add text frame',self.add_frame)); root.add_widget(make_button('Play animation',self.play)); root.add_widget(make_button('Stop',self.stop)); root.add_widget(make_button('Save animation',self.save)); self.status=make_label('Frames: 0',15,30); root.add_widget(self.status); self.add_home(root)
    def add_frame(self): self.frames.append('Frame '+str(len(self.frames)+1)); self.preview.text=self.frames[-1]; self.status.text='Frames: '+str(len(self.frames))
    def play(self):
        if not self.frames: self.add_frame()
        self.stop(); self.playing=True
        try: fps=max(1,min(24,float(self.fps_input.text)))
        except ValueError: fps=4
        self._index=0; self._event=Clock.schedule_interval(self.next_frame,1/fps)
    def next_frame(self,_dt):
        if not self.playing or not self.frames: return False
        self.preview.text=self.frames[self._index%len(self.frames)]; self._index+=1
    def stop(self):
        self.playing=False
        if getattr(self,'_event',None): self._event.cancel(); self._event=None
    def save(self): App.get_running_app().saved_animations.append(list(self.frames)); self.status.text='Animation saved.'


class FilesScreen(BaseScreen):
    def on_pre_enter(self, *_):
        app=App.get_running_app(); root=self.make_page('Trinity Files')
        root.add_widget(make_label(f'Pictures: {len(app.saved_pictures)} | Animations: {len(app.saved_animations)} | Copied texts: {len(app.copied_texts)}',15,40))
        for i,p in enumerate(app.saved_pictures): root.add_widget(make_button('Delete picture '+str(i+1),lambda n=i:self.delete_picture(n),42))
        for i,a in enumerate(app.saved_animations): root.add_widget(make_button('Delete animation '+str(i+1),lambda n=i:self.delete_animation(n),42))
        if app.copied_texts:
            root.add_widget(make_label('Saved text: '+app.copied_texts[-1][:120],13,45))
        add_home_button(root,app)
    def delete_picture(self,n):
        app=App.get_running_app()
        if n<len(app.saved_pictures): app.saved_pictures.pop(n)
        self.on_pre_enter()
    def delete_animation(self,n):
        app=App.get_running_app()
        if n<len(app.saved_animations): app.saved_animations.pop(n)
        self.on_pre_enter()


MORSE={ 'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..','0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.',' ':'/' }

class MorseScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root=self.make_page('Morse Code'); self.source=make_input('English text',height=70,multiline=True); root.add_widget(self.source)
        self.output=make_input('Morse output',height=100,multiline=True); root.add_widget(self.output)
        root.add_widget(make_button('Translate to Morse',self.translate)); root.add_widget(make_button('Save output',self.save)); self.add_home(root)
    def translate(self): self.output.text=' '.join(MORSE.get(ch,'?') for ch in self.source.text.upper())
    def save(self): App.get_running_app().copied_texts.append(self.output.text)

class TranslatorScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root=self.make_page('Morse Translator'); self.source=make_input('Morse, separate letters with spaces and words with /',height=90,multiline=True); root.add_widget(self.source)
        self.output=make_label('',16,100); root.add_widget(self.output); root.add_widget(make_button('Translate to English',self.translate)); self.add_home(root)
    def translate(self):
        reverse={v:k for k,v in MORSE.items()}; words=[]
        for word in self.source.text.strip().split(' / '): words.append(''.join(reverse.get(code,'?') for code in word.split()))
        self.output.text=' '.join(words)

class GospelScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root=self.make_page('Gospel'); root.add_widget(make_label('The Christian Gospel teaches that God loves humanity, that Jesus Christ lived, died, and rose again, and that people are invited to respond with faith, repentance, and love for others. Christians understand and explain these beliefs in different traditions.',17,220)); self.add_home(root)

class DashField(Widget):
    """Deterministic, spaced obstacle generation with a proper jump arc."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player_y = 0.0; self.jump_velocity = 0.0
        self.obstacles = []; self.started = False; self.dead = False
        self.elapsed = 0.0; self.level = 1; self.spawn_clock = 0.0
        self.bind(pos=self.draw, size=self.draw)
        self.event = Clock.schedule_interval(self.tick, 1/60)
        self.draw()
    def start(self):
        self.player_y = 0.0; self.jump_velocity = 0.0; self.obstacles = []
        self.started = True; self.dead = False; self.elapsed = 0.0; self.level = 1
        self.spawn_clock = 1.2; self.draw()
    def jump(self):
        if self.started and not self.dead and self.player_y <= 0.001:
            self.jump_velocity = 1.55
    def tick(self, dt):
        if not self.parent or not self.started or self.dead: return
        dt = min(dt, 0.04)
        self.elapsed += dt
        self.level = min(3, int(self.elapsed // 15) + 1)
        self.jump_velocity -= 3.9 * dt
        self.player_y = max(0.0, self.player_y + self.jump_velocity * dt)
        if self.player_y == 0.0: self.jump_velocity = 0.0
        self.spawn_clock -= dt
        interval = max(1.05, 1.65 - (self.level-1)*0.18)
        if self.spawn_clock <= 0:
            # Level-based patterns, with enough distance to jump between hazards.
            height = random.choice([0.10, 0.13, 0.16]) if self.level == 1 else random.choice([0.12, 0.16, 0.19])
            self.obstacles.append([1.03, height, random.choice([0.045, 0.05])])
            self.spawn_clock = interval * random.uniform(0.92, 1.12)
        speed = 0.58 + (self.level-1)*0.09
        for ob in self.obstacles: ob[0] -= speed * dt
        self.obstacles = [ob for ob in self.obstacles if ob[0] > -0.12]
        player_left, player_right = 0.18, 0.25
        player_height = 0.07
        for x, h, width in self.obstacles:
            overlaps_x = x < player_right and x+width > player_left
            if overlaps_x and self.player_y < h and self.player_y+player_height > 0:
                self.dead = True; break
        if self.elapsed >= 45 and not self.dead:
            self.started = False; self.elapsed = 45
        self.draw()
    def draw(self, *_):
        self.canvas.clear()
        with self.canvas:
            Color(0.035,0.05,0.12,1); Rectangle(pos=self.pos,size=self.size)
            Color(0.18,0.75,0.85,1); Line(points=[self.x,self.y+self.height*0.16,self.right,self.y+self.height*0.16],width=1.5)
            px=self.x+self.width*0.18; py=self.y+self.height*(0.16+self.player_y)
            Color(0.25,0.9,0.45,1); Rectangle(pos=(px,py),size=(self.width*0.07,self.height*0.07))
            Color(0.95,0.28,0.28,1)
            for x,h,w in self.obstacles:
                Rectangle(pos=(self.x+x*self.width,self.y+self.height*0.16),size=(self.width*w,self.height*h))
            Color(0.25,0.72,0.92,1); Line(rectangle=(self.x,self.y,self.width,self.height),width=1)
    def stop(self):
        if self.event: self.event.cancel(); self.event=None


class GeometryScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root=self.make_page('Geometry Dash'); root.add_widget(make_label('Jump over red obstacles. Survive 45 seconds to clear all 3 levels.',13,36))
        self.field=DashField(size_hint_y=1); root.add_widget(self.field)
        self.info=make_label('Tap Start, then Jump.',15,30); root.add_widget(self.info)
        row=BoxLayout(size_hint_y=None,height=dp(48),spacing=dp(5)); row.add_widget(make_button('Jump',self.jump,46)); row.add_widget(make_button('Start / Restart',self.start,46)); root.add_widget(row); self.add_home(root)
        self._dash_event=Clock.schedule_interval(self.status,0.2)
    def start(self): self.field.start(); self.info.text='Level 1 | Go!'
    def jump(self): self.field.jump()
    def status(self,_dt):
        if hasattr(self,'field'):
            f=self.field
            if f.dead:self.info.text=f'Crash on Level {f.level}. Restart to try again.'
            elif not f.started and f.elapsed>=45:self.info.text='All 3 levels cleared!'
            elif f.started:self.info.text=f'Level {f.level} | Time: {int(f.elapsed)} / 45 s'
    def on_leave(self,*_):
        if getattr(self,'_dash_event',None): self._dash_event.cancel(); self._dash_event=None
        if getattr(self,'field',None): self.field.stop()


class RacingField(Widget):
    def __init__(self,**kwargs):
        super().__init__(**kwargs); self.lane=1; self.distance=0; self.traffic=[]; self.speed=0.48; self.crashed=False; self.started=True; self.bind(pos=self.draw,size=self.draw); self.event=Clock.schedule_interval(self.tick,1/60); self.draw()
    def move(self,d):
        if not self.crashed:self.lane=max(0,min(2,self.lane+d)); self.draw()
    def accelerate(self):
        if not self.crashed:self.speed=min(1.0,self.speed+0.08)
    def tick(self,dt):
        if not self.parent or self.crashed:return
        self.distance+=self.speed*dt*10
        if random.random()<0.018:self.traffic.append([random.randrange(3),1.1])
        for car in self.traffic: car[1]-=self.speed*dt*0.65
        self.traffic=[c for c in self.traffic if c[1]>-0.15]
        if any(lane==self.lane and 0.08<y<0.22 for lane,y in self.traffic):self.crashed=True
        self.draw()
    def restart(self):self.lane=1;self.distance=0;self.traffic=[];self.speed=0.48;self.crashed=False;self.draw()
    def draw(self,*_):
        self.canvas.clear()
        with self.canvas:
            Color(0.08,0.32,0.16,1); Rectangle(pos=self.pos,size=self.size)
            road_x=self.x+self.width*0.12; road_w=self.width*0.76
            Color(0.17,0.18,0.2,1); Rectangle(pos=(road_x,self.y),size=(road_w,self.height))
            Color(0.9,0.9,0.78,1)
            for i in (1,2):
                xx=road_x+road_w*i/3
                for j in range(8): Rectangle(pos=(xx-dp(1),self.y+j*self.height/8),size=(dp(2),self.height/16))
            cw=road_w/3; car_w=cw*0.55; car_h=self.height*0.12
            Color(0.9,0.25,0.18,1)
            for lane,y in self.traffic: Rectangle(pos=(road_x+lane*cw+cw*0.22,self.y+y*self.height),size=(car_w,car_h))
            Color(0.2,0.75,0.98,1); Rectangle(pos=(road_x+self.lane*cw+cw*0.22,self.y+self.height*0.12),size=(car_w,car_h))
            Color(0.8,0.9,0.95,1); Line(rectangle=(self.x,self.y,self.width,self.height),width=1)
    def stop(self):
        if self.event:self.event.cancel(); self.event=None

class RacingScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root=self.make_page('Racing'); root.add_widget(make_label('Change lanes to avoid traffic. Accelerate to build distance.',13,34))
        self.field=RacingField(size_hint_y=1); root.add_widget(self.field)
        self.info=make_label('Distance: 0 m',16,30); root.add_widget(self.info)
        row=BoxLayout(spacing=dp(5),size_hint_y=None,height=dp(48))
        row.add_widget(make_button('Left',lambda:self.field.move(-1),45)); row.add_widget(make_button('Accelerate',self.field.accelerate,45)); row.add_widget(make_button('Right',lambda:self.field.move(1),45)); root.add_widget(row)
        root.add_widget(make_button('Restart race',self.restart,40)); self.add_home(root); self._race_event=Clock.schedule_interval(self.update_info,0.2)
    def update_info(self,_dt):
        if hasattr(self,'field'):
            f=self.field; self.info.text=f'Distance: {int(f.distance)} m | Speed: {int(f.speed*100)}%' + (' | CRASH! Restart race.' if f.crashed else '')
    def restart(self):
        if getattr(self,'_race_event',None): self._race_event.cancel()
        self.on_pre_enter()
    def on_leave(self,*_):
        if getattr(self,'_race_event',None): self._race_event.cancel(); self._race_event=None
        if getattr(self,'field',None): self.field.stop()


class CPUScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root = self.make_page('8-bit CPU')
        root.add_widget(make_label('Accumulator is decimal 0-9. ADD/SUB wrap around at 0 and 9.', 13, 40))
        root.add_widget(make_label('Commands: LDA n, ADD n, SUB n, OUT, CLR, MOV A n, HLT', 12, 38))
        self.code = make_input('One instruction per line', 'LDA 5\nADD 3\nOUT\nHLT', height=145, multiline=True); root.add_widget(self.code)
        self.acc_label = make_label('Accumulator: 0', 24, 42); root.add_widget(self.acc_label)
        self.output = make_label('Output: (none)', 15, 60); root.add_widget(self.output)
        root.add_widget(make_button('Run program', self.run_program)); self.add_home(root)
    def run_program(self):
        acc = 0; regs = {'A': 0, 'B': 0}; lines = [x.strip().upper() for x in self.code.text.splitlines() if x.strip()]
        pc = 0; steps = 0; log = []; outputs = []
        while 0 <= pc < len(lines) and steps < 200:
            parts = lines[pc].replace(',', ' ').split(); op = parts[0]; steps += 1
            try:
                if op == 'LDA' and len(parts) == 2: acc = int(parts[1]) % 10
                elif op == 'ADD' and len(parts) == 2: acc = (acc + int(parts[1])) % 10
                elif op == 'SUB' and len(parts) == 2: acc = (acc - int(parts[1])) % 10
                elif op == 'CLR' and len(parts) == 1: acc = 0
                elif op == 'OUT' and len(parts) == 1: outputs.append(str(acc))
                elif op == 'MOV' and len(parts) == 3 and parts[1] in regs: regs[parts[1]] = int(parts[2]) % 256
                elif op == 'ADD' and len(parts) == 3 and parts[1] in regs: regs[parts[1]] = (regs[parts[1]] + int(parts[2])) % 256
                elif op == 'JMP' and len(parts) == 2: pc = int(parts[1]); continue
                elif op == 'JNZ' and len(parts) == 2 and acc != 0: pc = int(parts[1]); continue
                elif op == 'HLT': break
                else: log.append('Unknown or invalid instruction: ' + lines[pc])
            except (ValueError, IndexError) as exc:
                log.append('Instruction error on line ' + str(pc+1) + ': ' + str(exc)); break
            pc += 1
        if steps >= 200: log.append('Stopped after 200 steps to prevent an endless loop.')
        self.acc_label.text = 'Accumulator: ' + str(acc)
        self.output.text = 'Output: ' + (', '.join(outputs) if outputs else '(none)') + '\nSteps: ' + str(steps) + ('\n' + '\n'.join(log) if log else '')


class MyAppScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root=self.make_page('My App'); root.add_widget(make_label('Your app workspace. This is a safe placeholder where you can build your own features.',16,80)); self.user_text=make_input('Write an idea or note',height=80,multiline=True); root.add_widget(self.user_text)
        root.add_widget(make_button('Save note',self.save)); self.status=make_label('',14,28); root.add_widget(self.status); self.add_home(root)
    def save(self): App.get_running_app().copied_texts.append(self.user_text.text); self.status.text='Saved in Trinity Files.'

# Safe arithmetic parser for the calculator. It never evaluates arbitrary Python code.
_ALLOWED_BINOPS={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.FloorDiv:operator.floordiv,ast.Mod:operator.mod,ast.Pow:operator.pow}
_ALLOWED_UNARY={ast.UAdd:operator.pos,ast.USub:operator.neg}
def safe_calculate(expression):
    tree=ast.parse(expression,mode='eval')
    def visit(node):
        if isinstance(node,ast.Expression): return visit(node.body)
        if isinstance(node,ast.Constant) and isinstance(node.value,(int,float)): return node.value
        if isinstance(node,ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
            left,right=visit(node.left),visit(node.right)
            if isinstance(node.op,ast.Pow) and abs(right)>10: raise ValueError('Exponent limit is 10')
            result=_ALLOWED_BINOPS[type(node.op)](left,right)
            if not math.isfinite(result) or abs(result)>1e100: raise ValueError('Result is too large')
            return result
        if isinstance(node,ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY: return _ALLOWED_UNARY[type(node.op)](visit(node.operand))
        raise ValueError('Use numbers and + - * / // % ** only')
    return visit(tree)

class CalculatorScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root=self.make_page('Calculator'); self.expression=make_input('Example: (12 + 5) * 3'); root.add_widget(self.expression)
        self.result=make_label('Result appears here',18,45); root.add_widget(self.result)
        keys=GridLayout(cols=4,spacing=dp(5),size_hint_y=None,height=dp(205))
        for key in ['7','8','9','/','4','5','6','*','1','2','3','-','0','.','(',')','%','//','+','**']:
            keys.add_widget(make_button(key,lambda k=key:self.insert(k),43))
        root.add_widget(keys); root.add_widget(make_button('Calculate',self.calculate)); root.add_widget(make_button('Clear',self.clear)); self.add_home(root)
    def insert(self,k): self.expression.text+=k
    def calculate(self):
        try: self.result.text=str(safe_calculate(self.expression.text.strip()))
        except Exception as e: self.result.text='Error: '+str(e)
    def clear(self): self.expression.text=''; self.result.text='Result appears here'

class InternetScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root=self.make_page('Internet'); root.add_widget(make_label('Opens websites in your device browser. This is not an embedded browser.',15,55))
        self.url=make_input('https://example.com', 'https://www.google.com'); root.add_widget(self.url)
        root.add_widget(make_button('Open website',self.open_website)); root.add_widget(make_button('Open search',self.search)); self.status=make_label('',14,40); root.add_widget(self.status); self.add_home(root)
    def open_website(self):
        url=self.url.text.strip()
        if not url.startswith(('https://','http://')): url='https://'+url
        if any(ch.isspace() for ch in url) or '://' not in url: self.status.text='Enter a valid website address.'; return
        try: webbrowser.open(url); self.status.text='Requested browser launch: '+url
        except Exception as e: self.status.text='Could not open browser: '+str(e)
    def search(self):
        query=self.url.text.strip()
        if not query: self.status.text='Type a search query first.'; return
        from urllib.parse import quote
        try: webbrowser.open('https://www.google.com/search?q='+quote(query)); self.status.text='Opened search in external browser.'
        except Exception as e: self.status.text='Could not open browser: '+str(e)

class CrossGPTScreen(BaseScreen):
    def on_pre_enter(self, *_):
        root=self.make_page('crossGPT'); root.add_widget(make_label('crossGPT | Offline helper plus optional online AI',14,40))
        self.chat=make_label('Ask a question below. Online mode needs your own compatible API key.',14,140); root.add_widget(self.chat)
        self.question=make_input('Type your question',height=75,multiline=True); root.add_widget(self.question)
        self.api_url=make_input('API endpoint (optional)','https://api.openai.com/v1/chat/completions'); root.add_widget(self.api_url)
        self.model=make_input('Model name','gpt-4o-mini'); root.add_widget(self.model)
        self.api_key=make_input('API key (not saved)',password=True); root.add_widget(self.api_key)
        root.add_widget(make_button('Ask offline helper',self.ask_offline)); root.add_widget(make_button('Ask online AI',self.ask_online)); self.status=make_label('',13,40); root.add_widget(self.status); self.add_home(root)
    def offline_answer(self, q):
        import re
        original = q.strip()
        s = original.lower().strip()
        if not s:
            return 'Type a question and I will try to help.'

        # Small built-in Cebuano (Bisaya) phrasebook. This is deliberately
        # offline and modest: exact phrases are more reliable than pretending
        # a tiny dictionary can translate every sentence perfectly.
        ceb_to_en = {
            'hello': 'Hello.', 'maayong buntag': 'Good morning.',
            'maayong hapon': 'Good afternoon.', 'maayong gabii': 'Good evening / good night.',
            'kumusta': 'How are you?', 'kumusta ka': 'How are you?',
            'unsa imong ngalan': 'What is your name?',
            'ako si': 'I am called / I am...', 'ako si droplet': 'I am Droplet.',
            'salamat': 'Thank you.', 'daghang salamat': 'Thank you very much.',
            'walay sapayan': "You're welcome.", 'palihug': 'Please.',
            'pasayloa ko': 'I am sorry / Please forgive me.', 'sorry': 'Sorry.',
            'oo': 'Yes.', 'dili': 'No / not.', 'tingali': 'Maybe / perhaps.',
            'maayo': 'Good / well.', 'maayo ra': 'I am fine / It is okay.',
            'maayo ra ko': 'I am fine.', 'unsa': 'What?', 'kinsa': 'Who?',
            'asa': 'Where?', 'kanus-a': 'When?', 'ngano': 'Why?', 'unsaon': 'How?',
            'asa ang kasilyas': 'Where is the bathroom?',
            'pila ni': 'How much is this?', 'tabangi ko': 'Help me.',
            'wala ko kasabot': "I don't understand.",
            'kasabot ko': 'I understand.', 'hinay hinay palihug': 'Slowly, please.',
            'istorya ta': "Let's talk.", 'amping': 'Take care.',
            'gihigugma tika': 'I love you.', 'gigutom ko': 'I am hungry.',
            'giuhaw ko': 'I am thirsty.', 'kapoy ko': 'I am tired.',
            'asa ka padulong': 'Where are you going?',
            'unsa imong gibuhat': 'What are you doing?',
            'nagtuon ko og bisaya': 'I am studying Cebuano / Bisaya.',
            'taga asa ka': 'Where are you from?',
            'taga': 'from / a native of', 'ako': 'I / me', 'ikaw': 'you',
            'siya': 'he / she', 'kami': 'we (not including you)',
            'kita': 'we (including you)', 'sila': 'they', 'kamo': 'you (plural)',
            'kami tanan': 'all of us (not including you)',
            'balay': 'house / home', 'tubig': 'water', 'pagkaon': 'food',
            'eskwelahan': 'school', 'higala': 'friend', 'pamilya': 'family',
            'bata': 'child', 'dako': 'big', 'gamay': 'small', 'init': 'hot',
            'bugnaw': 'cold', 'karon': 'now / today', 'ugma': 'tomorrow',
            'kagahapon': 'yesterday', 'kini': 'this', 'kana': 'that',
            'dinhi': 'here', 'didto': 'there', 'ug': 'and', 'apan': 'but',
            'kay': 'because', 'oo, palihug': 'Yes, please.',
        }
        en_to_ceb = {
            'hello': 'Kumusta!', 'hi': 'Kumusta!', 'good morning': 'Maayong buntag.',
            'good afternoon': 'Maayong hapon.', 'good evening': 'Maayong gabii.',
            'good night': 'Maayong gabii.', 'how are you': 'Kumusta ka?',
            'what is your name': 'Unsa imong ngalan?', 'thank you': 'Salamat.',
            'thank you very much': 'Daghang salamat.', 'you are welcome': 'Walay sapayan.',
            "you're welcome": 'Walay sapayan.', 'please': 'Palihug.',
            'i am sorry': 'Pasayloa ko.', 'sorry': 'Pasayloa ko.',
            'yes': 'Oo.', 'no': 'Dili.', 'maybe': 'Tingali.',
            'i am fine': 'Maayo ra ko.', 'i am okay': 'Maayo ra ko.',
            'what': 'Unsa?', 'who': 'Kinsa?', 'where': 'Asa?', 'when': 'Kanus-a?',
            'why': 'Ngano?', 'how': 'Unsaon?',
            'where is the bathroom': 'Asa ang kasilyas?',
            'how much is this': 'Pila ni?', 'help me': 'Tabangi ko.',
            "i don't understand": 'Wala ko kasabot.', 'i do not understand': 'Wala ko kasabot.',
            'i understand': 'Kasabot ko.', 'slowly please': 'Hinay-hinay palihug.',
            'take care': 'Amping.', "let's talk": 'Istorya ta.',
            'i am hungry': 'Gigutom ko.', 'i am thirsty': 'Giuhaw ko.',
            'i am tired': 'Kapoy ko.', 'where are you going': 'Asa ka padulong?',
            'what are you doing': 'Unsa imong gibuhat?',
            'i am studying cebuano': 'Nagtuon ko og Bisaya.',
            'i am learning cebuano': 'Nagtuon ko og Bisaya.',
            'where are you from': 'Taga asa ka?', 'i': 'Ako', 'you': 'Ikaw',
            'he': 'Siya', 'she': 'Siya', 'we': 'Kita (includes you) / Kami (excludes you)',
            'they': 'Sila', 'house': 'Balay', 'home': 'Balay', 'water': 'Tubig',
            'food': 'Pagkaon', 'school': 'Eskwelahan', 'friend': 'Higala',
            'family': 'Pamilya', 'child': 'Bata', 'big': 'Dako', 'small': 'Gamay',
            'hot': 'Init', 'cold': 'Bugnaw', 'today': 'Karon', 'tomorrow': 'Ugma',
            'yesterday': 'Kagahapon', 'this': 'Kini', 'that': 'Kana', 'here': 'Dinhi',
            'there': 'Didto', 'and': 'Ug', 'but': 'Apan', 'because': 'Kay',
        }
        def clean_phrase(value):
            value = value.lower().strip()
            value = re.sub(r'^[\s:;,\-]+|[\s?!.,;:]+$', '', value)
            value = re.sub(r'\s+', ' ', value)
            return value

        # Recognize common translation command styles, as well as a phrase typed alone.
        text_to_translate = original
        mode = None
        patterns = [
            (r'^(?:translate\s+)?(?:cebuano|bisaya)\s+to\s+english\s*[:\-]?\s*(.*)$', 'ceb'),
            (r'^(?:translate\s+)?english\s+to\s+(?:cebuano|bisaya)\s*[:\-]?\s*(.*)$', 'en'),
            (r'^translate\s+(?:to\s+english)\s*[:\-]?\s*(.*)$', 'ceb'),
            (r'^translate\s+(?:to\s+(?:cebuano|bisaya))\s*[:\-]?\s*(.*)$', 'en'),
            (r'^(?:ceb|cebuano|bisaya)\s*:\s*(.*)$', 'ceb'),
            (r'^en(?:glish)?\s*:\s*(.*)$', 'en'),
        ]
        for pattern, direction in patterns:
            match = re.match(pattern, original, re.I | re.S)
            if match:
                text_to_translate = match.group(1).strip()
                mode = direction
                break
        normalized = clean_phrase(text_to_translate)
        if mode == 'ceb':
            if normalized in ceb_to_en:
                return 'English: ' + ceb_to_en[normalized]
            words = normalized.split()
            if words and all(word in ceb_to_en for word in words):
                return 'Rough word-by-word English: ' + ' '.join(ceb_to_en[word] for word in words) + '\nNote: word order and context can change the natural translation.'
            return 'I do not know that Cebuano phrase yet. I work offline with a small phrasebook, so try a common phrase such as “kumusta ka” or “salamat”.'
        if mode == 'en':
            if normalized in en_to_ceb:
                return 'Cebuano / Bisaya: ' + en_to_ceb[normalized]
            words = normalized.split()
            if words and all(word in en_to_ceb for word in words):
                return 'Rough word-by-word Cebuano: ' + ' '.join(en_to_ceb[word].rstrip('.') for word in words) + '\nNote: this may not be grammatically natural; Cebuano sentence structure differs from English.'
            return 'I do not know that English phrase in my offline Cebuano phrasebook yet. Try “thank you”, “how are you”, or “where is the bathroom”.'

        # If the user types a known phrase without a translation command, translate it.
        if clean_phrase(original) in ceb_to_en:
            return 'Cebuano to English: ' + ceb_to_en[clean_phrase(original)]
        if clean_phrase(original) in en_to_ceb and len(clean_phrase(original).split()) <= 5:
            return 'English to Cebuano: ' + en_to_ceb[clean_phrase(original)]

        if re.search(r'\b(hello|hey|good morning|good afternoon|good evening)\b', s):
            return 'Hello! I am crossGPT, your offline helper. I can help with basic Python, maths, TrinityOS, and a small Cebuano-English phrasebook.'
        if re.search(r'\b(hi|howdy)\b', s):
            return 'Hi! What would you like to figure out today?'
        if any(x in s for x in ['your name', 'who are you', 'what are you']):
            return 'I am crossGPT, the built-in helper in TrinityOS. Offline, I use programmed rules and a small knowledge set, not a full internet-trained AI.'
        if any(x in s for x in ['time', 'date', 'today']) and any(x in s for x in ['what', 'current', 'today', 'time', 'date']):
            return 'Device date and time: ' + datetime.now().strftime('%A, %B %d, %Y, %H:%M:%S')
        if 'thank' in s:
            return 'You are welcome! Ask another question whenever you like.'
        if 'python' in s or 'kivy' in s:
            if any(w in s for w in ['error', 'bug', 'crash', 'not work', 'doesnt work', "doesn't work"]):
                return 'Python/Kivy debugging checklist:\n1. Read the final lines of the traceback.\n2. Find the exception type and line number.\n3. Check spelling, indentation, and variable names on that line.\n4. Fix that error and run again.\n5. If the app crashes before opening, check the first error mentioning your own .py file.'
            if 'loop' in s or 'repeat' in s or 'count' in s:
                return 'A for loop repeats a set number of times:\nfor i in range(5):\n    print(i)\nThis prints 0 through 4. A while loop repeats while its condition is true, so make sure the condition eventually changes.'
            if 'variable' in s or 'score' in s:
                return 'A variable stores a value. Example:\nscore = 0\nscore = score + 1\nprint(score)\nUse == to compare values, and = to assign a value. For an exact answer check, use if answer == target:.'
            if 'function' in s:
                return 'A function is reusable code. Example:\ndef greet(name):\n    return "Hello, " + name\nprint(greet("Alex"))\nUse return to send a result back to the code that called the function.'
            if 'list' in s or 'array' in s:
                return 'A Python list stores several values: scores = [3, 5, 8]. Read the first item with scores[0], add an item with scores.append(10), and use len(scores) to count items.'
            if 'if' in s or 'condition' in s:
                return 'An if statement makes a decision:\nif score == target:\n    print("Correct")\nelse:\n    print("Try again")\nUse == for equality and >= for greater-than-or-equal.'
            return 'Python is the programming language; Kivy is the toolkit for touch-friendly apps. Widgets build the interface, Clock schedules updates, and canvas instructions draw game objects.'
        if 'droplet' in s or 'crossgpt' in s:
            return 'TrinityOS is your Python/Kivy mini operating system. crossGPT now has expanded offline rules and a small Cebuano-English phrasebook. It still cannot match a full online AI or translate every sentence.'
        if re.search(r'\d\s*[+*/%-]\s*-?\d', s):
            expr = re.search(r'(-?\d+(?:\.\d+)?\s*[+*/%-]\s*-?\d+(?:\.\d+)?)', s)
            if expr:
                try:
                    return 'The answer is ' + str(safe_calculate(expr.group(1))) + '.'
                except Exception:
                    return 'I could not calculate that expression. Try a simple expression such as 12 * 8 or 25 / 5.'
        if 'tetris' in s:
            return 'Tetris is a puzzle game where falling shapes are arranged to complete horizontal rows. Completed rows disappear and award points.'
        if 'pong' in s:
            return 'Pong is a two-paddle ball game. Hitting the ball near the paddle centre sends it straighter; hitting near an edge sends it at a sharper angle.'
        if 'geometry dash' in s:
            return 'Geometry Dash is a rhythm platform game. The player jumps over obstacles while moving forward; good level generation needs safe gaps and obstacle timing that matches the game speed.'
        if 'accumulator' in s or 'cpu' in s:
            return 'An accumulator is a CPU register used for arithmetic. In this TrinityOS simulator it stores one decimal digit, 0-9, and arithmetic wraps around. For example, 7 + 5 becomes 2 when the result wraps modulo 10.'
        if 'offline' in s or 'internet' in s:
            return 'Offline mode works without a network and uses only programmed rules and phrasebook entries. Online mode can answer much more broadly, but it needs internet and an API account with available quota.'
        if 'translate' in s or 'cebuano' in s or 'bisaya' in s:
            return 'Try translation commands like:\nCebuano to English: salamat\nEnglish to Cebuano: thank you\nI have a small built-in phrasebook, so uncommon sentences may not be recognized offline.'
        # Broader offline helper topics: compact reference answers, not a full LLM.
        if any(x in s for x in ['what can you do', 'help topics', 'list topics', 'what do you know']):
            return ('Offline topics I can help with:\n'
                    '- Python basics and debugging\n- Simple arithmetic\n- Cebuano/Bisaya phrasebook\n'
                    '- TrinityOS apps and games\n- Study and writing tips\n- Basic science and geography\n'
                    '- Unit conversions and riddles\nTry: "explain gravity", "study tips", "joke", or "convert 5 km to m".')
        if any(x in s for x in ['study tip', 'study tips', 'how to study', 'study better']):
            return ('A simple study routine:\n1. Pick one small goal.\n2. Study for 20-25 minutes.\n'
                    '3. Close your notes and recall the main ideas.\n4. Check what you missed.\n'
                    '5. Review again tomorrow. Short active-recall sessions beat rereading alone.')
        if any(x in s for x in ['write a story', 'creative writing', 'writing tips', 'help me write']):
            return ('Writing starter: decide who the main character is, what they want, what blocks them, and what changes at the end. '
                    'For an essay, use a clear claim, evidence or examples, and a conclusion. Tell me the topic and I can offer a simple outline.')
        if any(x in s for x in ['gravity', 'photosynthesis', 'evaporation', 'water cycle', 'atoms', 'electricity']) or 'explain science' in s:
            if 'gravity' in s:
                return 'Gravity is the attraction between objects with mass. Earth pulls objects toward its centre, which is why dropped objects fall. In orbit, gravity is still acting; spacecraft are continually falling around Earth.'
            if 'photosynthesis' in s:
                return 'Photosynthesis is how plants use light energy to turn water and carbon dioxide into sugar, releasing oxygen. Chlorophyll helps capture the light.'
            if 'evaporation' in s or 'water cycle' in s:
                return 'The water cycle moves water around Earth: sunlight causes evaporation, water vapour cools and condenses into clouds, then precipitation returns water to the surface.'
            if 'atoms' in s:
                return 'An atom is a basic unit of matter. It has a nucleus containing protons and usually neutrons, with electrons occupying regions around the nucleus.'
            if 'electricity' in s:
                return 'Electric current is the flow of electric charge. A simple circuit needs a power source, a conducting path, and a component such as a lamp. Never experiment with wall outlets.'
        if any(x in s for x in ['earth', 'planet', 'continents', 'ocean']) and any(x in s for x in ['how many', 'what are', 'tell me', 'earth', 'planet']):
            if 'continent' in s:
                return 'A common school model counts 7 continents: Africa, Antarctica, Asia, Europe, North America, South America, and Oceania/Australia. Some regions use different continent models.'
            if 'ocean' in s:
                return 'There are commonly 5 oceans: Pacific, Atlantic, Indian, Southern, and Arctic.'
            return 'Earth is the third planet from the Sun. It has liquid water on much of its surface and one natural Moon.'
        if 'joke' in s:
            return 'Why did the computer go to the doctor? It had a virus. (The digital kind, not a sneeze!)'
        if 'riddle' in s:
            return 'Riddle: What has keys but cannot open locks?\nAnswer: A piano. Ask for another riddle to see a different one.'
        if 'convert' in s or 'unit conversion' in s:
            conversions = [
                (r'(-?\d+(?:\.\d+)?)\s*km\s*(?:to|in)\s*m\b', 1000, 'm'),
                (r'(-?\d+(?:\.\d+)?)\s*m\s*(?:to|in)\s*cm\b', 100, 'cm'),
                (r'(-?\d+(?:\.\d+)?)\s*cm\s*(?:to|in)\s*m\b', 0.01, 'm'),
                (r'(-?\d+(?:\.\d+)?)\s*kg\s*(?:to|in)\s*g\b', 1000, 'g'),
                (r'(-?\d+(?:\.\d+)?)\s*g\s*(?:to|in)\s*kg\b', 0.001, 'kg'),
                (r'(-?\d+(?:\.\d+)?)\s*hours?\s*(?:to|in)\s*minutes?\b', 60, 'minutes'),
            ]
            for pattern, factor, unit in conversions:
                match = re.search(pattern, s)
                if match:
                    return format(float(match.group(1)) * factor, 'g') + ' ' + unit
            return 'Offline conversions I recognize: km to m, m to cm, cm to m, kg to g, g to kg, and hours to minutes. Example: convert 5 km to m.'
        if 'algorithm' in s:
            return 'An algorithm is a step-by-step method for solving a problem. Example for adding two numbers: get the first number, get the second number, add them, then display the result.'
        if 'password' in s or 'api key' in s:
            return 'Keep passwords and API keys private. Do not paste them into chats, screenshots, or public code. If a key is exposed, revoke it and create a replacement. An API key is also not the same thing as ChatGPT login access.'
        if 'why' in s or 'how' in s or 'what' in s:
            return 'I have more offline answers now, but I am still a rule-based helper. Try Python, Kivy, a simple maths expression, study tips, basic science, unit conversions, TrinityOS games, or Cebuano-English phrases.'
        return 'I do not have a programmed answer for that yet. I can help with basic Python/Kivy, simple arithmetic, TrinityOS games, date/time, and common Cebuano-English phrases.'
    def ask_offline(self): self.chat.text=self.offline_answer(self.question.text); self.status.text='Answered offline.'
    def ask_online(self):
        q=self.question.text.strip(); key=self.api_key.text.strip(); endpoint=self.api_url.text.strip(); model=self.model.text.strip()
        if not q: self.status.text='Enter a question first.'; return
        if not key: self.chat.text=self.offline_answer(q); self.status.text='No API key provided, so offline answer shown.'; return
        if not endpoint.startswith('https://'):
            self.status.text='For safety, use an HTTPS API endpoint.'; return
        payload=json.dumps({'model':model or 'gpt-4o-mini','messages':[{'role':'user','content':q}]}).encode('utf-8')
        self.status.text='Contacting online AI...'
        def success(req,result):
            try: self.chat.text=result['choices'][0]['message']['content']; self.status.text='Online answer received.'
            except Exception: self.status.text='Unexpected API response. Check endpoint and model.'
        def failure(req, result):
            # Show a useful provider error without ever displaying the API key.
            code = getattr(req, 'resp_status', None)
            message = ''
            try:
                if isinstance(result, dict):
                    info = result.get('error', {})
                    if isinstance(info, dict):
                        message = info.get('message', '') or info.get('type', '')
                    elif isinstance(info, str):
                        message = info
                    if not message:
                        message = result.get('message', '')
                elif isinstance(result, bytes):
                    message = result.decode('utf-8', errors='replace')
                elif isinstance(result, str):
                    message = result
            except Exception:
                message = ''
            message = str(message).replace('\n', ' ').strip()
            if not message:
                message = 'No details returned by provider.'
            self.status.text = 'API HTTP ' + str(code or 'unknown') + ': ' + message[:180]
        def error(req,err): self.status.text='Network error: '+str(err)
        try: UrlRequest(endpoint,req_body=payload,req_headers={'Content-Type':'application/json','Authorization':'Bearer '+key},on_success=success,on_failure=failure,on_error=error,timeout=25,method='POST')
        except Exception as e: self.status.text='Could not start request: '+str(e)

class AIGuideScreen(BaseScreen):
    """Offline guide explaining how to use crossGPT responsibly and effectively."""
    def on_pre_enter(self, *_):
        root = self.make_page('AI Guidebook')
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(5), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        sections = [
            ('Welcome to crossGPT', 'crossGPT is the built-in assistant. It has two modes: Offline uses built-in rules and phrasebook entries; Online sends your question to the API provider you configure.'),
            ('How to ask better questions', 'Be specific. Instead of “help with Python,” try “Explain why my Python if statement does not run, in beginner-friendly steps.” Include the goal, what you tried, and the exact error when debugging.'),
            ('Useful prompt patterns', 'Explain: “Explain loops using a tiny example.”\nTeach: “Teach me one Python concept, then quiz me.”\nCompare: “Compare a for loop and a while loop.”\nTranslate: “Cebuano to English: salamat” or “English to Cebuano: thank you.”\nDebug: “What does this error mean?” Never include passwords or API keys.'),
            ('Offline mode', 'Offline mode works without internet or API credits. It recognizes selected topics, calculations, and a small Cebuano/Bisaya phrasebook. It is not a full language model, so it may not understand unfamiliar questions or translate full sentences naturally.'),
            ('Online mode', 'Online mode needs internet, a compatible API endpoint, a permitted model, a valid API key, and available API quota. API billing is separate from a ChatGPT subscription. A 401 often means authentication trouble; a 429 can indicate a rate or quota limit. Do not share your key.'),
            ('Check the answer', 'AI can make mistakes or sound confident while being wrong. Check important facts with reliable sources, run code in a safe test, and ask for the reasoning or an example if something is unclear.'),
            ('Privacy and safety', 'Do not enter private information, passwords, API keys, exact home addresses, or other people’s secrets. Ask a trusted adult for help before making purchases or changing account billing settings.'),
            ('What this AI can do today', 'The offline helper can answer some Python/Kivy questions, explain selected TrinityOS games, calculate simple arithmetic, give study and writing tips, explain a few science topics, handle some unit conversions, and translate entries in its phrasebook. It cannot browse the web or learn new facts automatically while offline.'),
        ]
        for heading, body in sections:
            content.add_widget(make_label(heading, 19, 32, halign='left'))
            content.add_widget(make_label(body, 15, max(82, 23 * (len(body) // 42 + body.count('\n') + 2)), halign='left'))
        content.add_widget(make_button('Open crossGPT', lambda: App.get_running_app().open_screen('crossgpt'), 48))
        content.add_widget(make_button('Home', App.get_running_app().go_home, 44))
        scroll.add_widget(content)
        root.add_widget(scroll)


class GoalField(Widget):
    """Simple drawn goal, goalkeeper and animated football for penalty shots."""
    def __init__(self,**kwargs):
        super().__init__(**kwargs); self.keeper_x=0.5; self.ball_x=0.5; self.ball_y=0.13; self.animating=False
        self.target_x=0.5; self.target_y=0.82; self.bind(pos=self.draw,size=self.draw); self.draw()
    def shoot(self,direction,keeper_direction,scored):
        self.keeper_x={'Left':0.25,'Center':0.5,'Right':0.75}[keeper_direction]
        self.ball_x={'Left':0.25,'Center':0.5,'Right':0.75}[direction]
        self.ball_y=0.82 if scored else 0.53; self.draw()
    def reset(self): self.keeper_x=0.5; self.ball_x=0.5; self.ball_y=0.13; self.draw()
    def draw(self,*_):
        self.canvas.clear()
        with self.canvas:
            Color(0.06,0.28,0.15,1); Rectangle(pos=self.pos,size=self.size)
            # Penalty area and goal
            Color(0.78,0.9,0.82,1); Line(points=[self.x+self.width*.08,self.y+self.height*.08,self.x+self.width*.92,self.y+self.height*.08],width=1)
            gx=self.x+self.width*.2; gy=self.y+self.height*.48; gw=self.width*.6; gh=self.height*.42
            Color(0.92,0.95,0.94,1); Line(rectangle=(gx,gy,gw,gh),width=2)
            Color(0.48,0.62,0.62,1)
            for i in range(1,7): Line(points=[gx+gw*i/7,gy,gx+gw*i/7,gy+gh],width=0.6)
            for i in range(1,4): Line(points=[gx,gy+gh*i/4,gx+gw,gy+gh*i/4],width=0.6)
            # Keeper
            kx=self.x+self.width*self.keeper_x; ky=self.y+self.height*.59
            Color(0.98,0.65,0.16,1); Ellipse(pos=(kx-self.width*.035,ky+self.height*.045),size=(self.width*.07,self.height*.09))
            Color(0.98,0.65,0.16,1); Line(points=[kx,ky+self.height*.045,kx,ky-self.height*.06],width=dp(5))
            Line(points=[kx-self.width*.08,ky-self.height*.005,kx+self.width*.08,ky-self.height*.005],width=dp(4))
            Line(points=[kx,ky-self.height*.06,kx-self.width*.055,ky-self.height*.12],width=dp(4)); Line(points=[kx,ky-self.height*.06,kx+self.width*.055,ky-self.height*.12],width=dp(4))
            # Ball
            Color(1,1,1,1); d=min(self.width,self.height)*.07
            Ellipse(pos=(self.x+self.width*self.ball_x-d/2,self.y+self.height*self.ball_y-d/2),size=(d,d))
            Color(0.05,0.05,0.05,1); Line(circle=(self.x+self.width*self.ball_x,self.y+self.height*self.ball_y,d*.22),width=1)

class FootballScreen(BaseScreen):
    DIFFICULTIES={'Easy':0.20,'Normal':0.38,'Hard':0.55}
    def on_pre_enter(self, *_):
        root=self.make_page('Football Penalty Shootout'); self.difficulty='Normal'; self.goals=0; self.shots=0
        self.info=make_label('Choose difficulty, then take 5 shots.',14,38); root.add_widget(self.info)
        self.field=GoalField(size_hint_y=1); root.add_widget(self.field)
        row=BoxLayout(spacing=dp(5),size_hint_y=None,height=dp(43))
        for d in self.DIFFICULTIES: row.add_widget(make_button(d,lambda level=d:self.set_difficulty(level),41))
        root.add_widget(row)
        row=BoxLayout(spacing=dp(5),size_hint_y=None,height=dp(48))
        for direction in ['Left','Center','Right']: row.add_widget(make_button(direction,lambda d=direction:self.shoot(d),45))
        root.add_widget(row); self.score_label=make_label('Goals: 0 / 0',17,32); root.add_widget(self.score_label)
        root.add_widget(make_button('Restart match',self.restart,40)); self.add_home(root)
    def set_difficulty(self,level): self.difficulty=level; self.info.text='Difficulty: '+level+'. Take your shot.'
    def shoot(self,direction):
        if self.shots>=5: self.info.text=f'Full time! Final score: {self.goals}/5. Restart to play again.'; return
        self.shots+=1
        if random.random()<self.DIFFICULTIES[self.difficulty]: keeper=direction
        else: keeper=random.choice([d for d in ['Left','Center','Right'] if d!=direction])
        scored=keeper!=direction
        self.field.shoot(direction,keeper,scored)
        if scored: self.goals+=1; self.info.text=f'GOAL! You shot {direction.lower()}.'
        else: self.info.text=f'Saved! The keeper guessed {direction.lower()}.'
        self.score_label.text=f'Goals: {self.goals} / {self.shots}'
        if self.shots==5: self.info.text+=f' Final score: {self.goals}/5.'
    def restart(self):
        self.goals=0; self.shots=0; self.field.reset(); self.score_label.text='Goals: 0 / 0'; self.info.text='New match. Difficulty: '+self.difficulty+'.'

class TrinityOS(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pin=None; self.military_time=True; self.show_seconds=True; self.sound_enabled=False
        self.saved_animations=[]; self.saved_pictures=[]; self.copied_texts=[]
        self.sm=None

    def build(self):
        Window.clearcolor=BG
        self.sm=ScreenManager(transition=FadeTransition(duration=0.15))
        screens=[('startup',StartupScreen),('lock',LockScreen),('home',HomeScreen),('apps',AppsScreen),('settings',SettingsScreen),('about',AboutScreen),('math',MathScreen),('pong',PongScreen),('tps',TPSScreen),('tetris',TetrisScreen),('frogger',FroggerScreen),('painter',PainterScreen),('animator',AnimatorScreen),('files',FilesScreen),('morse',MorseScreen),('translator',TranslatorScreen),('gospel',GospelScreen),('geometry',GeometryScreen),('racing',RacingScreen),('cpu',CPUScreen),('myapp',MyAppScreen),('calculator',CalculatorScreen),('internet',InternetScreen),('crossgpt',CrossGPTScreen),('aiguide',AIGuideScreen),('football',FootballScreen)]
        for name,cls in screens: self.sm.add_widget(cls(name=name))
        self.sm.current='startup'
        return self.sm

    def open_screen(self,name):
        if self.sm and name in self.sm.screen_names: self.sm.current=name
    def go_home(self): self.open_screen('home')
    def lock_device(self): self.open_screen('lock')
    def get_time(self):
        fmt='%H:%M:%S' if self.military_time and self.show_seconds else '%H:%M' if self.military_time else '%I:%M:%S %p' if self.show_seconds else '%I:%M %p'
        return datetime.now().strftime(fmt).lstrip('0')
    def get_date(self): return datetime.now().strftime('%A, %B %d, %Y')

if __name__ == '__main__':
    TrinityOS().run()
