import numpy as np
from OpenGL.GL import GLfloat
from Mach.transformations import rotation_matrix

def Identity():
    return np.matrix([      [1., 0., 0., 0.],
                            [0., 1., 0., 0.],
                            [0., 0., 1., 0.],
                            [0., 0., 0., 1.]
                            ])

def PerspectiveMatrix(field_of_view_y, aspect, z_near, z_far):

    fov_radians = np.radians(field_of_view_y)
    f = np.tan(fov_radians / 2)

    a_11 = 1 / (f * aspect)
    a_22 = 1 / f
    a_33 = -(z_near + z_far) / (z_near - z_far)
    a_34 = -2 * z_near * z_far / (z_near - z_far)

    perspective_matrix = np.matrix([
        [a_11, 0, 0, 0],
        [0, a_22, 0, 0],
        [0, 0, a_33, -1],
        [0, 0, a_34, 0]
    ])

    return perspective_matrix

def OrthographicMatrix(left, right, bottom, top, near, far):
    a_00 = 2 / (right - left)
    a_11 = 2 / (top - bottom)
    a_22 = -2 / (far - near)
    a_03 = -(right + left) / (right - left)
    a_13 = -(top + bottom) / (top - bottom)
    a_23 = -(far + near) / (far - near)

    orthographic_matrix = np.matrix([
        [a_00,  0,      0,      a_03],
        [0,     a_11,   0,      a_13],
        [0,     0,      a_22,   a_23],
        [0,     0,      0,      1]
    ])

    return orthographic_matrix

def LookAt(eye, center, up):
    f = Normalize(center-eye)
    s = Normalize(np.cross(up, f))
    u = np.cross(f, s)

    m = Identity()
    m[0, 0] = s[0]
    m[1, 0] = s[1]
    m[2, 0] = s[2]

    m[0, 1] = u[0];
    m[1, 1] = u[1];
    m[2, 1] = u[2];

    m[0, 2] =-f[0];
    m[1, 2] =-f[1];
    m[2, 2] =-f[2];

    m[3, 0] =-np.dot(s, eye);
    m[3, 1] =-np.dot(u, eye);
    m[3, 2] = np.dot(f, eye);
    return m

def TranslationMatrix(x, y, z):
    """
    Generates a translation matrix

    Arguments:
        x - how far to translate in the x axis (float)
        y - how far to translate in the y axis (float)
        z - how far to translate in the z axis (float)
    """
    return np.matrix([  [1., 0., 0., x],
                        [0., 1., 0., y],
                        [0., 0., 1., z],
                        [0., 0., 0., 1.]])

def Normalize(arr):
    return arr / np.linalg.norm(arr)

def Hyp(arr):
    return np.linalg.norm(arr)

def RotationMatrix(theta, x, y, z, point=None):
    """
    Generates a rotation matrix

    Arguments:
        theta - amount (in radians) to rotate (float)
        x - rotation weight in the x direction (float between 0 and 1)
        y - rotation weight in the y direction (float between 0 and 1)
        z - rotation weight in the z direction (float between 0 and 1)
    """
    return rotation_matrix(theta, [x, y, z])

def ScaleMatrix(x, y, z):
    return np.matrix([  [x,       0.,      0.,      0.],
                        [0.,      y,       0.,      0.],
                        [0.,      0.,      z,       0.],
                        [0.,      0.,      0.,      1.]])

def MatFromArray(arr):
    return np.matrix([  [arr[0],  arr[1],  arr[2],  arr[3]],
                        [arr[4],  arr[5],  arr[6],  arr[7]],
                        [arr[8],  arr[9],  arr[10], arr[11]],
                        [arr[12], arr[13], arr[14], arr[15]]
                        ])
