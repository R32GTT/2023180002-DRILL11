import time

from pico2d import *


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
BOY_GROUND_Y = 90
SPRITE_SIZE = 100
AUTORUN_DISPLAY_SIZE = 150
NORMAL_SPEED = 300.0
AUTORUN_SPEED = 600.0
AUTORUN_DURATION = 5.0
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
        if key == SDLK_a:
            self.boy.machine.change('AUTORUN')
        elif key in (SDLK_LEFT, SDLK_RIGHT):
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


class AutoRunState(BoyState):
    name = 'AUTORUN'

    def __init__(self, boy):
        super().__init__(boy)
        self.elapsed = 0.0

    def enter(self):
        self.elapsed = 0.0
        if self.boy.move_direction == 0:
            self.boy.move_direction = self.boy.face_direction
        self.boy.keep_inside_canvas(AUTORUN_DISPLAY_SIZE)

    def update(self, delta_time):
        self.elapsed += delta_time
        if self.elapsed >= AUTORUN_DURATION:
            self.boy.move_direction = 0
            self.boy.machine.change('IDLE')
            return

        self.boy.move_and_bounce(AUTORUN_SPEED, AUTORUN_DISPLAY_SIZE, delta_time)

    def handle_key_down(self, key):
        if key not in (SDLK_LEFT, SDLK_RIGHT):
            return

        self.boy.keys_held.add(key)
        self.boy.set_direction(-1 if key == SDLK_LEFT else 1)
        self.boy.machine.change('RUN')


class BoyStateMachine:
    def __init__(self, boy):
        self.states = {
            'IDLE': IdleState(boy),
            'RUN': RunState(boy),
            'AUTORUN': AutoRunState(boy),
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

    def move_and_bounce(self, speed, display_size, delta_time):
        half_width = display_size / 2
        left_edge = half_width
        right_edge = CANVAS_WIDTH - half_width
        next_x = self.x + self.move_direction * speed * delta_time

        if next_x <= left_edge:
            self.x = left_edge
            self.set_direction(1)
        elif next_x >= right_edge:
            self.x = right_edge
            self.set_direction(-1)
        else:
            self.x = next_x

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
        is_running = self.state in ('RUN', 'AUTORUN')
        if is_running:
            row = 0 if self.face_direction < 0 else 100
        else:
            row = 200 if self.face_direction < 0 else 300
        draw_size = AUTORUN_DISPLAY_SIZE if self.state == 'AUTORUN' else SPRITE_SIZE
        self.image.clip_draw(
            self.frame * SPRITE_SIZE,
            row,
            SPRITE_SIZE,
            SPRITE_SIZE,
            self.x,
            self.y,
            draw_size,
            draw_size,
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
