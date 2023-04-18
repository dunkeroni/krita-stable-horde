from PyKrita import * #fake import for IDE

from krita import *
import json
import urllib.request
from ..misc import utility


class Dialog(QWidget):
	def __init__(self, worker):
		super().__init__()#None)

		self.worker = worker
		self.utils = utils = utility.Checker()
		settings = self.readSettings()

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
			self.denoise_strength.setEnabled(False)
		elif mode == self.worker.MODE_IMG2IMG:
			self.denoise_strength.setEnabled(True)

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
				#set status to none and activate the generate button again
				self.statusDisplay.setText("Done.")
				self.setEnabledStatus(True)
				
	#override
	def reject(self):
		self.worker.cancel()
		self.writeSettings()
		super().reject()

	def readSettings(self):
		defaults = {
			"generationMode": self.worker.MODE_TEXT2IMG,
			"denoise_strength": 30,
			"prompt": "",
			"negativePrompt": "",
			"promptStrength": 7,
			"steps": 20,
			"seed": "",
			"nsfw": True,
			"apikey": "",
			"maxWait": 5,
			"highResFix": False,
			"karras": True,
			"clip_skip": 1,
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
			"denoise_strength": self.denoise_strength.value(),
			"prompt": self.prompt.toPlainText(),
			"negativePrompt": self.negativePrompt.toPlainText(),
			"promptStrength": self.promptStrength.value(),
			"steps": int(self.steps.value()),
			"seed": self.seed.text(),
			"nsfw": self.nsfw.checkState(),
			"apikey": self.apikey.text(),
			"maxWait": self.maxWait.value(),
			"highResFix": self.highResFix.checkState(),
			"karras": self.karras.checkState(),
			"clip_skip": self.clip_skip.value(),
		}

		try:
			settings = json.dumps(settings)
			Application.writeSetting("Stablehorde", "Config", settings)
		except Exception as ex:
			ex = ex

	def setEnabledStatus(self, status):
		#Update these to include all the widgets that should be disabled when generating
		self.modeText2Img.setEnabled(status)
		self.modeImg2Img.setEnabled(status)
		self.modeInpainting.setEnabled(status)

		if self.generationMode.checkedId() == self.worker.MODE_IMG2IMG:
			self.denoise_strength.setEnabled(status)

		self.promptStrength.setEnabled(status)
		self.steps.setEnabled(status)
		self.seed.setEnabled(status)
		self.nsfw.setEnabled(status)
		self.prompt.setEnabled(status)
		self.apikey.setEnabled(status)
		self.maxWait.setEnabled(status)
		self.generateButton.setEnabled(status)

	def setupBasicTab(self, settings):
		# ================ Basic Tab ================
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

		if mode == self.worker.MODE_TEXT2IMG or mode == self.worker.MODE_INPAINTING:
			self.denoise_strength.setEnabled(False)

		# Seed
		self.seed = QLineEdit()
		self.seed.setText(settings["seed"])
		layout.addRow("Seed (optional)", self.seed)

		# Model
		self.model = QComboBox()
		#get a list of models from the server
		try:
			response = urllib.request.urlopen("https://stablehorde.net/api/v2/status/models")
			models = json.loads(response.read())
			
			#sort models based on Count
			models = sorted(models, key=lambda k: k['count'], reverse=True)

			#add to combobox
			for model in models:
				self.model.addItem(model["name"] + " (" + str(model["count"]) + ")", model["name"])
		except Exception as ex:
			self.utils.errorMessage("Error", "Could not connect to the server to get a list of models.")
			self.reject()
		self.model.setCurrentIndex(0)
		layout.addRow("Model", self.model)

		# sampler
		self.sampler = QComboBox()
		self.sampler_options = [ 'k_lms', 'k_heun', 'k_euler', 'k_euler_a', 'k_dpm_2', 'k_dpm_2_a', 'k_dpm_fast', 'k_dpm_adaptive', 'k_dpmpp_2s_a', 'k_dpmpp_2m', 'dpmsolver', 'k_dpmpp_sde', 'DDIM' ]
		for sampler in self.sampler_options:
			self.sampler.addItem(sampler)
		self.sampler.setCurrentIndex(3)
		layout.addRow("Sampler", self.sampler)

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
		self.highResFix.setChecked(settings["highResFix"])
		layout.addRow("High Resolution Fix",self.highResFix)

		# Prompt
		self.prompt = QTextEdit()
		self.prompt.setText(settings["prompt"])
		layout.addRow("Prompt", self.prompt)

		# Negative Prompt
		self.negativePrompt = QTextEdit()
		self.negativePrompt.setText(settings["negativePrompt"])
		layout.addRow("Negative Prompt", self.negativePrompt)

		# Status
		self.statusDisplay = QTextEdit()
		self.statusDisplay.setReadOnly(True)
		layout.addRow("Status", self.statusDisplay)

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
		#get user info from server with the find_user API call
		apikey = "0000000000" if self.apikey.text() == "" else self.apikey.text()
		headers = {"Content-Type": "application/json", "Accept": "application/json", "apikey": apikey, "Client-Agent": "dunkeroni's crappy Krita plugin"}
		url="https://stablehorde.net/api/v2/find_user"
		request = urllib.request.Request(url=url, headers=headers)
		response = urllib.request.urlopen(request)
		data = response.read()
		try:
			self.userInfo = json.loads(data)
			#update values from userInfo
			self.userID.setText(self.userInfo["username"])
			self.kudos.setText(str(self.userInfo["kudos"]))
			self.trusted.setText(str(self.userInfo["trusted"]))
			self.requests.setText(str(self.userInfo["records"]["request"]["image"]))
			self.contributions.setText(str(self.userInfo["records"]["fulfillment"]["image"]))
			
		except urllib.error.HTTPError as e:
			raise Exception(data)