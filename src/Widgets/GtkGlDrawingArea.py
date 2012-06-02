from gi.repository import Gtk, Gdk
from gi.repository import GObject
from gi.repository import GdkX11
import pyglet
from pyglet import gl
import time
#from pyglet.gl import *
from OpenGL.GL import *
from OpenGL.GLU import *
from pyglet.gl import Config, gl_info, glu_info
import sys
import numpy
import Globals
from OpenGL.GL.shaders import *
if sys.platform in ('win32','cygwin'):
  from pyglet.window.win32 import _user32
  from pyglet.gl import wgl
elif sys.platform == 'linux2':
  from pyglet.image.codecs.gdkpixbuf2 import gdk
  from pyglet.gl import glx



def ReadFile(filename):
    readfile = open(filename,'r')
    source = readfile.read()
    readfile.close()
    return source
def ReadBinaryFile(filename):
    readfile = open(filename,'rb')
    source = readfile.read()
    readfile.close()
    return source

def MakeBuffer(target, data, size):
    TempBuffer = glGenBuffers(1)
    glBindBuffer(target, TempBuffer)
    glBufferData(target, size, data, GL_STATIC_DRAW)
    return TempBuffer

class BoxedLabel(pyglet.text.Label):
    
    def __init__(self,text='', font_name=None, font_size=None, 
                 bold=False, italic=False, color=(255, 255, 255, 255), 
                 x=0, y=0, width=None, height=None, anchor_x='left', 
                 anchor_y='baseline', halign='left', multiline=False, 
                 dpi=None, batch=None, group=None, bgcolor=(0,0,0,0)):
        pyglet.text.Label.__init__(self,text,font_name,font_size,bold,italic,color,x,y,width,height,anchor_x,anchor_y,halign,multiline,dpi,batch,group)
        self.begin_update()
        self.set_style("background_color", bgcolor)
        self.set_style("color", color)
        self.end_update()

class ExpandedImageData(pyglet.image.ImageData):
    
    
    def _get_gl_format_and_type(self, format):
        if format == 'I':
            return GL_LUMINANCE, GL_UNSIGNED_BYTE
        elif format == 'L':
            return GL_LUMINANCE, GL_UNSIGNED_BYTE
        elif format == 'LA':
            return GL_LUMINANCE_ALPHA, GL_UNSIGNED_BYTE
        elif format == 'R':
            return GL_RED, GL_UNSIGNED_BYTE
        elif format == 'G':
            return GL_GREEN, GL_UNSIGNED_BYTE
        elif format == 'B':
            return GL_BLUE, GL_UNSIGNED_BYTE
        elif format == 'A':
            return GL_ALPHA, GL_UNSIGNED_BYTE
        elif format == 'RGB':
            return GL_RGB, GL_UNSIGNED_BYTE
        elif format == 'RGBA':
            return GL_RGBA, GL_UNSIGNED_BYTE
        elif (format == 'ARGB' and
              gl_info.have_extension('GL_EXT_bgra') and
              gl_info.have_extension('GL_APPLE_packed_pixels')):
            return GL_BGRA, GL_UNSIGNED_INT_8_8_8_8_REV
        elif (format == 'ABGR' and
              gl_info.have_extension('GL_EXT_abgr')):
            return GL_ABGR_EXT, GL_UNSIGNED_BYTE
        elif (format == 'BGR' and
              gl_info.have_extension('GL_EXT_bgra')):
            return GL_BGR, GL_UNSIGNED_BYTE
        elif (format == 'BGRA' and
              gl_info.have_extension('GL_EXT_bgra')):
            return GL_BGRA, GL_UNSIGNED_BYTE
        elif (format == 'ABGR1555'):
            return GL_BGRA,GL_UNSIGNED_SHORT_1_5_5_5_REV

        return None, None
    


class GtkGlDrawingArea(Gtk.DrawingArea):
    config=None
    context=None

    def __init__(self):
        self.gl_initialized = 0
        self.get_config()
        self.texture = glGenTextures(1)
        self.inheight = 1
        self.inwidth = 1
        self.gameimage=None
        Gtk.DrawingArea.__init__(self)
        self.set_double_buffered(0)
        self.connect('draw', self.expose)
        self.connect('configure-event', self.configure)
    def update_texture(self,data,width,height, pitch, dataformat):
        self.inheight = height
        self.inwidth = width
        self.gameimage = ExpandedImageData(width,height,dataformat,data)
        self.gameimage = self.gameimage.get_texture()
        self.gameimage = self.gameimage.get_transform(flip_y=True)
        self.queue_draw()
        
        #print self.gameimage.get_texture()
        #self.texture = texture

    def get_config(self):
        if not self.config:
            platform = pyglet.window.get_platform()
            self.display = platform.get_default_display()
            self.screen = self.display.get_screens()[0]

        for template_config in [
                                Config(double_buffer=True, depth_size=32),
                                Config(double_buffer=True, depth_size=24),
                                Config(double_buffer=True, depth_size=16)]:
            try:
                self.config = self.screen.get_best_config(template_config) 
                break
            except pyglet.window.NoSuchConfigException:
                pass

        if not self.config:
            raise pyglet.window.NoSuchConfigException(
                            'No standard config is available.')

        if not self.config.is_complete():
            print 'not complete'
            self.config = self.screen.get_best_config(self.config)

      #print self.config.get_gl_attributes()

        if not self.context:
            self.context = self.config.create_context(pyglet.gl.current_context)

    def setup(self):
    # One-time GL setup
        glClearColor(0, 0, 0, 1)
        glColor3f(1, 0, 0)
        #glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
    # Define a simple function to create ctypes arrays of floats:
        def vec(*args):
            return (GLfloat * len(args))(*args)

        if sys.platform in ('win32', 'cygwin'):
            self.lowerlabel = pyglet.text.Label('Hello, world',
font_size=14, font_name='Arial',
                                          x=5, y=20)
            self.upperlabel = pyglet.text.Label('Hello, world',
font_size=14, font_name='Arial',
                                          x=20, y=20)
        else:
            self.lowerlabel = pyglet.text.Label('Hello, world',
font_size=14, font_name='DejaVu Sans Mono',
                                          x=5, y=20)
            self.upperlabel = BoxedLabel('Hello, world',
font_size=14, font_name='DejaVu Sans Mono',
                                          x=20, y=20, bgcolor = (0,0,0,255))
            

    def switch_to(self):
        if sys.platform == 'darwin':
            agl.aglSetCurrentContext(self._agl_context)
            _aglcheck()
        elif sys.platform in ('win32', 'cygwin'):
            self._dc = _user32.GetDC(self.window.handle)
            self.context._set_window(self)
            wgl.wglMakeCurrent(self._dc, self.context._context)
        else:
            glx.glXMakeCurrent(self.config._display, self.get_property('window').get_xid(),self.context._context)
        self.context.set_current()
        gl_info.set_active_context()
        glu_info.set_active_context()

    def flip(self):
        if sys.platform == 'darwin':
            agl.aglSwapBuffers(self._agl_context)
            _aglcheck()
        elif sys.platform in ('win32', 'cygwin'):
            wgl.wglSwapLayerBuffers(self._dc, wgl.WGL_SWAP_MAIN_PLANE)
        else:
            glx.glXSwapBuffers(self.config._display, self.get_property('window').get_xid())

    def configure(self, d, event):
        self.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.BLANK_CURSOR))
        width = d.get_allocated_width()
        height = d.get_allocated_height()
        if width > 1:
            self.switch_to()
            if not self.gl_initialized:
                self.setup()
                self.gl_initialized = 1
            glViewport(0, 0, width, height)
        return 0

    def expose(self, d, event):
        width = d.get_allocated_width()
        height = d.get_allocated_height()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60., width / float(height), .1, 1000.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -4)
        glEnable(GL_LIGHTING)
        glColor3f(1, 0, 0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width,0, height, -1, 1)
        glViewport(0,0,width,height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glDisable(GL_LIGHTING)
        glColor3f(1, 1, 1)
        keepAspectRatio = Globals.SettingsXML.find("AspectRatio").get("keep")
        if keepAspectRatio == "True":
            heightratio = float(height)/self.inheight
            widthratio = float(width)/self.inwidth
            if widthratio <= heightratio:
                drawheight = int(self.inheight*widthratio)
                drawwidth = int(self.inwidth*widthratio)
            else:
                drawheight = int(self.inheight*heightratio)
                drawwidth = int(self.inwidth*heightratio)
        else:
            drawwidth,drawheight = width,height
        YPos = height/2 - drawheight/2
        XPos = width/2 - drawwidth/2
        if self.gameimage:
            self.gameimage.blit(XPos, YPos+225, 0,drawwidth,drawheight)
            
        self.upperlabel.text = time.strftime('Now is %H:%M:%S')
        self.upperlabel.x = width - self.upperlabel.content_width -5
        self.upperlabel.y = height - self.upperlabel.content_height
        self.upperlabel.draw()

        if self.config.double_buffer:
            self.flip()
        else:
            glFlush()
        return 0