from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import qDebug

from ..core.loraSetting import LoraSetting

class LoraSearcher():
	def __init__(self, scrollArea: QScrollArea):
		self.scrollArea = scrollArea
		self.layout = QFormLayout()
		self.loraList = [] #list of LoraSetting objects to be filled later

		self.createSearchArea(self.layout)

	def setLoraList(self, loraList: list):
		self.loraList: list[LoraSetting] = loraList

	def createSearchArea(self, layout: QFormLayout):
		#load from Civitai
		# number of LoRAs to load spinbox
		self.numLoras = QSpinBox()
		self.numLoras.setRange(1, 9999)
		self.numLoras.setValue(100)
		#Load Loras pushbutton
		self.loadLorasButton = QPushButton("Load LoRAs")
		#add to layout
		Hlayout = QHBoxLayout()
		Hlayout.addWidget(self.numLoras)
		Hlayout.addWidget(self.loadLorasButton)
		loadLorasContainer = QWidget()
		loadLorasContainer.setLayout(Hlayout)
		layout.addRow(loadLorasContainer)

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
		self.filterButtons[0].setToolTip("NOTE: May not be accurate. Depends on creators and users to flag NSFW models.")
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
		for sett in self.loraList:
			result = sett.isValid(self.filterButtons[0].isChecked(), self.searchbar.text(), self.filterButtons[1].isChecked(), self.filterButtons[2].isChecked(), self.filterButtons[3].isChecked())
			if result:
				sett.show()
			else:
				sett.hide()
		pass




