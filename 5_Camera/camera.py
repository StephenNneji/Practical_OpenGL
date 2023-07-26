"""
Class and functions for scene camera
"""
import math
import numpy as np

eps = 1e-6


def look_at(position, target, up_dir=None):
    """Computes the view matrix so that camera is looking at a target
    from a desired position and orientation.

    :param position: position of camera
    :type position: np.ndarray
    :param target: point to look at
    :type target: np.ndarray
    :param up_dir: up direction of camera
    :type up_dir: Union[np.ndarray, None]
    :return: 4 x 4 view matrix
    :rtype: np.ndarray
    """
    position = np.array(position)
    target = np.array(target)
    view = np.identity(4, np.float32)

    if np.all(position == target):
        view = np.identity(4, np.float32)
        view[:3, 3] = -position
        return view

    up = up_dir

    forward = position - target
    forward =  forward /np.linalg.norm(forward)

    if up is None:
        if math.fabs(forward[0]) < eps and math.fabs(forward[2]) < eps:
            up = np.array([0, 0, -1]) if forward[1] > 0 else np.array([0, 0, 1])
        else:
            up = np.array([0, 1, 0])

    left = np.cross(up, forward)
    left = left / np.linalg.norm(left)

    up = np.cross(forward, left)

    view[0, :3] = left
    view[1, :3] = up
    view[2, :3] = forward

    trans = np.zeros(3)
    trans[0] = left[0] * -position[0] + left[1] * -position[1] + left[2] * -position[2]
    trans[1] = up[0] * -position[0] + up[1] * -position[1] + up[2] * -position[2]
    trans[2] = forward[0] * -position[0] + forward[1] * -position[1] + forward[2] * -position[2]
    view[:3, 3] = trans

    return view

 
def perspective(fov, aspect, z_near, z_far):
    """Computes the one-point perspective projection matrix of camera
    
    :param aspect: ratio of the x and y dimension ie x / y
    :type aspect: float
    :param fov: field of view for y dimension in degrees
    :type fov: float
    :param z_near: the distance from the viewer to the near clipping plane (always positive)
    :type z_near: float
    :param z_far: the distance from the viewer to the far clipping plane (always positive).
    :type z_far: float
    :return: 4 x 4 perspective projection matrix
    :rtype: np.ndarray
    """
    projection = np.zeros((4, 4), np.float32)

    y_max = z_near * math.tan(0.5 * math.radians(fov))
    x_max = y_max * aspect

    z_depth = z_far - z_near

    projection[0, 0] = z_near / x_max
    projection[1, 1] = z_near / y_max
    projection[2, 2] = (-z_near - z_far) / z_depth
    projection[3, 2] = -1
    projection[2, 3] = -2 * z_near * z_far / z_depth

    return projection


def orthographic(fov, aspect, z_near, z_far):
    """Computes the orthographic projection matrix of camera. The camera fov is used to calculate the 
    ortho dimensions but typically you can specify the size directly see https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/glOrtho.xml

    :param aspect: ratio of the x and y dimension ie x / y
    :type aspect: float
    :param fov: field of view for y dimension in degrees
    :type fov: float
    :param z_near: the distance from the viewer to the near clipping plane (always positive)
    :type z_near: float
    :param z_far: the distance from the viewer to the far clipping plane (always positive).
    :type z_far: float
    :return: 4 x 4 orthographic projection matrix
    :rtype: np.ndarray
    """
    projection = np.zeros((4, 4), np.float32)

    y_max = z_near * math.tan(0.5 * math.radians(fov))
    x_max = y_max * aspect

    z_depth = z_far - z_near

    projection[0, 0] = 1 / x_max
    projection[1, 1] = 1 / y_max
    projection[2, 2] = -2 / z_depth
    projection[2, 3] = (-z_far - z_near) / z_depth
    projection[3, 3] = 1

    return projection
