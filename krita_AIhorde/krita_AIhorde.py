# v2.0.1

from krita import *
from PyKrita import * #fake import for IDE
from PyQt5.QtCore import qDebug #logging calls conflict in Krita, so use qDebug instead
from .core import horde
from .misc import utility
from .frontend import widget

class AIhorde(DockWidget):
   def __init__(self):#, parent):
      super().__init__()#parent)
      self.setWindowTitle("AI Horde")
      self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
      qDebug('AIhorde started') #won't be running at this point, but might save to file?
      self.setWidget(widget.Dialog())

   def setup(self):
      pass

   def canvasChanged(self, canvas):
      pass

   def createActions(self, window):
      pass

Krita.instance().addDockWidgetFactory(DockWidgetFactory("AIhorde", DockWidgetFactoryBase.DockLeft, AIhorde))

