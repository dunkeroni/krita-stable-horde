from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ..core.loraSetting import LoraSetting

class LoraSearcher():
	def __init__(self, scrollArea: QScrollArea):
		self.scrollArea = scrollArea
		self.layout = QFormLayout()

		self.createSearchArea(self.layout)


	def createSearchArea(self, layout: QFormLayout):
		#create search bar, inline with a "Search" pushbutton
		self.searchbar = QLineEdit()
		self.searchbar.setPlaceholderText("Search")
		self.searchbar.setClearButtonEnabled(True)
		self.searchbar.setFixedWidth(200)
		self.searchbar.setFixedHeight(30)
		self.searchbar.returnPressed.connect(self.search) #search on enter
		self.searchbar.setToolTip("Search for models by name, description, or ID")
		self.searchButton = QPushButton("Search")
		self.searchButton.setFixedWidth(100)
		self.searchButton.setFixedHeight(30)
		self.searchButton.clicked.connect(self.search) #search on click
		#add to layout
		Hlayout = QHBoxLayout()
		Hlayout.addWidget(self.searchbar)
		Hlayout.addWidget(self.searchButton)
		searchcontainer = QWidget()
		searchcontainer.setLayout(Hlayout)
		layout.addRow(searchcontainer)
		
		#row of checkboxes to toggle filters
		self.filterButtons = []
		self.filterButtons.append(QCheckBox("Show NSFW"))
		self.filterButtons.append(QCheckBox("Search ID"))
		self.filterButtons.append(QCheckBox("Search Name"))
		self.filterButtons.append(QCheckBox("Search Desc"))		

		#add to layout
		Hlayout = QHBoxLayout()
		for button in self.filterButtons:
			button.setChecked(True) #default all buttons to true
			Hlayout.addWidget(button)
		filtercontainer = QWidget()
		filtercontainer.setLayout(Hlayout)
		layout.addRow(filtercontainer)

	def search(self):
		qDebug("Searching for LoRAS")
		#apply filters and include matching loraSetting objects
		pass




