import time

from pico2d import *


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
BOY_GROUND_Y = 90
SPRITE_SIZE = 100
NORMAL_SPEED = 300.0
ANIMATION_FPS = 12.0


class BoyState:
    name = None

    def __init__(self, boy):
        self.boy = boy

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self, delta_time):
        pass

    def handle_key_down(self, key):
        pass

    def handle_key_up(self, key):
        pass


class IdleState(BoyState):
    name = 'IDLE'

    def handle_key_down(self, key):
        if key in (SDLK_LEFT, SDLK_RIGHT):
            self.boy.set_direction(-1 if key == SDLK_LEFT else 1)
            self.boy.keys_held.add(key)
            self.boy.machine.change('RUN')


class RunState(BoyState):
    name = 'RUN'

    def update(self, delta_time):
        self.boy.x += self.boy.move_direction * NORMAL_SPEED * delta_time
        self.boy.keep_inside_canvas(SPRITE_SIZE)

    def handle_key_down(self, key):
        if key in (SDLK_LEFT, SDLK_RIGHT):
            self.boy.keys_held.add(key)
            self.boy.set_direction(-1 if key == SDLK_LEFT else 1)

    def handle_key_up(self, key):
        if key not in (SDLK_LEFT, SDLK_RIGHT):
            return

        self.boy.keys_held.discard(key)
        if self.boy.keys_held:
            direction = -1 if SDLK_LEFT in self.boy.keys_held else 1
            self.boy.set_direction(direction)
        else:
            self.boy.move_direction = 0
            self.boy.machine.change('IDLE')


class BoyStateMachine:
    def __init__(self, boy):
        self.states = {
            'IDLE': IdleState(boy),
            'RUN': RunState(boy),
        }
        self.current = self.states['IDLE']
        self.current.enter()

    @property
    def state(self):
        return self.current.name

    def change(self, state_name):
        if self.current.name == state_name:
            return

        next_state = self.states[state_name]
        self.current.exit()
        self.current = next_state
        self.current.enter()

    def update(self, delta_time):
        self.current.update(delta_time)

    def handle_key_down(self, key):
        self.current.handle_key_down(key)

    def handle_key_up(self, key):
        self.current.handle_key_up(key)


class Boy:
    def __init__(self):
        self.x = CANVAS_WIDTH / 2
        self.y = BOY_GROUND_Y
        self.frame = 0
        self.frame_time = 0.0
        self.face_direction = 1
        self.move_direction = 0
        self.keys_held = set()
        self.image = load_image('animation_sheet.png')
        self.machine = BoyStateMachine(self)

    @property
    def state(self):
        return self.machine.state

    def set_direction(self, direction):
        self.move_direction = direction
        self.face_direction = direction

    def keep_inside_canvas(self, display_size):
        half_width = display_size / 2
        self.x = max(half_width, min(CANVAS_WIDTH - half_width, self.x))

    def update(self, delta_time):
        self.machine.update(delta_time)
        self.frame_time += delta_time
        frame_duration = 1.0 / ANIMATION_FPS
        if self.frame_time >= frame_duration:
            frames_to_advance = int(self.frame_time / frame_duration)
            self.frame = (self.frame + frames_to_advance) % 8
            self.frame_time %= frame_duration

    def handle_key_down(self, key):
        self.machine.handle_key_down(key)

    def handle_key_up(self, key):
        self.machine.handle_key_up(key)

    def draw(self):
        if self.state == 'RUN':
            row = 0 if self.face_direction < 0 else 100
        else:
            row = 200 if self.face_direction < 0 else 300
        self.image.clip_draw(
            self.frame * SPRITE_SIZE,
            row,
            SPRITE_SIZE,
            SPRITE_SIZE,
            self.x,
            self.y,
        )


class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def draw(self):
        self.image.draw(CANVAS_WIDTH / 2, 30)


class Game:
    def __init__(self):
        self.grass = Grass()
        self.boy = Boy()
        self.running = True

    def handle_events(self):
        for event in get_events():
            if event.type == SDL_QUIT:
                self.running = False
            elif event.type == SDL_KEYDOWN:
                if event.key == SDLK_ESCAPE:
                    self.running = False
                else:
                    self.boy.handle_key_down(event.key)
            elif event.type == SDL_KEYUP:
                self.boy.handle_key_up(event.key)

    def update(self, delta_time):
        self.boy.update(delta_time)

    def draw(self):
        clear_canvas()
        self.grass.draw()
        self.boy.draw()
        update_canvas()


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        game = Game()
        previous_time = time.monotonic()
        while game.running:
            game.handle_events()
            current_time = time.monotonic()
            delta_time = min(current_time - previous_time, 0.05)
            previous_time = current_time
            game.update(delta_time)
            game.draw()
            delay(0.01)
    finally:
        close_canvas()


if __name__ == '__main__':
    main()
