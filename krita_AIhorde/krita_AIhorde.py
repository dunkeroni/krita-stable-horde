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
      #action = window.createAction("generate", "Stablehorde", "tools/scripts")
      #action.triggered.connect(self.openDialog)

   #def openDialog(self):
      #dialog = widget.Dialog(worker)
      #dialog.exec()

#Krita.instance().addExtension(AIhorde(Krita.instance()))
#add AIhorde to the dockwidgetfactory
#Krita.instance().addDockWidgetFactory(DockWidgetFactory("AIhorde", DockWidgetFactoryBase.DockRight, AIhorde))
#utils = utility.Checker()
#worker = horde.Worker()
Krita.instance().addDockWidgetFactory(DockWidgetFactory("AIhorde", DockWidgetFactoryBase.DockLeft, AIhorde))
#dialog = Dialog()
#dialog.exec()
