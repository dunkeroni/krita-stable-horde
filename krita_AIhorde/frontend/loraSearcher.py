from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ..core.loraSetting import LoraSetting

class loraSearcher():
	def __init__(self, scrollArea: QScrollArea):
		self.scrollArea = scrollArea
		self.layout = scrollArea.widget().layout()



	def createSearchBar(layout: QFormLayout):
		#create search bar
		searchbar = QLineEdit()
		searchbar.setPlaceholderText("Search")
		layout.addRow(searchbar)
		return searchbar


