import xml.etree.ElementTree as ET
from Mega.MegaObject import MegaObject
from Mach.Shader import Shader
from Mach.Mach import resource_path
from Mach.Attribute import Attribute
import numpy as np

collision_shader = None
box = None

def init():
    global collision_shader, box

    collision_shader = Shader(
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

    box = collision_shader.createNewMachObject()
    attributes = [
        Attribute(boxvertices, 0, size = 3, dtype=np.float32)
    ]
    box.storeAttributeArray(attributes)
    box.storeFloat('box', 0, 0, 1, 1)
    box.bind()
    collision_shader.bind()

class MultCollisions:
    def __init__(self, collision_boxes):
        self.collision_boxes = collision_boxes

    def scale(self, scaleX, scaleY):
        col = []
        for c in self.collision_boxes:
            col.append(c.scale(scaleX, scaleY))
        return MultCollisions(col)

    def translate(self, x, y):
        col = []
        for c in self.collision_boxes:
            col.append(c.translate(x, y))
        return MultCollisions(col)

    def draw(self):
        for c in self.collision_boxes:
            box.storeFloat('box', *c.getRenderTuple())
            box.storeFloat('color', *c.getColor())
            box.bind()
            box.draw()

    def overlapse(self, other):
        for o in other.collision_boxes:
            for c in self.collision_boxes:
                if o.overlapse(c):
                    return True

        return False

class CollisionBox:
    def __init__(self, nx, ny, cx, cy, fx, fy, color = [1, 1, 0]):
        self.nx = nx
        self.ny = ny
        self.cx = cx
        self.cy = cy
        self.fx = fx
        self.fy = fy
        self.color = [color[0], color[1], color[2], 0.5]

    def scale(self, scaleX, scaleY):
        nx = self.nx * scaleX
        ny = self.ny * scaleY
        cx = self.cx * scaleX
        cy = self.cy * scaleY
        fx = self.fx * scaleX
        fy = self.fy * scaleY
        return CollisionBox(nx, ny, cx, cy, fx, fy, self.color)

    def translate(self, x, y):
        nx = self.nx + x
        ny = self.ny + y
        cx = self.cx + x
        cy = self.cy + y
        fx = self.fx + x
        fy = self.fy + y
        return CollisionBox(nx, ny, cx, cy, fx, fy, self.color)

    def getRenderTuple(self):
        return (self.nx, self.ny, self.fx, self.fy)

    def getColor(self):
        return self.color;

    def overlapse(self, other):
        hw = abs(self.cx - self.nx)
        hh = abs(self.cy - self.ny)
        ohw = abs(other.cx - other.nx)
        ohh = abs(other.cy - other.ny)

        mdx = hw + ohw
        mdy = hh + ohh

        dx = abs(self.cx - other.cx)
        dy = abs(self.cy - other.cy)

        return dx <= mdx and dy <= mdy

def Decode(filename, pixels_in_height):
    tree = ET.parse(filename)
    root = tree.getroot()

    boxes = {}

    for child in root:
        child_name = child.tag[1:]
        width = int(child.attrib['pw'])
        height = int(child.attrib['ph'])

        #boxes[child_name] = []
        for box in child:
            fx = float(box.attrib['fx'])
            fy = float(box.attrib['fy'])
            nx = float(box.attrib['nx'])
            ny = float(box.attrib['ny'])
            cx = float(box.attrib['cx'])
            cy = float(box.attrib['cy'])
            r = float(box.attrib['r'])
            g = float(box.attrib['g'])
            b = float(box.attrib['b'])

            rgb = [r, g, b]

            pheight = height / pixels_in_height
            pwidth = width / height * pheight

            box = CollisionBox(nx, ny, cx, cy, fx, fy, rgb).scale(pwidth, pheight)
            if child_name not in boxes:
                boxes[int(child_name)] = MultCollisions([box])
            #boxes[child_name].append(box)


    return boxes
