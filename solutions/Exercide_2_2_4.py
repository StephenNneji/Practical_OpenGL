import sys
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

#SOLUTION
FRAGMENT_SHADER = """
#version 330
out vec4 fragColour;
uniform int index;
uniform vec2 resolution;

void main() {
    if (gl_FragCoord.x > resolution.x/2) {
        fragColour = vec4(0.0, 1.0, 0.0, 1.0);
    }
    else {
        fragColour = vec4(1.0, 0.0, 0.0, 1.0);
    }
}
"""

class GLWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(parent)
        
        self.index = 0

    def initializeGL(self):
        GL.glClearColor(0.0, 0.0, 0.0, 0.0)

        # Create and compile our GLSL program from the shaders
        self.program_id = shaders.compileProgram(shaders.compileShader(VERTEX_SHADER, GL.GL_VERTEX_SHADER),
                                                 shaders.compileShader(FRAGMENT_SHADER, GL.GL_FRAGMENT_SHADER))
    
    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glUseProgram(self.program_id)

        resolution_loc = GL.glGetUniformLocation(self.program_id, "resolution")
        GL.glUniform2f(resolution_loc, self.width(), self.height())

        switch_loc = GL.glGetUniformLocation(self.program_id, "index")
        GL.glUniform1i(switch_loc, self.index)

        GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 4)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(500, 500)
        self.setWindowTitle('Shader with Uniform variable [Press the A key]')

        self.glWidget = GLWidget(self)
        self.setCentralWidget(self.glWidget)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_A:
            self.glWidget.index = (self.glWidget.index + 1) % 3
            self.glWidget.update()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
