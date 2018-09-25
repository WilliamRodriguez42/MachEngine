from Mach.Shader import *
from Mach.Attribute import *
from Mach.Matrix import *
from Mach.Mach import resource_path
#import Mach.TextureAtlas as ta

render_shader = None

def init():
    global render_shader, sprites

    render_shader = Shader(
        resource_path('my_vert.glsl'),
        resource_path('my_frag.glsl')
    )
    #render_shader.storeSampler2D('atlas', atlas)
    render_shader.bind()

atlas = None
def set_atlas(at):
    global atlas
    if atlas != at:
        atlas = at
        render_shader.storeSampler2D('atlas', atlas)

class RenderObject:
    def __init__(self, scaleX = 1, scaleY = 1):
        self.scaleX = scaleX
        self.scaleY = scaleY

        vertices = [
            0.5, 0.5, 0,
            -0.5, -0.5, 0,
            -0.5, 0.5, 0,
            0.5, 0.5, 0,
            0.5, -0.5, 0,
            -0.5, -0.5, 0,
        ]

        texCoords = [
            1, 0,
            0, 1,
            0, 0,
            1, 0,
            1, 1,
            0, 1,
        ]

        self.obj = render_shader.createNewMachObject()

        attributes = [
            Attribute(vertices, 0, size = 3, dtype=np.float32),
            Attribute(texCoords, 1, size = 2, dtype=np.float32)
        ]

        self.obj.storeAttributeArray(attributes)

        self.obj.storeMatrix4('texCoordManip', Identity())
        self.obj.storeMatrix4('posRotScale', ScaleMatrix(self.scaleX, self.scaleY, 1))

        self.obj.bind()

    def setSprite(self, sprite):
        texCoordManip = TranslationMatrix(sprite.x, sprite.y, 0) * ScaleMatrix(sprite.w, sprite.h, 1)
        self.obj.storeMatrix4('texCoordManip', texCoordManip)

    def setScale(self, scaleX, scaleY):
        self.scaleX = scaleX
        self.scaleY = scaleY

    def draw(self, x, y, z=0):
        posRotScale = TranslationMatrix(x, y, z) * ScaleMatrix(self.scaleX, self.scaleY, 1)
        self.obj.storeMatrix4('posRotScale', posRotScale)
        self.obj.bind()
        self.obj.draw()
