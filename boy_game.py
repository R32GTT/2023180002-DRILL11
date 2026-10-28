from pico2d import *
from transitions import Machine
import math
import random
import time


# Game object class here

class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def draw(self):
        self.image.draw(400, 30)

    def update(self):
        pass


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.idle_since = time.monotonic()
        self.face_dir = 1
        self.run_direction = 0
        self.keys_held = set()
        self.image = load_image('animation_sheet.png')
        self.machine = Machine(
            model=self,
            states=['IDLE', 'RUN', 'SLEEP'],
            initial='IDLE',
            transitions=[
                {'trigger': 'sleep', 'source': 'IDLE', 'dest': 'SLEEP'},
                {
                    'trigger': 'wake',
                    'source': 'SLEEP',
                    'dest': 'IDLE',
                    'after': 'reset_idle_timer'
                },
                {'trigger': 'start_run', 'source': ['IDLE', 'SLEEP'], 'dest': 'RUN'},
                {
                    'trigger': 'stop_run',
                    'source': 'RUN',
                    'dest': 'IDLE',
                    'after': 'reset_idle_timer'
                },
            ],
            auto_transitions=False
        )

    def update(self):
        self.frame = (self.frame + 1) % 8
        if self.state == 'IDLE':
            if time.monotonic() - self.idle_since >= 5:
                self.sleep()
        elif self.state == 'RUN':
            self.x = max(50, min(750, self.x + self.run_direction * 5))

    def handle_keydown(self, key):
        if key in (SDLK_LEFT, SDLK_RIGHT):
            self.keys_held.add(key)
            self.run_direction = -1 if key == SDLK_LEFT else 1
            self.face_dir = self.run_direction
            if self.state != 'RUN':
                self.start_run()
        elif self.state == 'SLEEP':
            if key == SDLK_SPACE:
                self.wake()
        elif self.state == 'IDLE':
            self.idle_since = time.monotonic()

    def handle_keyup(self, key):
        if key not in (SDLK_LEFT, SDLK_RIGHT):
            return

        self.keys_held.discard(key)
        if self.keys_held:
            self.run_direction = -1 if SDLK_LEFT in self.keys_held else 1
            self.face_dir = self.run_direction
        elif self.state == 'RUN':
            self.run_direction = 0
            self.stop_run()

    def reset_idle_timer(self):
        self.idle_since = time.monotonic()

    def draw(self):
        idle_row = 300 if self.face_dir == 1 else 200
        if self.state == 'SLEEP':
            # Lower sprite to keep its rotated body against the grass.
            self.image.clip_composite_draw(
                self.frame * 100, idle_row, 100, 100,
                math.pi / 2, '', self.x, self.y - 40, 100, 100
            )
        elif self.state == 'RUN':
            run_row = 100 if self.run_direction == 1 else 0
            self.image.clip_draw(self.frame * 100, run_row, 100, 100, self.x, self.y)
        else:
            self.image.clip_draw(self.frame * 100, idle_row, 100, 100, self.x, self.y)


def handle_events():
    global running

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                running = False
            else:
                boy.handle_keydown(event.key)
        elif event.type == SDL_KEYUP:
            boy.handle_keyup(event.key)


def reset_world():
    global world
    global boy

    world = []

    grass = Grass()
    world.append(grass)

    boy = Boy()
    world.append(boy)



def update_world():
    for o in world:
        o.update()
    pass


def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()


running = True

open_canvas()
reset_world()
# game loop
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)
# finalization code
close_canvas()
