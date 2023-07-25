import ctypes
import sys
import numpy as np
from OpenGL import GL
import OpenGL.GL.shaders as shaders
from PyQt6 import QtOpenGLWidgets, QtWidgets
from camera import perspective, look_at


VERTEX_SHADER = """
#version 330
uniform mat4 MVP;
in vec3 position;
in vec3 vertexColour;
out vec3 outColour;

void main(){
  outColour = vertexColour;
  gl_Position = MVP * vec4(position, 1.0); 
}
"""


FRAGMENT_SHADER = """
#version 330

out vec4 colour;
//This should be the same name as output from vertex shader
in vec3 outColour;

void main(){
  colour = vec4(outColour, 0);
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

        # Get a handle for our buffers
        self.vertex_position_id = GL.glGetAttribLocation(self.program_id, "position")
        self.vertex_colour_id = GL.glGetAttribLocation(self.program_id, "vertexColour")
        vertex_buffer_data = np.array([-0.0, 0.1, 0.0, 
                                       -1.0, -1.0, -1.0, 
                                       1.0, -1.0, -1.0, 
                                       0.0, 1.0, -1.0], np.float32)
        colour_buffer_data = np.array([0.0, 0.0, 0.0, 
                                       1.0, 0.0, 0.0, 
                                       1.0, 1.0, 0.0, 
                                       1.0, 0.0, 1.0], np.float32)
        element_buffer_data = np.array([1, 2, 3, 0, 1, 2, 0, 2, 3, 0, 3, 1], np.uint32)
        
        self.vertex_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertex_buffer_data.itemsize * len(vertex_buffer_data),  vertex_buffer_data, GL.GL_STATIC_DRAW)

        self.colour_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.colour_buffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, colour_buffer_data.itemsize * len(colour_buffer_data),  colour_buffer_data, GL.GL_STATIC_DRAW)

        self.element_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.element_buffer)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, element_buffer_data.itemsize * len(element_buffer_data), element_buffer_data, GL.GL_STATIC_DRAW)

        # Projection matrix : 45° Field of View, 4:3 ratio, display range : 0.1 unit <-> 100 units
        projection = perspective(45.0, 4.0 / 3.0, 0.1, 100.0)
	
	    # Camera matrix
        view = look_at([4, 3, 3], # Camera is at (4,3,3), in World Space
					   [0, 0, 0], # and looks at the origin
					   [0, 1, 0]  # Head is up (set to 0, -1, 0 to look upside-down)
					  )
	    # Model matrix : an identity matrix (model will be at the origin)
        model = np.identity(4)

	    # Model-View-Projection (MVP) matrix: multiplication of our 3 matrices
        self.MVP = projection @ view @ model

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
        # Use our shader
        GL.glUseProgram(self.program_id)

        # Send our transformation to the currently bound shader in the "MVP" uniform
        mvp_loc = GL.glGetUniformLocation(self.program_id, "MVP")
        GL.glUniformMatrix4fv(mvp_loc, 1, GL.GL_FALSE, self.MVP.transpose())

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
        
        # 2nd attribute buffer : colour
        GL.glEnableVertexAttribArray(self.vertex_colour_id)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.colour_buffer)
        GL.glVertexAttribPointer(self.vertex_colour_id, 3, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0))
                             
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.element_buffer)
        GL.glDrawElements(GL.GL_TRIANGLES, 12, GL.GL_UNSIGNED_INT, ctypes.c_void_p(0))
        GL.glDisableVertexAttribArray(self.vertex_position_id)
        GL.glDisableVertexAttribArray(self.vertex_colour_id)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(500, 500)
        self.setWindowTitle('Transformation')

        self.glWidget = GLWidget(self)
        self.setCentralWidget(self.glWidget)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
