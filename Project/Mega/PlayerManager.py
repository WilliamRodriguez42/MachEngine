from Mega.MegaObject import *

class PlayerManager(MegaObject):
    def __init__(self, sprites, hitBoxes, hurtBoxes):
        super().__init__(resource_path('Wolf/Wolf.png'), sprites, hitBoxes, hurtBoxes)

        self.animations = {
            'idle' : Animation({
                'left' : 'walk left',
                'right' : 'walk right',
                'down' : 'crouch',
                'space' : 'jump',
                'shift left' : 'run left',
                'shift right' : 'run right',
                'a' : 'standing punch',
                'b' : 'standing kick'
            },
                [2],
                None
            ),

            'walk right' : Animation({
                'idle' : 'idle',
                'left' : 'walk left',
                'down' : 'crouch',
                'space' : 'jump',
                'shift left' : 'run left',
                'shift right' : 'run right',
                'a' : 'standing punch',
                'b' : 'standing kick'
            },
                list(range(0, 3)),
                False
            ),

            'walk up' : Animation({
                'idle' : 'idle',
                'left' : 'walk left',
                'down' : 'crouch',
                'space' : 'jump',
                'shift left' : 'run left',
                'shift right' : 'run right',
                'a' : 'standing punch',
                'b' : 'standing kick'
            },
                list(range(7, 11)),
                False
            ),

            'walk down' : Animation({
                'idle' : 'idle',
                'left' : 'walk left',
                'down' : 'crouch',
                'space' : 'jump',
                'shift left' : 'run left',
                'shift right' : 'run right',
                'a' : 'standing punch',
                'b' : 'standing kick'
            },
                list(range(3, 7)),
                False
            ),

            'walk left' : Animation({
                'idle' : 'idle',
                'right' : 'walk right',
                'down' : 'crouch',
                'space' : 'jump',
                'shift left' : 'run left',
                'shift right' : 'run right',
                'a' : 'standing punch',
                'b' : 'standing kick'
            },
                list(range(0, 3)),
                True
            ),

            'run left' : Animation({
                'idle' : 'idle',
                'left' : 'walk left',
                'right' : 'walk right',
                'shift right' : 'run right',
                'space' : 'jump',
                'down' : 'crouch',
                'a' : 'running punch left',
                'b' : 'running kick left'
            },
                [15],
                True
            ),

            'run right' : Animation({
                'idle' : 'idle',
                'left' : 'walk left',
                'right' : 'walk right',
                'shift left' : 'run left',
                'space' : 'jump',
                'down' : 'crouch',
                'a' : 'running punch right',
                'b' : 'running kick right'
            },
                [15],
                False
            ),

            'standing damage left' : Animation({
            },
                [65, 65, 65],
                None,
                after = 'idle'
            ),

            'standing damage right' : Animation({
            },
                [65, 65, 65],
                None,
                after = 'idle'
            )
        }

        for name, anim in self.animations.items():
            if name not in ['jump', 'rising', 'falling', 'rising punch', 'rising kick', 'falling punch', 'falling kick', 'land', 'KO']:
                anim.allowed['hit left'] = 'standing damage left'
                anim.allowed['hit right'] = 'standing damage right'
            elif name != 'KO':
                anim.allowed['hit left'] = 'falling damage left'
                anim.allowed['hit right'] = 'falling damage right'
            anim.allowed['KO'] = 'KO'

        self.setCurrentAnimation('idle')

        self.velocityx = 0

        self.speed = 0.05
        self.runMult = 3

        self.fallSpeed = 0.03

        self.bounds = 16/9
        self.floor = -0.5

        self.posx = self.floor
        self.posy = self.floor

        self.health = 100

    def update(self):
        super().update()

        if self.currentAnimName == 'walk left':
            self.velocityx = -self.speed
        elif self.currentAnimName == 'walk right':
            self.velocityx = self.speed
        elif self.currentAnimName == 'run left':
            self.velocityx = -self.speed * self.runMult
        elif self.currentAnimName == 'run right':
            self.velocityx = self.speed * self.runMult
        elif self.currentAnimName == 'jump':
            self.posy += self.fallSpeed
        elif self.currentAnimName == 'rising':
            self.posy += self.fallSpeed / 3
        elif self.currentAnimName == 'falling':
            self.posy -= self.fallSpeed / 3
        elif self.currentAnimName == 'land':
            self.posy -= self.fallSpeed
            if self.posy <= self.floor:
                self.posy = self.floor
                self.currentAnimName = 'idle'
                self.currentAnimation = self.animations[self.currentAnimName]
                self.frameCounter = 0
        elif self.currentAnimName == 'falling damage left':
            self.posy -= self.fallSpeed / 4
            if self.posy <= self.floor:
                self.posy = self.floor
                self.currentAnimName = 'deded'
                self.currentAnimation = self.animations[self.currentAnimName]
                self.frameCounter = 0
            self.velocityx = -self.speed
        elif self.currentAnimName == 'falling damage right':
            self.posy -= self.fallSpeed / 4
            if self.posy <= self.floor:
                self.posy = self.floor
                self.currentAnimName = 'deded'
                self.currentAnimation = self.animations[self.currentAnimName]
                self.frameCounter = 0
            self.velocityx = self.speed
        elif self.currentAnimName == 'standing punch':
            if self.flipped:
                self.velocityx = -0.03
            else:
                self.velocityx = 0.03
        elif self.currentAnimName == 'falling punch':
            if self.posy > ((self.fallSpeed * 4) / 5) + self.floor:
                self.posy -= self.fallSpeed / 5
        elif self.currentAnimName == 'running punch right':
            if self.flipped:
                self.velocityx = -self.speed
            else:
                self.velocityx = self.speed
        elif self.currentAnimName == 'running punch left':
            if self.flipped:
                self.velocityx = -self.speed
            else:
                self.velocityx = self.speed
        elif self.currentAnimName == 'running kick right':
            if self.flipped:
                self.velocityx = -self.speed
            else:
                self.velocityx = self.speed
        elif self.currentAnimName == 'running kick left':
            if self.flipped:
                self.velocityx = -self.speed
            else:
                self.velocityx = self.speed
        elif self.currentAnimName == 'rising punch':
            self.posy += self.fallSpeed / 5
        elif self.currentAnimName == 'falling kick':
            if self.posy > ((self.fallSpeed * 4) / 5) + self.floor:
                self.posy -= self.fallSpeed / 5
        elif self.currentAnimName == 'rising kick':
            self.posy += self.fallSpeed / 5
        elif self.currentAnimName == 'idle':
            self.posy = self.floor
            self.velocityx *= 0.9
        elif self.currentAnimName == 'standing damage left':
            self.posy = self.floor
            self.velocityx = -self.speed
        elif self.currentAnimName == 'standing damage right':
            self.posy = self.floor
            self.velocityx = self.speed
        else:
            self.velocityx *= 0.9
            self.posy = self.floor
        self.posx += self.velocityx

        if self.posx > self.bounds:
            self.posx = self.bounds
        elif self.posx < -self.bounds:
            self.posx = -self.bounds

    def isHit(self, hitBox, damage):
        hurtBox = self.getHurtBox()
        if hurtBox is None:
            return False

        if hitBox is None:
            return False

        if hurtBox.overlapse(hitBox):
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                self.RequestAction('KO')
            return True
        return False
