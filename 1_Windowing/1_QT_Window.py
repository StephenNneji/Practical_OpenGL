import sys
from OpenGL import GL
from PyQt6 import QtOpenGLWidgets, QtWidgets


class GLWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(parent)

    def initializeGL(self):
        GL.glClearColor(0.0, 0.0, 1.0, 0.0)
    
    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    def resizeGL(self, width, height):
        print(f"The size of the GL Widget is ({width}, {height})")

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(500, 500)
        self.setWindowTitle('Windowing')

        self.glWidget = GLWidget(self)
        self.setCentralWidget(self.glWidget)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
