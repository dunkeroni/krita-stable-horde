# v2.0.1

from krita import *
from .frontend import widget

class AIhorde(DockWidget):
	def __init__(self):#, parent):
		super().__init__()#parent)
		self.setWindowTitle("AI Horde")
		self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
		self.setWidget(widget.Dialog())

	def setup(self):
		pass

	def canvasChanged(self, canvas):
		pass

	def createActions(self, window):
		pass

Krita.instance().addDockWidgetFactory(DockWidgetFactory("AIhorde", DockWidgetFactoryBase.DockLeft, AIhorde))

