from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from random import randint

END_LINE = 45

app = Ursina()

class Person(FrameAnimation3d):
    def __init__(self, position=(0, 0, 0), speed=0.1):
        super().__init__(
            'untitled_',
            fps=60,
            autoplay=False,
            loop=True,
            position=position,
            scale=1,
            texture='white_cube',

            speed=speed
        )

class Tree(Entity):
    def __init__(self, position=(0, 0, 0), scale=1, origin=0, rotation=0):
        super().__init__(
            model='assets/tree',
            position=position,
            scale=scale,
            origin=origin,
            rotation=rotation
        )

class Tagger(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(
            model='assets/robot',
            position=position,
            scale=1,
            origin=0,

            speak_count=0,
            status='idle',
            voice=Audio('assets/sound', autoplay=False)
        )

        invoke(self.start_game, delay=2)

    def start_game(self):
        game_text.text = 'START!'
        invoke(game_text.disable, delay=2)

        self.look_back()

    def speak(self):
        if self.status != 'speak':
            self.status = 'speak'
            self.voice.play()

        self.speak_count += 1

        if self.speak_count > 4:
            self.look_forward()
        else:
            invoke(self.speak, delay=1)

    def look_forward(self):
        self.status = 'forward'
    
        self.animate('rotation_y', 0, duration=.2, curve=curve.linear)

        invoke(self.look_back, delay=3)

    def look_back(self):
        self.status = 'back'

        self.animate('rotation_y', 180, duration=3, curve=curve.linear)

        self.speak_count = 0

        invoke(self.speak, delay=3)


Sky()
ground = Entity(model='cube', scale=(100, 1, 100), collider='box', color=color.gray, texture='white_cube')
line = Entity(model='cube', position=(0, 0.1, END_LINE), scale=(100, 1, 1), color=color.red, texture='white_cube')
PointLight(parent=camera, color=color.white, position=(0, 10, -1.5))
AmbientLight(color=color.rgba(100, 100, 100, 0.1))

game_text = Text(text='START!', scale=4, position=(0, 0.35, 0), origin=0, color=color.black)
debug_text = Text(text='idle', scale=1, position=(0, -0.45, 0), origin=0, color=color.light_gray)

player = FirstPersonController()
tagger = Tagger(position=(0, 0, END_LINE))

for _ in range(20):
    tree = Tree(
        position=(randint(-50, 50), 0.3, randint(-50, 50)),
        scale=randint(20, 45) / 100,
        origin=0,
        rotation=(randint(-5, 5), randint(0, 360), randint(-5, 5))
    )

people = []
# person = Person(position=(0, 0.5, 2), speed=0.01)
# people = [person]
# for _ in range(3):
#     p = duplicate(person)
#     p.position = (randint(-10, 10), 0.5, randint(-3, 1))
#     p.speed = randint(5, 15) / 1000
#     people.append(p)

last_position, last_rotation = None, None

def update():
    global last_position, last_rotation

    debug_text.text = '%s, %s, %s' % (tagger.status, player.position, player.rotation)

    if tagger.status == 'forward':
        if last_position is None and last_rotation is None:
            last_position = player.position
            last_rotation = player.rotation
        elif last_position != player.position or last_rotation != player.rotation:
            game_text.enable()
            game_text.color = color.red
            game_text.text = 'YOU DIED'
            player.disable()

        for p in people:
            p.pause()
    else:
        last_position, last_rotation = None, None

        for p in people:
            p.resume()
            p.position += Vec3(0, 0, p.speed)

    if player.position.z > END_LINE:
        game_text.enable()
        game_text.color = color.azure
        game_text.text = 'YOU WON!'
        # tagger.disable()

app.run()
