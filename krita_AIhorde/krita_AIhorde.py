# v1.3.4

from krita import *
from PyKrita import * #fake import for IDE
from .core import horde
from .misc import utility
from .frontend import widget

class AIhorde(DockWidget):
   def __init__(self):#, parent):
      super().__init__()#parent)
      self.setWindowTitle("AIhorde")
      self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
      self.setWidget(widget.Dialog(worker))

   def setup(self):
      pass

   def canvasChanged(self, canvas):
      pass

   def createActions(self, window):
      action = window.createAction("generate", "Stablehorde", "tools/scripts")
      action.triggered.connect(self.openDialog)

   def openDialog(self):
      dialog = widget.Dialog(worker)
      dialog.exec()

#Krita.instance().addExtension(AIhorde(Krita.instance()))
#add AIhorde to the dockwidgetfactory
#Krita.instance().addDockWidgetFactory(DockWidgetFactory("AIhorde", DockWidgetFactoryBase.DockRight, AIhorde))
utils = utility.Checker()
worker = horde.Worker()
Krita.instance().addDockWidgetFactory(DockWidgetFactory("AIhorde", DockWidgetFactoryBase.DockLeft, AIhorde))
#dialog = Dialog()
#dialog.exec()
