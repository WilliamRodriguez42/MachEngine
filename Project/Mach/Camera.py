from Mach.Matrix import *

class OrthoScreenCamera:
    def __init__(self, width, height, aspect, near_clip, far_clip, zoom = 1):
        """
        Creates an orthographic matrix used for rendering to the screen
        Takes in the width and height of the screen in pixels
        as well as the desired aspect ratio in width / heigth
        the near_clip and far_clip express the desired clipping ranges of the matrix
        and the zoom allows the user to multiply the upper and lower ranges of the x and y axis by a scalar

        the +y is limited to zoom
        the -y is limited to -zoom
        the +x is limited to zoom * aspect
        the -x is limited to -zoom * aspect
        """
        self.near_clip = near_clip
        self.far_clip = far_clip
        self.zoom = zoom
        self.aspect = aspect
        self.width = width
        self.height = height
        self.resize(width, height)

    def updateObjects(self, matrix_name, objects):
        """
        Takes in a list of MachObjects or Shaders and will fill out a uniform with the name matrix_name with our OrthographicMatrix
        """
        for o in objects:
            o.storeMatrix4(matrix_name, self.mat)

    def resize(self, width = 0, height = 0, zoom = 0):
        """
        Resizes our matrix to fit a new screen width and height, or will zoom the screen
        """
        if width > 0: self.width = width
        if height > 0: self.height = height
        if zoom > 0: self.zoom = zoom

        if width > self.aspect * height:
            aspect = 1 / (height * self.zoom)
        else:
            aspect = self.aspect / (width * self.zoom)
        self.mat = OrthographicMatrix(-width * aspect, width * aspect, -height * aspect, height * aspect, self.near_clip, self.far_clip)

class Camera:
    """
    X axis is to the right of the screen
    Y axis is to the top of the screen
    Z axis is out of the screen
    """

    limit = np.pi / 2.1
    def __init__(self, aspect, FOV=60, z_near=0.1, z_far=100):
        self.look = np.array([0., 0, -1])
        self.pos = np.array([0., 0, -10])
        self.up = np.array([0., 1, 0])

        self.rx = 0 # Local rotation in x axis, must be clamped between -pi / 4 to pi / 4

        self.FOV = FOV
        self.z_near = z_near
        self.z_far = z_far

        self.recalc()
        self.perspectiveMatrix = PerspectiveMatrix(FOV, aspect, z_near, z_far)

    def getLocalAxis(self):
        " Gets the local axis in global space coordinates"
        z = Normalize(self.look)
        x = Normalize(np.cross(z, Normalize(self.up)))
        y = Normalize(np.cross(z, x))
        return (x, y, z)

    def getChangeOfBasis(self):
        " Gets the change of basis matrix to map global space to local space"
        return np.matrix(self.getLocalAxis())

    def setPos(self, x, y, z):
        " Set the world position of the camera"
        delta = self.look - self.pos
        self.pos = np.array([x, y, z])

        self.recalc()

    def movePos(self, x, y, z):
        " Move the position of the camera"
        delta = np.array([x, y, z])
        self.pos += delta

        self.recalc()

    def movePosLocal(self, x, y, z):
        " Move the position of the camera in the local axis"
        lx, ly, lz = self.getLocalAxis()

        mx = x * lx
        my = y * ly
        mz = z * lz

        delta = mx + my + mz
        self.pos += delta

        self.recalc()

    def moveRotY(self, r):
        " Moves the camera in the global y axis by r radians"
        rm = RotationMatrix(r, 0, 1, 0)
        self.look = rm.dot(np.append(self.look, 1).reshape(4, 1)).T[0, :3]
        self.recalc()

    def moveRotX(self, r):
        " Moves the camera in the local x axis by r radians"

        self.rx += r
        if self.rx > self.limit:
            self.rx = self.limit
        elif self.rx < -self.limit:
            self.rx = -self.limit

        globalX, _, globalZ = self.getLocalAxis()

        rm = RotationMatrix(self.rx, *globalX)

        self.look[1] = 0
        self.look = Normalize(self.look)
        self.look = rm.dot(np.append(self.look, 1).reshape(4,1)).T[0, :3]
        self.recalc()

    def lookAt(self, x, y, z):
        " Makes the camera look at a certain point in global space"
        self.look = Normalize(self.pos - np.array([x, y, z]))
        self.recalc()

    def recalc(self):
        self.modelViewMatrix = LookAt(self.pos, self.pos - self.look, self.up)

    def getModelViewMatrix(self):
        " Returns the 4x4 model view matrix"
        return self.modelViewMatrix

    def getPerspectiveMatrix(self):
        " Returns the 4x4 perspective matrix"
        return self.perspectiveMatrix

    def getOrthographicMatrix(self):
        " Returns the 4x4 orthographic matrix"
        return self.orthographicMatrix

    def resizeAspect(self, width, height):
        self.aspect = width / height
        self.perspectiveMatrix = PerspectiveMatrix(self.FOV, self.aspect, self.z_near, self.z_far)
