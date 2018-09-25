from Mega.MegaObject import *

class Scene(MegaObject):
    def __init__(self, sprites, hitBoxes, hurtBoxes):
        super().__init__(resource_path('Backgrounds/Backgrounds.png'), sprites, hitBoxes, hurtBoxes)

        self.animations = {
        'default' : Animation({
        },
            [0],
            None
        )
        }
