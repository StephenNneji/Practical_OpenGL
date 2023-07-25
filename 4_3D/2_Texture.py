import ctypes
import sys
import numpy as np
from OpenGL import GL
import OpenGL.GL.shaders as shaders
from PIL import Image
from PyQt6 import QtOpenGLWidgets, QtWidgets


VERTEX_SHADER = """
#version 330
in vec3 position;
in vec2 uv;
out vec2 outUV;

void main(){
  outUV = uv;
  gl_Position = vec4(position, 1.0); 
}
"""


FRAGMENT_SHADER = """
#version 330

out vec4 colour;
//This should be the same name as output from vertex shader
in vec2 outUV;
uniform sampler2D bricks;

void main(){
  colour = texture(bricks, outUV);
}
"""

class GLWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(parent)

    def initializeGL(self):
        GL.glClearColor(0.0, 0.0, 0.4, 0.0)
        GL.glEnable(GL.GL_DEPTH_TEST)

        # Create and compile our GLSL program from the shaders
        self.program_id = shaders.compileProgram(shaders.compileShader(VERTEX_SHADER, GL.GL_VERTEX_SHADER),
                                                 shaders.compileShader(FRAGMENT_SHADER, GL.GL_FRAGMENT_SHADER))
               
        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
       
        # Set the texture wrapping parameters
        # GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
        # GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)

        # Set texture filtering parameters
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    
        # load image
        image = Image.open("exercises/4_3D/bricks.jpg")
        img_data = np.array(list(image.getdata()), np.uint8)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGB, image.width, image.height, 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, img_data)
        GL.glBindTexture(GL.GL_TEXTURE_2D, GL.GL_FALSE)


        # Get a handle for our buffers
        self.vertex_position_id = GL.glGetAttribLocation(self.program_id, "position")
        self.vertex_uv_id = GL.glGetAttribLocation(self.program_id, "uv")   
        self.texture_id  = GL.glGetUniformLocation(self.program_id, "bricks")

        vertex_buffer_data = np.array([-1. , -1. ,  1.,
                                       1. , -1. ,  1.,
                                       0. ,  1. ,  1.,
                                       0. ,  0.1,  0.,
                                       -1. , -1. ,  1.,
                                       1. , -1. ,  1.,
                                       -0. ,  0.1,  0.,
                                       1. , -1. ,  1.,
                                       0. ,  1. ,  1.,
                                       0. ,  0.1,  0.,
                                       0. ,  1. ,  1.,
                                       -1. , -1. ,  1.], np.float32)
        
        uv_buffer_data = np.array([0.5, 1.0, 0.0, 0.0, 0.0, 1.0, 
                                   0.0, 0.0, 0.5, 1.0,  0.0, 1.0,
                                   0.0, 0.0, 0.5, 1.0,  0.0, 1.0, 
                                   0.0, 0.0, 0.5, 1.0,  0.0, 1.0], np.float32) 
        element_buffer_data = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], np.uint32)
        
        self.vertex_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertex_buffer_data.itemsize * len(vertex_buffer_data),  vertex_buffer_data, GL.GL_STATIC_DRAW)

        self.uv_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.uv_buffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, uv_buffer_data.itemsize * len(uv_buffer_data),  uv_buffer_data, GL.GL_STATIC_DRAW)

        self.element_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.element_buffer)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, element_buffer_data.itemsize * len(element_buffer_data), element_buffer_data, GL.GL_STATIC_DRAW)
    
    
    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
        # Use our shader
        GL.glUseProgram(self.program_id)

        # Bind our texture in Texture Unit 0
        GL.glActiveTexture(GL.GL_TEXTURE0)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        # Set our texture sampler to user Texture Unit 0
        GL.glUniform1i(self.texture_id, 0)

        # 1st attribute buffer : vertices
        GL.glEnableVertexAttribArray(self.vertex_position_id)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer)
        GL.glVertexAttribPointer(self.vertex_position_id, # The attribute we want to configure
                                 3,                     # size
                                 GL.GL_FLOAT,              # type
                                 GL.GL_FALSE,              # normalized?
                                 0,                     # stride
                                 ctypes.c_void_p(0)     # array buffer offset
                                )
        
        # 2nd attribute buffer : uvs
        GL.glEnableVertexAttribArray(self.vertex_uv_id)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.uv_buffer)
        GL.glVertexAttribPointer(self.vertex_uv_id, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0))
                             
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.element_buffer)
        GL.glDrawElements(GL.GL_TRIANGLES, 12, GL.GL_UNSIGNED_INT, ctypes.c_void_p(0))
        GL.glDisableVertexAttribArray(self.vertex_position_id)
        GL.glDisableVertexAttribArray(self.vertex_uv_id)
        GL.glBindTexture(GL.GL_TEXTURE_2D, GL.GL_FALSE)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(500, 500)
        self.setWindowTitle('Texture')

        self.glWidget = GLWidget(self)
        self.setCentralWidget(self.glWidget)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
