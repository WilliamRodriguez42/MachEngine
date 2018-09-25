from Mach.Shader import *
from Mach.Mach import *
from Mach.Rendered import Texture, DepthTexture
from Mach.Camera import Camera
from Mach.UniformBlock import UniformBlock
from Mach.Struct import Struct
from Mach.Matrix import *
from Mach.transformations import clip_matrix
from Mach.Audio import *
from Mach.Camera import *
import Mach.TextureAtlas as ta

import Mega.PlayerManager as pm
import Mega.HitAndHurt as hnh
import Mega.RenderObject as ren
import Mega.MegaObject as mo
from Mega.Scene import Scene

from PyQt5 import Qt, QtGui, QtCore
import numpy as np

import sys

pixels_in_height = 100
aspect_ratio = 16/9

class Game(GlQWindow):
    captureMouse = True
    mouseCaptured = False

    def start(self):
        self.captureMouse = True

        hitBoxes = hnh.Decode(resource_path('Wolf/Hit/Collision.xml'), pixels_in_height)
        hurtBoxes = hnh.Decode(resource_path('Wolf/Hit/Collision.xml'), pixels_in_height)

        self.camera = OrthoScreenCamera(width, height, aspect_ratio, 0.1, 100, 1)

        hnh.init()
        ren.init()
        mo.init()

        wolf_sprites = ta.parse(resource_path('Wolf/Wolf.xml'))
        self.oneManager = pm.PlayerManager(wolf_sprites, hitBoxes, hurtBoxes)
        self.twoManager = pm.PlayerManager(wolf_sprites, hitBoxes, hurtBoxes)

        background_sprites = ta.parse(resource_path('Backgrounds/Backgrounds.xml'))
        self.background = Scene(background_sprites, {}, {})

        self.oneManager.posx = -0.75
        self.twoManager.posx = 0.75
        self.twoManager.flipped = True

        self.boxShader = Shader(
            resource_path('boxvert.glsl'),
            resource_path('boxfrag.glsl')
        )

        boxvertices = [
            1, 1, 0,
            0, 0, 0,
            0, 1, 0,
            1, 1, 0,
            1, 0, 0,
            0, 0, 0,
        ]

        self.oneHealthBar = self.boxShader.createNewMachObject()
        attributes = [
            Attribute(boxvertices, 0, size = 3, dtype=np.float32)
        ]
        self.oneHealthBar.storeAttributeArray(attributes)
        self.oneHealthBar.storeFloat('color', 1, 0, 0, 1)
        self.oneHealthBar.bind()

        self.twoHealthBar = self.boxShader.createNewMachObject()
        self.twoHealthBar.storeAttributeArray(attributes)
        self.twoHealthBar.storeFloat('color', 1, 0, 0, 1)

        self.imageShader = Shader(
            resource_path('imagevert.glsl'),
            resource_path('imagefrag.glsl')
        )

        self.imageShader.bind()

        coords = [
            1, 0,
            0, 1,
            0, 0,
            1, 0,
            1, 1,
            0, 1,
        ]

        attributes = [
            Attribute(boxvertices, 0, size=3, dtype=np.float32),
            Attribute(coords, 1, size=2, dtype=np.float32)
        ]
        self.titleScreen = self.imageShader.createNewMachObject()
        self.titleScreen.storeAttributeArray(attributes)
        self.titleScreen.storeFloat('box', -aspect_ratio, -1, aspect_ratio, 1)
        self.titleScreen.storeSampler2D('image', resource_path('title.png'))
        self.titleScreen.bind()

        self.background = self.imageShader.createNewMachObject()
        self.background.storeAttributeArray(attributes)
        self.background.storeFloat('box', -aspect_ratio, -1, aspect_ratio, 1)
        self.background.storeSampler2D('image', resource_path('background.jpg'))
        self.background.bind()

        self.nextRound = self.imageShader.createNewMachObject()
        self.nextRound.storeAttributeArray(attributes)
        self.nextRound.storeFloat('box', -aspect_ratio, -1, aspect_ratio, 1)
        self.nextRound.storeSampler2D('image', resource_path('Next Round.png'))
        self.nextRound.bind()

        self.title = True
        self.drawHitBoxes = True
        self.waitNextRound = False

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.title:
            self.imageShader.bind()
            self.titleScreen.bind()
            self.titleScreen.draw()
        else:
            self.imageShader.bind()
            self.background.bind()
            self.background.draw()

            self.oneManager.update()
            self.twoManager.update()

            oneBox, oneDamage = self.oneManager.getHitBox()
            twoBox, twoDamage = self.twoManager.getHitBox()

            oneHit = self.oneManager.isHit(twoBox, twoDamage)
            twoHit = self.twoManager.isHit(oneBox, oneDamage)

            if oneHit:
                if self.twoManager.flipped:
                    self.oneManager.RequestAction('hit left')
                else:
                    self.oneManager.RequestAction('hit right')
            if twoHit:
                if self.oneManager.flipped:
                    self.twoManager.RequestAction('hit left')
                else:
                    self.twoManager.RequestAction('hit right')

            ren.render_shader.bind()
            self.oneManager.pixel_draw(pixels_in_height)
            self.twoManager.pixel_draw(pixels_in_height)

            hnh.collision_shader.bind()
            if self.drawHitBoxes:

                if oneBox is not None:
                    oneBox.draw()

                hurtBox = self.oneManager.getHurtBox()
                if hurtBox is not None:
                    hurtBox.draw()

                if twoBox is not None:
                    twoBox.draw()

                hurtBox = self.twoManager.getHurtBox()
                if hurtBox is not None:
                    hurtBox.draw()

            self.oneHealthBar.storeFloat('box', -aspect_ratio, 0.8, -0.7 - (0.7 - self.oneManager.health / 100), 1)
            self.oneHealthBar.bind()
            self.oneHealthBar.draw()

            self.twoHealthBar.storeFloat('box', aspect_ratio, 0.8, 0.7  + (0.7 - self.twoManager.health / 100), 1)
            self.twoHealthBar.bind()
            self.twoHealthBar.draw()

            if self.oneManager.health <= 0 or self.twoManager.health <= 0:
                self.imageShader.bind()
                self.nextRound.bind()
                self.nextRound.draw()
                self.waitNextRound = True


    # Called whenever the window is resized
    def windowResized(self, width, height):
        self.bind()
        self.camera.resize(width, height)
        self.camera.updateObjects('projectionMatrix', [self.boxShader, hnh.collision_shader, self.imageShader, ren.render_shader])
        self.draw()

    # Key handling
    def keyPress(self, key):
        # Release the mouse when escape is hit
        if self.title:
            self.title = False

        if key == QtCore.Qt.Key_Escape:
            self.mouseCaptured = False
            self.setCursor(Qt.Qt.ArrowCursor)
        elif key == QtCore.Qt.Key_J:
            self.oneManager.RequestAction('space')
        elif key == QtCore.Qt.Key_K:
            self.oneManager.RequestAction('a')
        elif key == QtCore.Qt.Key_L:
            self.oneManager.RequestAction('b')

        elif key == 16777227:
            self.twoManager.RequestAction('space')
        elif key == QtCore.Qt.Key_Slash:
            self.twoManager.RequestAction('a')
        elif key == QtCore.Qt.Key_Asterisk:
            self.twoManager.RequestAction('b')

        elif key == 16777274: # F11
            if self.windowState() & QtCore.Qt.WindowFullScreen:
                self.showNormal()
                self.parent().showNormal()
            else:
                self.parent().showFullScreen()
                self.showFullScreen()



        if self.waitNextRound and key == QtCore.Qt.Key_Space:
            self.oneManager.posx = -2
            self.twoManager.posx = 2
            self.twoManager.flipped = True
            self.oneManager.flipped = False

            self.oneManager.setCurrentAnimation('idle')
            self.twoManager.setCurrentAnimation('idle')
            self.oneManager.frameCounter = 0
            self.twoManager.frameCounter = 0

            self.oneManager.velocityx = 0
            self.twoManager.velocityx = 0

            self.oneManager.posy = 0
            self.twoManager.posy = 0

            self.oneManager.health = 100
            self.twoManager.health = 100

            self.waitNextRound = False

    def keyHeldDown(self, keysHeld):
        shift = QtCore.Qt.Key_Shift in keysHeld
        ctrl = QtCore.Qt.Key_Control in keysHeld

        oneRequest = 'idle'
        twoRequest = 'idle'
        for key in keysHeld:
            if key == QtCore.Qt.Key_A:
                if shift:
                    oneRequest = 'shift left'
                else:
                    oneRequest = 'left'
            elif key == QtCore.Qt.Key_D:
                if shift:
                    oneRequest = 'shift right'
                else:
                    oneRequest = 'right'
            elif key == QtCore.Qt.Key_S:
                oneRequest = 'down'


            if key == QtCore.Qt.Key_Left:
                if ctrl:
                    twoRequest = 'shift left'
                else:
                    twoRequest = 'left'
            elif key == QtCore.Qt.Key_Right:
                if ctrl:
                    twoRequest = 'shift right'
                else:
                    twoRequest = 'right'
            elif key == QtCore.Qt.Key_Down:
                twoRequest = 'down'


        self.oneManager.RequestAction(oneRequest)
        self.twoManager.RequestAction(twoRequest)


    def keyRelease(self, key):
        pass

    # Mouse events
    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()

        # Capture the mouse
        if self.captureMouse and not self.mouseCaptured:
            self.setCursor(Qt.Qt.BlankCursor)

            cursor = QtGui.QCursor()
            cursor.setPos(-1, -1)

            geom = self.getGeometry()
            originX = geom.width / 2
            originY = geom.height / 2
            cursor.setPos(geom.x + originX, geom.y + originY)

            self.mouseCaptured = True

    def mouseReleaseEvent(self, event):
        #print(event.button())
        x = event.x()
        y = event.y()

    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()

        if self.mouseCaptured:
            geom = self.getGeometry()

            originX = geom.width / 2
            originY = geom.height / 2

            deltaX = x - originX
            deltaY = y - originY

            cursor = QtGui.QCursor()
            cursor.setPos(geom.x + originX, geom.y + originY)

    # Wheel events
    def wheelEvent(self,event):
        x = event.angleDelta().x()
        y = event.angleDelta().y()

if __name__ == "__main__":
    # create the QT App and window
    width, height = 1066, 600

    app = Qt.QApplication([])
    glQWindow = Game()

    glQWindowWidget = Qt.QWidget.createWindowContainer(glQWindow, None, Qt.Qt.Widget)
    glQWindowWidget.show()
    glQWindowWidget.resize(width, height)
    app.exec_()

    app.close()
