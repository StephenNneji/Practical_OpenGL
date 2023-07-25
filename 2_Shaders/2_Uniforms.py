import sys
import numpy as np
from OpenGL import GL
import OpenGL.GL.shaders as shaders
from PyQt6 import QtOpenGLWidgets, QtWidgets, QtCore


VERTEX_SHADER = """
#version 330
const vec2 vertices[4] = vec2[4](vec2(-1.0, -1.0), vec2(1.0, -1.0), 
                                 vec2(-1.0, 1.0), vec2(1.0, 1.0));
void main()
{
    gl_Position = vec4(vertices[gl_VertexID], 0.0, 1.0);
}
"""


FRAGMENT_SHADER = """
#version 330
uniform vec3 colour;
out vec4 fragColour;

void main(){
  fragColour = vec4(colour, 1.0);
}
"""

class GLWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(parent)
        
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

    def initializeGL(self):
        GL.glClearColor(0.0, 0.0, 0.0, 0.0)

        # Create and compile our GLSL program from the shaders
        self.program_id = shaders.compileProgram(shaders.compileShader(VERTEX_SHADER, GL.GL_VERTEX_SHADER),
                                                 shaders.compileShader(FRAGMENT_SHADER, GL.GL_FRAGMENT_SHADER))
    
    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glUseProgram(self.program_id)
        
        colourLoc = GL.glGetUniformLocation(self.program_id, "colour")
        GL.glUniform3fv(colourLoc, 1, np.random.rand(3))

        GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 4)
    

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(500, 500)
        self.setWindowTitle('Shader with Uniform variable')

        self.glWidget = GLWidget(self)
        self.setCentralWidget(self.glWidget)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.glWidget.update)
        self.timer.start()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
