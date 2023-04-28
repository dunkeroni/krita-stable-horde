from PyKrita import * #fake import for IDE
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ..misc import utility
from ..core import hordeAPI, horde
from ..misc import range_slider


class Dialog(QWidget):
	def __init__(self, worker):
		super().__init__()

		self.worker: horde.Worker = worker
		self.utils = utils = utility.Checker()
		settings = utility.readSettings()
		self.maskMode = False

		self.setWindowTitle("AI Horde")
		self.layout = QVBoxLayout()

		tabBasic = self.setupBasicTab(settings)
		tabAdvanced = self.setupAdvancedTab(settings)
		tabUser = self.setupUserTab(settings)
		
		tabs = QTabWidget()
		tabs.addTab(tabBasic, "Basic")
		tabs.addTab(tabAdvanced, "Advanced")
		tabs.addTab(tabUser, "User")
		self.layout.addWidget(tabs)

		self.setLayout(self.layout)
		self.resize(350, 300)

		if utils.checkWebpSupport() is False:
			self.generateButton.setEnabled(False)
			self.statusDisplay.setText("Your operating system doesn't support the webp image format. Please check troubleshooting section of readme on GitHub for solution.")

		update = utils.checkUpdate()

		if update["update"] is True:
			self.statusDisplay.setText(update["message"])

	def handleModeChanged(self):
		mode = self.generationMode.checkedId()

		if mode == self.worker.MODE_TEXT2IMG or mode == self.worker.MODE_INPAINTING:
			self.denoise_strength.setEnabled(False)
			self.minSize.setEnabled(False)
		elif mode == self.worker.MODE_IMG2IMG:
			self.denoise_strength.setEnabled(True)
			self.minSize.setEnabled(True)
	
	def toggleMaskMode(self, forceDisable = False):
		if self.maskMode or forceDisable:
			qDebug("Disabling mask mode...")
			self.maskMode = False
			self.maskButton.setText("Mask")
			self.img2imgButton.setText("Img2Img")
			self.maskButton.setStyleSheet("background-color:#015F90;")
		else:
			if utility.document() is None:
				utility.errorMessage("Please open a document. Please check details.", "For image generation a document with a size at or above 384x384, color model 'RGB/Alpha', color depth '8-bit integer' and a paint layer is needed.")
				return
			if utility.document().selection() is None:
				utility.errorMessage("Make a selection.", "Please select a region of the document before enabling mask mode.")
				return
			qDebug("Enabling mask mode...")
			self.maskMode = True
			self.maskButton.setText("Cancel")
			self.img2imgButton.setText("Inpaint")
			self.maskButton.setStyleSheet("background-color:#890000;")

	def img2imgGenerate(self):
		if utility.document().selection() is None:
			utility.errorMessage("Make a selection.", "Please select a region of the document before enaging Img2Img mode.")
			return
		self.generate(True, self.maskMode)
		self.toggleMaskMode(True)

	def generate(self, img2img = False, inpainting = False):
		qDebug("Generating image from dialog call...")
		doc = utility.document()

		# no document
		if doc is None:
			utility.errorMessage("Please open a document. Please check details.", "For image generation a document with a size at or above 384x384, color model 'RGB/Alpha', color depth '8-bit integer' and a paint layer is needed.")
			return
		# document has invalid color model or depth
		elif doc.colorModel() != "RGBA" or doc.colorDepth() != "U8":
			utility.errorMessage("Invalid document properties. Please check details.", "For image generation a document with color model 'RGB/Alpha', color depth '8-bit integer' is needed.")
			return
		# document too small or large
		#elif doc.width() < 384 or doc.width() > 1024 or doc.height() < 384 or doc.height() > 1024:
			#utility.errorMessage("Invalid document size. Please check details.", "Document needs to be between 384x384 and 1024x1024.")
			#return
		# img2img/inpainting: missing init image layer
		#elif (mode == self.worker.MODE_IMG2IMG or mode == self.worker.MODE_INPAINTING) and self.worker.getInitNode() is None:
			#utility.errorMessage("Please add a visible layer which shows the init/inpainting image.", "")
			#return
		# img2img/inpainting: selection has to be removed otherwise crashes krita when creating init image
		#elif (mode == self.worker.MODE_IMG2IMG or mode == self.worker.MODE_INPAINTING) and doc.selection() is not None:
			#utility.errorMessage("Please remove the selection by clicking on the image.", "")
			#return
		# no prompt
		elif len(self.prompt.toPlainText()) == 0:
			utility.errorMessage("Please enter a prompt.", "")
			return
		else:
			utility.writeSettings(self)
			self.setEnabledStatus(False)
			self.statusDisplay.setText("Waiting for generated image...")
			self.worker.generate(self, img2img, inpainting)

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
				#set status to none and activate the generate button again
				#self.statusDisplay.setText("Done.")
				self.setEnabledStatus(True)
				
	#override
	def reject(self):
		self.worker.cancel()
		utility.writeSettings(self)
		super().reject()

	def setEnabledStatus(self, status):
		#Update these to include all the widgets that should be disabled when generating
		self.promptStrength.setEnabled(status)
		self.model.setEnabled(status)
		self.sampler.setEnabled(status)
		self.denoise_strength.setEnabled(status)
		self.SizeRange.setEnabled(status)
		self.steps.setEnabled(status)
		self.seed.setEnabled(status)
		self.nsfw.setEnabled(status)
		self.prompt.setEnabled(status)
		self.negativePrompt.setEnabled(status)
		self.karras.setEnabled(status)
		self.highResFix.setEnabled(status)
		self.clip_skip.setEnabled(status)
		self.apikey.setEnabled(status)
		self.maxWait.setEnabled(status)
		self.postProcessing.setEnabled(status)
		self.facefixer_strength.setEnabled(status)
		self.upscale.setEnabled(status)
		self.generateButton.setEnabled(status)

	def setupBasicTab(self, settings):
		# ================ Basic Tab ================
		tabBasic = QWidget()
		layout = QFormLayout()

		# Generate
		self.generateButton = QPushButton("Generate")
		self.generateButton.clicked.connect(self.generate)
		self.generateButton.setStyleSheet("background-color:#A04200;")
		layout.addWidget(self.generateButton)

		# Mask and Img2Img buttons
		self.maskButton = QPushButton("Mask")
		self.maskButton.clicked.connect(self.toggleMaskMode)
		self.img2imgButton = QPushButton("Img2Img")
		self.img2imgButton.clicked.connect(self.img2imgGenerate)
		self.maskButton.setStyleSheet("background-color:#015F90;")
		self.img2imgButton.setStyleSheet("background-color:#015F90;")
		layout.addRow(self.maskButton, self.img2imgButton)

		# Denoise Strength
		slider = QSlider(Qt.Orientation.Horizontal, self)
		slider.setRange(0, 100)
		slider.setTickInterval(1)
		slider.setValue(settings["denoise_strength"])
		self.denoise_strength = slider
		labeldenoise_strength = QLabel(str(self.denoise_strength.value()/100))
		self.denoise_strength.valueChanged.connect(lambda: labeldenoise_strength.setText(str(self.denoise_strength.value()/100)))
		layoutH = QHBoxLayout()
		layoutH.addWidget(self.denoise_strength)
		layoutH.addWidget(labeldenoise_strength)
		container = QWidget()
		container.setLayout(layoutH)
		layout.addRow("Denoising", container)

		#multi size range slider
		self.SizeRange = range_slider.RangeSlider(Qt.Orientation.Horizontal, self)
		self.SizeRange.setRange(4, 32) #increments of 64
		self.SizeRange.setLow(8)
		self.SizeRange.setHigh(32)
		self.SizeRange.sliderMoved.connect(lambda: self.SizeRangeLabel.setText(str(self.SizeRange.low()*64) + " - " + str(self.SizeRange.high()*64)))
		layoutH = QHBoxLayout()
		layoutH.addWidget(self.SizeRange)
		self.SizeRangeLabel = QLabel(str(self.SizeRange.low()*64) + " - " + str(self.SizeRange.high()*64))
		layoutH.addWidget(self.SizeRangeLabel)
		container = QWidget()
		container.setLayout(layoutH)
		layout.addRow("Size Range", container)

		# Seed
		self.seed = QLineEdit()
		self.seed.setText(settings["seed"])
		layout.addRow("Seed (optional)", self.seed)

		# Model
		self.model = QComboBox()
		#get a list of models from the server
		models = hordeAPI.status_models()

		#add to combobox
		for model in models:
			self.model.addItem(model["name"] + " (" + str(model["count"]) + ")", model["name"])
		self.model.setCurrentIndex(0)
		layout.addRow("Model", self.model)

		# sampler
		self.sampler = QComboBox()
		self.sampler_options = [ 'k_lms', 'k_heun', 'k_euler', 'k_euler_a', 'k_dpm_2', 'k_dpm_2_a', 'k_dpm_fast', 'k_dpm_adaptive', 'k_dpmpp_2s_a', 'k_dpmpp_2m', 'dpmsolver', 'k_dpmpp_sde', 'DDIM' ]
		for sampler in self.sampler_options:
			self.sampler.addItem(sampler)
		self.sampler.setCurrentIndex(3)
		layout.addRow("Sampler", self.sampler)

		#number of images
		self.numImages = QSpinBox()
		self.numImages.setRange(1, 10)
		self.numImages.setValue(1)
		layout.addRow("Number of Images", self.numImages)
		
		# Steps
		slider = QSlider(Qt.Orientation.Horizontal, self)
		slider.setRange(10, 150)
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
		
		#HighResFix
		self.highResFix = QCheckBox()
		self.highResFix.setChecked(False)
		layout.addRow("High Resolution Fix",self.highResFix)

		# Prompt
		self.prompt = QTextEdit()
		self.prompt.setText(settings["prompt"])
		layout.addRow("Prompt", self.prompt)

		# Negative Prompt
		self.negativePrompt = QTextEdit()
		self.negativePrompt.setText(settings["negativePrompt"])
		layout.addRow("Negative Prompt", self.negativePrompt)

		# Post Processing combobox
		self.postProcessing = QComboBox()
		postProcessing_options = ['None', 'GFPGAN', 'CodeFormers', 'strip_background' ]
		for postProcessing in postProcessing_options:
			self.postProcessing.addItem(postProcessing)
		self.postProcessing.setCurrentIndex(0)
		layout.addRow("Post Processing", self.postProcessing)

		# facefixer_strength
		slider = QSlider(Qt.Orientation.Horizontal, self)
		slider.setRange(0, 100)
		slider.setTickInterval(1)
		slider.setValue(75)
		self.facefixer_strength = slider
		labelfacefixer_strength = QLabel(str(self.facefixer_strength.value()/100))
		self.facefixer_strength.valueChanged.connect(lambda: labelfacefixer_strength.setText(str(self.facefixer_strength.value()/100)))
		layoutH = QHBoxLayout()
		layoutH.addWidget(self.facefixer_strength)
		layoutH.addWidget(labelfacefixer_strength)
		container = QWidget()
		container.setLayout(layoutH)
		layout.addRow("Facefixer Strength", container)

		# Upscaler combobox
		self.upscale = QComboBox()
		upscale_options = ['None', 'RealESRGAN_x4plus', 'RealESRGAN_x2plus', 'RealESRGAN_x4plus_anime_6B', 'NMKD_Siax', '4x_AnimeSharp' ]
		for upscale in upscale_options:
			self.upscale.addItem(upscale)
		self.upscale.setCurrentIndex(0)
		layout.addRow("Upscaler", self.upscale)

		# Status
		self.statusDisplay = QTextEdit()
		self.statusDisplay.setReadOnly(True)
		layout.addRow("Status", self.statusDisplay)

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

		return tabBasic

	def setupAdvancedTab(self, settings):
		# ==============Advanced Tab================
		tabAdvanced = QWidget()
		layout = QFormLayout()

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
		layout.addRow("CFG", container)

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

		#clip_skip slider
		slider = QSlider(Qt.Orientation.Horizontal, self)
		slider.setRange(1, 12)
		slider.setTickInterval(1)
		slider.setValue(settings["clip_skip"])
		self.clip_skip = slider
		labelClipSkip = QLabel(str(self.clip_skip.value()))
		self.clip_skip.valueChanged.connect(lambda: labelClipSkip.setText(str(self.clip_skip.value())))
		layoutH = QHBoxLayout()
		layoutH.addWidget(self.clip_skip)
		layoutH.addWidget(labelClipSkip)
		container = QWidget()
		container.setLayout(layoutH)
		layout.addRow("Clip Skip (broken)", container)
		
		# NSFW
		self.nsfw = QCheckBox()
		self.nsfw.setChecked(settings["nsfw"])
		layout.addRow("NSFW",self.nsfw)

		# Karras
		self.karras = QCheckBox()
		self.karras.setChecked(settings["karras"])
		layout.addRow("Karras",self.karras)


		tabAdvanced.setLayout(layout)
		return tabAdvanced
	
	def setupUserTab(self, settings):
		tabUser = QWidget()
		layout = QFormLayout()

		# API Key
		self.apikey = QLineEdit()
		self.apikey.setText(settings["apikey"])
		#make the apikey text hidden
		self.apikey.setEchoMode(QLineEdit.Password)
		layout.addRow("API Key (optional)", self.apikey)

		#user ID
		self.userID = QLineEdit()
		self.userID.setReadOnly(True)
		layout.addRow("User ID", self.userID)

		#kudos
		self.kudos = QLineEdit()
		self.kudos.setReadOnly(True)
		layout.addRow("Kudos", self.kudos)

		#trusted
		self.trusted = QLineEdit()
		self.trusted.setReadOnly(True)
		layout.addRow("Trusted", self.trusted)

		# usage["requests"]
		self.requests = QLineEdit()
		self.requests.setReadOnly(True)
		layout.addRow("Requests", self.requests)

		# usage["contributions"]
		self.contributions = QLineEdit()
		self.contributions.setReadOnly(True)
		layout.addRow("Contributions", self.contributions)

		#add a refresh button
		self.refreshUserButton = QPushButton("Refresh")
		self.refreshUserButton.clicked.connect(self.updateUserInfo)
		layout.addRow(self.refreshUserButton)

		self.updateUserInfo() #populate actual values if they exist

		tabUser.setLayout(layout)

		return tabUser
	
	def updateUserInfo(self):
		qDebug("Updating user info")
		#get user info from server with the find_user API call
		self.userInfo = hordeAPI.find_user(self.apikey.text())
		#update values from userInfo
		if self.userInfo:
			self.userID.setText(self.userInfo["username"])
			self.kudos.setText(str(self.userInfo["kudos"]))
			self.trusted.setText(str(self.userInfo["trusted"]))
			self.requests.setText(str(self.userInfo["records"]["request"]["image"]))
			self.contributions.setText(str(self.userInfo["records"]["fulfillment"]["image"]))