from Mega.RenderObject import *

ro = None

def init():
    global ro
    ro = RenderObject()

class Animation:
    def __init__(self, allowed, frames, faceLeft, after = None, damage = 0, extra = None):
        self.allowed = allowed
        self.frames = frames
        self.faceLeft = faceLeft
        self.after = after
        self.damage = damage
        self.extra = extra

class MegaObject:
    def __init__(self, atlas, sprites, hit_boxes, hurt_boxes):
        self.atlas = atlas
        self.hitBoxes = hit_boxes
        self.hurtBoxes = hurt_boxes
        self.sprites = sprites

        self.posx = 0
        self.posy = 0

        self.animations = {
        'default' : Animation({
        },
            [0],
            None
        )
        }

        self.currentAnimName = 'default'
        self.currentAnimation = self.animations[self.currentAnimName]
        self.frameCounter = 0
        self.flipped = False

    def setCurrentAnimation(self, currentAnimName):
        self.currentAnimName = currentAnimName
        self.currentAnimation = self.animations[self.currentAnimName]

    def update(self):
        self.frameCounter += 0.4
        if int(self.frameCounter) >= len(self.currentAnimation.frames):
            if self.currentAnimation.after:
                self.currentAnimName = self.currentAnimation.after
                self.currentAnimation = self.animations[self.currentAnimName]

            self.frameCounter = 0

    def draw(self, scaleX = 1, scaleY = 1):
        set_atlas(self.atlas)

        if self.flipped:
            ro.setScale(-scaleX, scaleY)
        else:
            ro.setScale(scaleX, scaleY)
        ro.setSprite(self.getSprite())
        ro.draw(self.posx, self.posy)

    def pixel_draw(self, pixels_in_height, scaleX = 1, scaleY = 1):
        sx, sy = self.pixel_scale(pixels_in_height)
        scaleX *= sx
        scaleY *= sy

        self.draw(sx, sy)

    def getSprite(self):
        return self.sprites[self.getFrame()]

    def RequestAction(self, request):
        if request in self.currentAnimation.allowed:
            self.currentAnimName = self.currentAnimation.allowed[request]
            self.currentAnimation = self.animations[self.currentAnimName]
            if self.currentAnimation.faceLeft is not None:
                self.flipped = int(self.currentAnimation.faceLeft)

            self.frameCounter = 0

    def getHitBox(self):
        frame = self.getFrame()
        if frame in self.hitBoxes:
            hb = self.hitBoxes[frame]
            if self.flipped:
                hb = hb.scale(-1, 1)
            return (hb.translate(self.posx, self.posy), self.currentAnimation.damage)
        return (None, 0)

    def pixel_scale(self, pixels_in_height):
        sprite = self.getSprite()

        pheight = sprite.ph / pixels_in_height
        pwidth = sprite.pw / sprite.ph * pheight
        return (pwidth, pheight)

    def getHurtBox(self):
        frame = self.getFrame()
        if frame in self.hurtBoxes:
            hb = self.hurtBoxes[frame]
            if self.flipped:
                hb = hb.scale(-1, 1)
            return hb.translate(self.posx, self.posy)
        return None

    def getFrame(self):
        return self.currentAnimation.frames[int(self.frameCounter)]
