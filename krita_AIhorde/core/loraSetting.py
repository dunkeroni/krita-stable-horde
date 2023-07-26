from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class LoraSetting():
	HORDE_MAX_SIZE_MB = 150

	def __init__(self, layout: QFormLayout):
		self.parentLayout = layout
		self.layout = QFormLayout()
		self.layout.setAlignment(Qt.AlignTop)
		#create a container widget to hold the layout
		self.frame = QWidget() #contains the layout so it can be hidden
		self.frame.setLayout(self.layout)
		self.parentLayout.addWidget(self.frame)
		self.frame.setContentsMargins(0, 0, 0, 0)
		self.frame.setMinimumSize(0, 0)
		self.frame.resize(0, 0)

		#create local variables for each setting
		self.name = ""
		self.filename = ""
		self.id = "" #STRING
		self.description = ""
		self.checkbox = None
		self.trigger = None
		self.unetStrength = None
		self.textEncoderStrength = 1.0
		self.unetStrength = 1.0
		self.nsfw = False
		self.trainedWords = []
		self.promptTrigger = "" #unused
		self.rating = 0.0
		self.sizeKB = 0.0

		#status variables
		self.built = False
		self.hidden = False

	def build(self):
		qDebug("Adding controls for " + self.name)
		#add checkbox
		checkbox = QCheckBox()
		checkbox.setChecked(False)
		label = QLabel(self.name + " (" + self.id + ")")
		#add to layout
		Hlayout = QHBoxLayout()
		Hlayout.addWidget(checkbox) 
		Hlayout.addWidget(label)
		Hlayout.setAlignment(Qt.AlignLeft)
		lablecontainer = QWidget()
		lablecontainer.setLayout(Hlayout)
		lablecontainer.setMinimumSize(0, 0)
		self.layout.addWidget(lablecontainer)
		label.setToolTip(self.description)

		#add lineEdit for trained words
		lineEdit = QLineEdit(str(self.trainedWords))
		lineEdit.setReadOnly(True)
		trainedWordslabel = QLabel("Trained Words:")
		Hlayout = QHBoxLayout()
		Hlayout.setContentsMargins(0, 0, 0, 0)
		Hlayout.addWidget(trainedWordslabel)
		Hlayout.addWidget(lineEdit)
		trainedWordscontainer = QWidget()
		trainedWordscontainer.setLayout(Hlayout)
		trainedWordscontainer.setMinimumSize(0, 0)
		self.layout.addWidget(trainedWordscontainer)
		#tooltip
		trainedWordsTooltip = "The words the model was trained on (if any).\nIf there are words in here, you can use them in your prompt to get better results.\nHover over the lora name to see if the civitai description has any other hints on use."
		lineEdit.setToolTip(trainedWordsTooltip)
		trainedWordslabel.setToolTip(trainedWordsTooltip)

		#add lineEdit for custom trigger word, default to name
		lineEdit = QLineEdit(self.name)
		triggerlabel = QLabel("Prompt Trigger:")
		Hlayout = QHBoxLayout()
		Hlayout.addWidget(triggerlabel)
		Hlayout.addWidget(lineEdit)
		triggercontainer = QWidget()
		triggercontainer.setLayout(Hlayout)
		triggercontainer.setMinimumSize(0, 0)
		self.layout.addWidget(triggercontainer)
		#tooltip
		promptTriggerTooltip = "YOU DO NOT NEED TO USE TRIGGER WORDS IN YOUR PROMPT.\n\n At this time, the setting appears to do nothing. I have included it in case that changes.\nYou can just enable and control loras from the checkbox."
		lineEdit.setToolTip(promptTriggerTooltip)
		triggerlabel.setToolTip(promptTriggerTooltip)

		#Add two strength sliders
		# Unet Strength
		unetStrength = QSlider(Qt.Orientation.Horizontal)
		unetStrength.setRange(0, 10)
		unetStrength.setTickInterval(1)
		unetStrength.setValue(10)
		labelUnetStrength = QLabel(str(unetStrength.value()/10))
		unetStrength.valueChanged.connect(lambda: labelUnetStrength.setText(str(unetStrength.value()/10)))
		l2US = QLabel("Unet Strength")
		layoutH = QHBoxLayout()
		layoutH.addWidget(l2US)
		layoutH.addWidget(unetStrength)
		layoutH.addWidget(labelUnetStrength)
		UScontainer = QWidget()
		UScontainer.setLayout(layoutH)
		UScontainer.setMinimumSize(0, 0)
		self.layout.addWidget(UScontainer)
		#tooltip
		unetStrengthTooltip = "How strongly the LoRA will affect how the model generates the image."
		unetStrength.setToolTip(unetStrengthTooltip)
		l2US.setToolTip(unetStrengthTooltip)

		# Text Encoder Strength
		slider = QSlider(Qt.Orientation.Horizontal)
		slider.setRange(0, 10)
		slider.setTickInterval(1)
		slider.setValue(10)
		textEncoderStrength = slider
		labelTextEncoderStrength = QLabel(str(textEncoderStrength.value()/10))
		textEncoderStrength.valueChanged.connect(lambda: labelTextEncoderStrength.setText(str(textEncoderStrength.value()/10)))
		l2CS = QLabel("Text Encoder Strength")
		layoutH = QHBoxLayout()
		layoutH.addWidget(l2CS)
		layoutH.addWidget(textEncoderStrength)
		layoutH.addWidget(labelTextEncoderStrength)
		CScontainer = QWidget()
		CScontainer.setLayout(layoutH)
		CScontainer.setMinimumSize(0, 0)
		self.layout.addWidget(CScontainer)
		#tooltip
		textEncoderStrengthTooltip = "How strongly the LoRA will affect how the model processes the prompt."
		textEncoderStrength.setToolTip(textEncoderStrengthTooltip)
		l2CS.setToolTip(textEncoderStrengthTooltip)

		#reduce buffer spacing
		trainedWordscontainer.layout().setContentsMargins(0, 0, 0, 0)
		triggercontainer.layout().setContentsMargins(0, 0, 0, 0)
		UScontainer.layout().setContentsMargins(0, 0, 0, 0)
		CScontainer.layout().setContentsMargins(0, 0, 0, 0)
		lablecontainer.layout().setContentsMargins(0, 0, 0, 0)
		self.frame.setContentsMargins(0, 0, 0, 0)
		self.frame.layout().setContentsMargins(0, 0, 0, 0)
		self.layout.setContentsMargins(0, 0, 0, 0)

		#connect show/hide to checkbox
		trainedWordscontainer.setVisible(False)
		triggercontainer.setVisible(False)
		UScontainer.setVisible(False)
		CScontainer.setVisible(False)
		
		#.stateChanged.connect(lambda: triggercontainer.setVisible(checkbox.isChecked())) #hiding this until we need it for something in the future
		checkbox.stateChanged.connect(lambda: UScontainer.setVisible(checkbox.isChecked()))
		checkbox.stateChanged.connect(lambda: CScontainer.setVisible(checkbox.isChecked()))
		checkbox.stateChanged.connect(lambda: trainedWordscontainer.setVisible(checkbox.isChecked()))

		#preserve references to the elements
		self.checkbox = checkbox
		self.trigger = lineEdit
		self.unetStrength = unetStrength
		self.textEncoderStrength = textEncoderStrength

		#set status
		self.built = True
	
	def hide(self):
		self.frame.setVisible(False)
		self.hidden = True
		pass

	def show(self):
		self.frame.setVisible(True)
		self.hidden = False
		pass

	def isValid(self, nsfw = True, searchText = "", searchID = True, searchName = True, searchDescription = True):
		#check if this lora is valid
		valid = True #default case
		
		#true when nsfw is enabled or the lora is not nsfw
		valid = valid and (not(self.nsfw) or nsfw) 

		#true when the lora is smaller than maxSizeMB
		valid = valid and (self.sizeKB <= self.HORDE_MAX_SIZE_MB * 1024)

		#searches text if the filter is active
		valid = valid and self.search(searchText, searchID, searchName, searchDescription)

		return valid

	def search(self, searchText, searchID, searchName, searchDescription):
		if searchText == "": #default case
			return True
		searchText = searchText.lower() #case insensitive
		
		if searchID:
			#check if the searchText appears in the ID
			if self.id.lower().find(searchText) != -1:
				return True
		if searchName:
			#check if the searchText appears in the name
			if self.name.lower().find(searchText) != -1:
				return True
		if searchDescription:
			#check if the searchText appears in the description
			if self.description.lower().find(searchText) != -1:
				return True
			
		return False #no matches found