from PyKrita import * #fake import for IDE

from krita import *
import json
import requests
from ..misc import utility


class Dialog(QDialog):
	def __init__(self, worker):
		super().__init__(None)

		self.worker = worker
		self.utils = utils = utility.Checker()
		settings = self.readSettings()

		self.setWindowTitle("Stablehorde")
		self.layout = QVBoxLayout()

		# Basic Tab
		tabBasic = QWidget()
		layout = QFormLayout()

		# Generation Mode
		box = QGroupBox()
		self.modeText2Img = QRadioButton("Text -> Image")
		self.modeImg2Img = QRadioButton("Image -> Image")
		self.modeInpainting = QRadioButton("Inpainting")
		layoutV = QVBoxLayout()
		layoutV.addWidget(self.modeText2Img)
		layoutV.addWidget(self.modeImg2Img)
		layoutV.addWidget(self.modeInpainting)
		box.setLayout(layoutV)
		label = QLabel("Generation Mode")
		label.setStyleSheet("QLabel{margin-top:12px;}")
		layout.addRow(label, box)

		group = QButtonGroup()
		group.addButton(self.modeText2Img, self.worker.MODE_TEXT2IMG)
		group.addButton(self.modeImg2Img, self.worker.MODE_IMG2IMG)
		group.addButton(self.modeInpainting, self.worker.MODE_INPAINTING)
		group.button(settings["generationMode"]).setChecked(True)
		self.generationMode = group
		self.generationMode.buttonClicked.connect(self.handleModeChanged)

		mode = self.generationMode.checkedId()

		# NSFW
		self.nsfw = QCheckBox()
		self.nsfw.setCheckState(settings["nsfw"])
		layout.addRow("NSFW",self.nsfw)

		# Seed
		self.seed = QLineEdit()
		self.seed.setText(settings["seed"])
		layout.addRow("Seed (optional)", self.seed)

		# Model
		self.model = QComboBox()
		#get a list of models from the server
		try:
			response = requests.get("https://stablehorde.com/api/v2/status/models")
			models = json.loads(response.text)
			for model in models:
				self.model.addItem(model["name"])
		except Exception as ex:
			self.utils.errorMessage("Error", "Could not connect to the server to get a list of models.")
			self.reject()
		self.model.setCurrentIndex(settings["model"])
		layout.addRow("Model", self.model)

		# Prompt
		self.prompt = QTextEdit()
		self.prompt.setText(settings["prompt"])
		layout.addRow("Prompt", self.prompt)

		# Status
		self.statusDisplay = QTextEdit()
		self.statusDisplay.setReadOnly(True)
		layout.addRow("Status", self.statusDisplay)

		# Generate
		self.generateButton = QPushButton("Generate")
		self.generateButton.clicked.connect(self.generate)
		layout.addWidget(self.generateButton)

		# Space
		layoutH = QHBoxLayout()
		layoutH.addSpacing(50)
		container = QWidget()
		container.setLayout(layoutH)
		layout.addWidget(container)

		# Cancel
		cancelButton = QPushButton("Cancel")
		cancelButton.setFixedWidth(100)
		cancelButton.clicked.connect(self.reject)
		layout.addWidget(cancelButton)
		layout.setAlignment(cancelButton, Qt.AlignRight)

		tabBasic.setLayout(layout)

		# Advanced Tab
		tabAdvanced = QWidget()
		layout = QFormLayout()

		# Init Strength
		slider = QSlider(Qt.Orientation.Horizontal, self)
		slider.setRange(0, 10)
		slider.setTickInterval(1)
		slider.setValue(settings["initStrength"])
		self.initStrength = slider
		labelInitStrength = QLabel(str(self.initStrength.value()/10))
		self.initStrength.valueChanged.connect(lambda: labelInitStrength.setText(str(self.initStrength.value()/10)))
		layoutH = QHBoxLayout()
		layoutH.addWidget(self.initStrength)
		layoutH.addWidget(labelInitStrength)
		container = QWidget()
		container.setLayout(layoutH)
		layout.addRow("Init Strength", container)

		if mode == worker.MODE_TEXT2IMG or mode == worker.MODE_INPAINTING:
			self.initStrength.setEnabled(False)

		# Prompt Strength
		slider = QSlider(Qt.Orientation.Horizontal, self)
		slider.setRange(0, 20)
		slider.setTickInterval(1)
		slider.setValue(settings["promptStrength"])
		self.promptStrength = slider
		labelPromptStrength = QLabel(str(self.promptStrength.value()))
		self.promptStrength.valueChanged.connect(lambda: labelPromptStrength.setText(str(self.promptStrength.value())))
		layoutH = QHBoxLayout()
		layoutH.addWidget(self.promptStrength)
		layoutH.addWidget(labelPromptStrength)
		container = QWidget()
		container.setLayout(layoutH)
		layout.addRow("Prompt Strength", container)

		# Steps
		slider = QSlider(Qt.Orientation.Horizontal, self)
		slider.setRange(10, 200)
		slider.setTickInterval(1)
		slider.setValue(settings["steps"])
		self.steps = slider
		labelSteps = QLabel(str(self.steps.value()))
		self.steps.valueChanged.connect(lambda: labelSteps.setText(str(self.steps.value())))
		layoutH = QHBoxLayout()
		layoutH.addWidget(self.steps)
		layoutH.addWidget(labelSteps)
		container = QWidget()
		container.setLayout(layoutH)
		layout.addRow("Steps", container)

		# API Key
		self.apikey = QLineEdit()
		self.apikey.setText(settings["apikey"])
		layout.addRow("API Key (optional)", self.apikey)

		# Max Wait
		slider = QSlider(Qt.Orientation.Horizontal, self)
		slider.setRange(1, 5)
		slider.setTickInterval(1)
		slider.setValue(settings["maxWait"])
		self.maxWait = slider
		labelMaxWait = QLabel(str(self.maxWait.value()))
		self.maxWait.valueChanged.connect(lambda: labelMaxWait.setText(str(self.maxWait.value())))
		layoutH = QHBoxLayout()
		layoutH.addWidget(self.maxWait)
		layoutH.addWidget(labelMaxWait)
		container = QWidget()
		container.setLayout(layoutH)
		layout.addRow("Max Wait (minutes)", container)

		tabAdvanced.setLayout(layout)

		tabs = QTabWidget()
		tabs.addTab(tabBasic, "Basic")
		tabs.addTab(tabAdvanced, "Advanced")
		self.layout.addWidget(tabs)

		self.setLayout(self.layout)
		self.resize(350, 300)

		webpSupport = utils.checkWebpSupport()

		if webpSupport is False:
			self.generateButton.setEnabled(False)
			self.statusDisplay.setText("Your operating system doesn't support the webp image format. Please check troubleshooting section of readme on GitHub for solution.")

		update = utils.checkUpdate()

		if update["update"] is True:
			self.statusDisplay.setText(update["message"])

	def handleModeChanged(self):
		mode = self.generationMode.checkedId()

		if mode == self.worker.MODE_TEXT2IMG or mode == self.worker.MODE_INPAINTING:
			self.initStrength.setEnabled(False)
		elif mode == self.worker.MODE_IMG2IMG:
			self.initStrength.setEnabled(True)

	def generate(self):
		mode = self.generationMode.checkedId()
		doc = Application.activeDocument()

		# no document
		if doc is None:
			self.utils.errorMessage("Please open a document. Please check details.", "For image generation a document with a size between 384x384 and 1024x1024, color model 'RGB/Alpha', color depth '8-bit integer' and a paint layer is needed.")
			return
		# document has invalid color model or depth
		elif doc.colorModel() != "RGBA" or doc.colorDepth() != "U8":
			self.errorMessage("Invalid document properties. Please check details.", "For image generation a document with color model 'RGB/Alpha', color depth '8-bit integer' is needed.")
			return
		# document too small or large
		elif doc.width() < 384 or doc.width() > 1024 or doc.height() < 384 or doc.height() > 1024:
			self.errorMessage("Invalid document size. Please check details.", "Document needs to be between 384x384 and 1024x1024.")
			return
		# img2img/inpainting: missing init image layer
		elif (mode == self.worker.MODE_IMG2IMG or mode == self.worker.MODE_INPAINTING) and self.worker.getInitNode() is None:
			self.errorMessage("Please add a visible layer which shows the init/inpainting image.", "")
			return
		# img2img/inpainting: selection has to be removed otherwise crashes krita when creating init image
		elif (mode == self.worker.MODE_IMG2IMG or mode == self.worker.MODE_INPAINTING) and doc.selection() is not None:
			self.errorMessage("Please remove the selection by clicking on the image.", "")
			return
		# no prompt
		elif len(self.prompt.toPlainText()) == 0:
			self.errorMessage("Please enter a prompt.", "")
			return
		else:
			self.writeSettings()
			self.setEnabledStatus(False)
			self.statusDisplay.setText("Waiting for generated image...")
			self.worker.generate(self)

	#override
	def customEvent(self, ev):
		if ev.type() == self.worker.eventId:
			if ev.updateType == utility.UpdateEvent.TYPE_CHECKED:
				self.statusDisplay.setText(ev.message)
			elif ev.updateType == utility.UpdateEvent.TYPE_INFO:
				self.statusDisplay.setText(ev.message)
				self.setEnabledStatus(True)
			elif ev.updateType == utility.UpdateEvent.TYPE_ERROR:
				self.statusDisplay.setText("An error occurred: " + ev.message)
				self.setEnabledStatus(True)
			elif ev.updateType == utility.UpdateEvent.TYPE_FINISHED:
				self.close()

	#override
	def reject(self):
		self.worker.cancel()
		self.writeSettings()
		super().reject()

	def readSettings(self):
		defaults = {
			"generationMode": self.worker.MODE_TEXT2IMG,
			"initStrength": 3,
			"prompt": "",
			"promptStrength": 8,
			"steps": 50,
			"seed": "",
			"nsfw": 0,
			"apikey": "",
			"maxWait": 5
		}

		try:
			settings = Application.readSetting("Stablehorde", "Config", None)

			if not settings:
				settings = defaults
			else:
				settings = json.loads(settings)
				missing = False

			for key in defaults:
				if not key in settings:
					missing = True
					break

			if missing is True:
				settings = defaults
		except Exception as ex:
			settings = defaults

		return settings

	def writeSettings(self):
		settings = {
			"generationMode": self.generationMode.checkedId(),
			"initStrength": self.initStrength.value(),
			"prompt": self.prompt.toPlainText(),
			"promptStrength": self.promptStrength.value(),
			"steps": int(self.steps.value()),
			"seed": self.seed.text(),
			"nsfw": self.nsfw.checkState(),
			"apikey": self.apikey.text(),
			"maxWait": self.maxWait.value()
		}

		try:
			settings = json.dumps(settings)
			Application.writeSetting("Stablehorde", "Config", settings)
		except Exception as ex:
			ex = ex

	def setEnabledStatus(self, status):
		self.modeText2Img.setEnabled(status)
		self.modeImg2Img.setEnabled(status)
		self.modeInpainting.setEnabled(status)

		if self.generationMode.checkedId() == self.worker.MODE_IMG2IMG:
			self.initStrength.setEnabled(status)

		self.promptStrength.setEnabled(status)
		self.steps.setEnabled(status)
		self.seed.setEnabled(status)
		self.nsfw.setEnabled(status)
		self.prompt.setEnabled(status)
		self.apikey.setEnabled(status)
		self.maxWait.setEnabled(status)
		self.generateButton.setEnabled(status)