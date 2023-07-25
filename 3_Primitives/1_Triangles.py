import ctypes
import sys
import numpy as np
from OpenGL import GL
import OpenGL.GL.shaders as shaders
from PyQt6 import QtOpenGLWidgets, QtWidgets


VERTEX_SHADER = """
#version 330
in vec2 position;

void main()
{
  gl_Position = vec4(position, 0.0, 1.0);
}
"""


FRAGMENT_SHADER = """
#version 330
out vec4 colour;

void main(){
  colour = vec4(1, 0, 0, 0);
}
"""

class GLWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(parent)

    def initializeGL(self):
        GL.glClearColor(0.0, 0.0, 0.4, 0.0)

        # Create and compile our GLSL program from the shaders
        self.program_id = shaders.compileProgram(shaders.compileShader(VERTEX_SHADER, GL.GL_VERTEX_SHADER),
                                                 shaders.compileShader(FRAGMENT_SHADER, GL.GL_FRAGMENT_SHADER))

        # Get a handle for our buffers
        self.vertex_position_id = GL.glGetAttribLocation(self.program_id, "position")

        g_vertex_buffer_data = np.array([-1.0, -1.0, 1.0, -1.0, 0.0, 1.0], np.float32)
        
        self.vertex_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, g_vertex_buffer_data.itemsize * len(g_vertex_buffer_data),  g_vertex_buffer_data, GL.GL_STATIC_DRAW)
    
    
    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Use our shader
        GL.glUseProgram(self.program_id)

        # 1st attribute buffer : vertices
        GL.glEnableVertexAttribArray(self.vertex_position_id)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer)
        GL.glVertexAttribPointer(self.vertex_position_id, # The attribute we want to configure
                              2,                     # size
                              GL.GL_FLOAT,              # type
                              GL.GL_FALSE,              # normalized?
                              0,                     # stride
                              ctypes.c_void_p(0)     # array buffer offset
                             )
        
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3) 
        GL.glDisableVertexAttribArray(self.vertex_position_id)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(500, 500)
        self.setWindowTitle('Triangles')

        self.glWidget = GLWidget(self)
        self.setCentralWidget(self.glWidget)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
