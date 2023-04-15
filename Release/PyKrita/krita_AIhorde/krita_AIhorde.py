# v1.3.4

from krita import *
from PyKrita import * #fake import for IDE
from .core import horde
from .misc import utility
from .frontend import widget

class Stablehorde(Extension):
   def __init__(self, parent):
      super().__init__(parent)

   def setup(self):
      pass

   def createActions(self, window):
      action = window.createAction("generate", "Stablehorde", "tools/scripts")
      action.triggered.connect(self.openDialog)

   def openDialog(self):
      dialog = widget.Dialog(worker)
      dialog.exec()

Krita.instance().addExtension(Stablehorde(Krita.instance()))
utils = utility.Checker()
worker = horde.Worker()
#dialog = Dialog()
#dialog.exec()
