# v1.3.4

from krita import *
from PyKrita import * #fake import for IDE
from PyQt5.QtCore import qDebug #logging calls conflict in Krita, so use qDebug instead
import logging
from .core import horde
from .misc import utility
from .frontend import widget

from os import path

class AIhorde(DockWidget):
   def __init__(self):#, parent):
      super().__init__()#parent)
      self.setWindowTitle("AIhorde")
      self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
      qDebug('AIhorde started') #won't be running at this point, but might save to file?
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
