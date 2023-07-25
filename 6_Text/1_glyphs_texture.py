import ctypes
import sys
import numpy as np
from OpenGL import GL
import OpenGL.GL.shaders as shaders
from PyQt6 import QtOpenGLWidgets, QtWidgets, QtGui, QtCore


VERTEX_SHADER = """
#version 330 

in vec3 vertexPos;
in vec2 vertexUV;
uniform vec2 scale; 
uniform vec3 position;
out vec2 outUV; 

void main() 
{ 
    outUV = vertexUV;
    float x = ((position.x + vertexPos.x) * scale.x) - 1.0;
    float y = ((position.y + vertexPos.y) * scale.y) + 1.0;
    gl_Position = vec4(x, y, position.z, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330

in vec2 outUV;
uniform sampler2D glyph;

void main(){

	// Output color = color of the texture at the specified UV
	gl_FragColor = texture2D(glyph, outUV);
}
"""


class GLWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(parent)

    def __del__(self):
        GL.glDeleteProgram(self.program_id)

    def initializeGL(self):
        GL.glClearColor(0.0, 0.0, 0.4, 0.0)
	    
        # Create and compile our GLSL program from the shaders
        self.program_id = shaders.compileProgram(shaders.compileShader(VERTEX_SHADER, GL.GL_VERTEX_SHADER),
                                                 shaders.compileShader(FRAGMENT_SHADER, GL.GL_FRAGMENT_SHADER))

        # Get a handle for our buffers
        self.vertex_position_id = GL.glGetAttribLocation(self.program_id, "vertexPos")
        self.vertex_uv_id = GL.glGetAttribLocation(self.program_id, "vertexUV")
        self.texture_id  = GL.glGetUniformLocation(self.program_id, "glyph")

        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
    
        # Set the texture wrapping parameters
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP)
    
        # Set texture filtering parameters
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    
        image, vertex = self.createTexture('This is just a test')
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, image.width(), image.height(), 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, ctypes.c_void_p(image.constBits().__int__()))

        g_vertex_buffer_data = np.array(vertex, np.float32) 
        g_uv_buffer_data = np.array([0, 0, 0, 1, 1, 0, 1, 1], np.float32)
        g_element_buffer_data = np.array([0, 1, 2, 1, 2, 3], np.uint32)

        self.vertex_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertex_buffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, g_vertex_buffer_data.itemsize * len(g_vertex_buffer_data),  g_vertex_buffer_data, GL.GL_STATIC_DRAW)
    
        self.uv_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.uv_buffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, g_uv_buffer_data.itemsize * len(g_uv_buffer_data),  g_uv_buffer_data, GL.GL_STATIC_DRAW)

        self.element_buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.element_buffer)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, g_element_buffer_data.itemsize * len(g_element_buffer_data), g_element_buffer_data, GL.GL_STATIC_DRAW)
        

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        # Enable Transparency 
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        # Use our shader
        GL.glUseProgram(self.program_id)

        scale_loc = GL.glGetUniformLocation(self.program_id, "scale")
        position_loc = GL.glGetUniformLocation(self.program_id, "position")
        GL.glUniform2fv(scale_loc, 1, [2.0/self.width(), -2.0/self.height()])
        GL.glUniform3fv(position_loc, 1, [10, 10, 0])

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

        # 2nd attribute buffer : uv
        GL.glEnableVertexAttribArray(self.vertex_uv_id)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.uv_buffer)
        GL.glVertexAttribPointer(self.vertex_uv_id,  2, GL.GL_FLOAT, GL.GL_FALSE, 0, ctypes.c_void_p(0))

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.element_buffer)
        GL.glDrawElements(GL.GL_TRIANGLES, 6, GL.GL_UNSIGNED_INT, ctypes.c_void_p(0))
        GL.glDisableVertexAttribArray(self.vertex_position_id)
        GL.glDisableVertexAttribArray(self.vertex_uv_id)
        GL.glDisable(GL.GL_BLEND)

    @staticmethod
    def createTexture(text):
        font = QtGui.QFont("Times", 10)
        metric = QtGui.QFontMetrics(font)
        rect = metric.boundingRect(text)
        
        # The glyph texture would typically be generated for each character but QT helps 
        image = QtGui.QImage(rect.size(), QtGui.QImage.Format.Format_RGBA8888)
        image.fill(QtCore.Qt.GlobalColor.transparent)
        painter = QtGui.QPainter()
        painter.begin(image)
        painter.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing | QtGui.QPainter.RenderHint.TextAntialiasing)
        painter.setFont(font)
        painter.setPen(QtGui.QColor.fromRgbF(0, 1, 0))
        painter.drawText(0, metric.ascent(), text)  
        painter.end()

        w = rect.width()
        h = rect.height()
        vertex = [0., 0., 0., 0., h, 0., w, 0., 0., w, h, 0.]

        return image, vertex
    

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(500, 500)
        self.setWindowTitle('Glyphs Texture')

        self.glWidget = GLWidget(self)
        self.setCentralWidget(self.glWidget)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())