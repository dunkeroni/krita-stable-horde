from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import math

from ..misc import utility, range_slider, kudos
from ..core import hordeAPI, horde, resultCollector
from ..frontend import basicTab, advancedTab, userTab, loraTab, resultsTab, tooltips

class Dialog(QWidget):
	def __init__(self):
		super().__init__()

		self.maskMode = False

		self.setWindowTitle("AI Horde")
		self.layout = QVBoxLayout()
		
		# Create tabs
		tabs = QTabWidget()
		self.basic = basicTab.addBasicTab(tabs, self)
		self.advanced = advancedTab.addAdvancedTab(tabs, self)
		self.user = userTab.addUserTab(tabs) #doesn't need self because no sliders in user tab
		self.loraSettings = loraTab.addLoraTab(tabs, self)
		self.results = resultsTab.addResultsTab(tabs, self)
		self.layout.addWidget(tabs)
		self.tabs = tabs

		self.setLayout(self.layout)
		self.resize(350, 300)

		self.collectElements()
		self.settings = utility.readSettings()
		self.applyLoadedSettings(self.settings)
		
		self.connectFunctions()
		#self.updateKudos()
		self.refreshUser()

		self.connectToolTips() #add tooltip text to all the UI elements

		self.rescol = resultCollector.ResultCollector(self.results)
		self.worker = horde.Worker(self) #needs dialog reference for threaded event messages

		if utility.checkWebpSupport() is False:
			self.generateButton.setEnabled(False)
			self.statusDisplay.setText("Your operating system doesn't support the webp image format. Please check troubleshooting section of readme on GitHub for solution.")

		update = utility.checkUpdate()
		if update["update"] is True:
			self.statusDisplay.setText(update["message"])
	
	def collectElements(self):
		#All UI elements that the dialog panel sees should be listed here
		### Basic ###
		self.priceCheck: QPushButton = self.basic['priceCheck']
		self.generateButton: QPushButton = self.basic['generateButton']
		self.maskButton: QPushButton = self.basic['maskButton']
		self.img2imgButton: QPushButton = self.basic['img2imgButton']
		self.denoise_strength: QSlider = self.basic['denoise_strength']
		self.CFG: QSlider = self.basic['CFG']
		self.SizeRange: range_slider.RangeSlider = self.basic['SizeRange']
		self.highResFix: QCheckBox = self.basic['highResFix']
		self.seed: QLineEdit = self.basic['seed']
		self.model: QComboBox = self.basic['model']
		self.sampler: QComboBox = self.basic['sampler']
		self.steps: QSlider = self.basic['steps']
		self.prompt: QTextEdit = self.basic['prompt']
		self.negativePrompt: QTextEdit = self.basic['negativePrompt']
		self.numImages: QSpinBox = self.basic['numImages']
		self.upscale: QComboBox = self.basic['upscale']
		self.statusDisplay: QLabel = self.basic['statusDisplay']
		self.cancelButton: QPushButton = self.basic['cancelButton']

		### Advanced ###
		self.maxWait: QSlider = self.advanced['maxWait']
		self.clip_skip: QSlider = self.advanced['clip_skip']
		self.nsfw: QCheckBox = self.advanced['nsfw']
		self.karras: QCheckBox = self.advanced['karras']
		self.useRealInpaint: QCheckBox = self.advanced['useRealInpaint']
		self.shareWithLAION: QCheckBox = self.advanced['shareWithLAION']
		self.inpaintMode: QButtonGroup = self.advanced['inpaintMode']
		self.postProcessing: QComboBox = self.advanced['postProcessing']
		self.facefixer_strength: QSlider = self.advanced['facefixer_strength']

		### User ###
		self.apikey: QLineEdit = self.user['apikey']
		self.userID: QLineEdit = self.user['userID']
		self.workerIDs: QLineEdit = self.user['workerIDs']
		self.kudos: QLineEdit = self.user['kudos']
		self.trusted: QLineEdit = self.user['trusted']
		self.concurrency: QLineEdit = self.user['concurrency']
		self.requests: QLineEdit = self.user['requests']
		self.contributions: QLineEdit = self.user['contributions']
		self.refreshUserButton: QPushButton = self.user['refreshUserButton']
		self.preferredWorkers: QLineEdit = self.user['preferredWorkers']
		self.transferUserName: QLineEdit = self.user['transferUserName']
		self.transferKudosAmount: QLineEdit = self.user['transferKudosAmount']
		self.transferKudosButton: QPushButton = self.user['transferKudosButton']

		### EXPERIMENTAL ###
		#Temporary settings that add extra functionality for testing: 0 = Img2Img PostMask, 1 = Img2Img PreMask, 2 = Img2Img DoubleMask, 3 = Inpaint Raw Mask
		#self.inpaintMode: QButtonGroup = self.experiment['inpaintMode']

		### RESULTS ###
		self.groupSelector: QComboBox = self.results['groupSelector']
		self.nextResult: QPushButton = self.results['nextResult']
		self.prevResult: QPushButton = self.results['prevResult']
		self.deleteButton: QPushButton = self.results['deleteButton']
		self.deleteAllButton: QPushButton = self.results['deleteAllButton']
		self.genInfo: QTextEdit = self.results['genInfo']

	def connectToolTips(self):
		allWidgets = {}
		allWidgets.update(self.basic)
		allWidgets.update(self.advanced)
		allWidgets.update(self.user)
		#allWidgets.update(self.lora)
		allWidgets.update(self.results)
		tooltips.addToolTips(allWidgets)

	def connectFunctions(self):
		#User button connections
		self.generateButton.clicked.connect(self.generate)
		self.maskButton.clicked.connect(self.toggleMaskMode)
		self.img2imgButton.clicked.connect(self.img2imgGenerate)
		self.cancelButton.clicked.connect(self.reject)
		self.refreshUserButton.clicked.connect(self.refreshUser)
		self.transferKudosButton.clicked.connect(self.transferKudos)

		#kudos update connections
		self.priceCheck.clicked.connect(self.updateKudos)
		self.denoise_strength.valueChanged.connect(self.updateKudos)
		self.SizeRange.sliderMoved.connect(self.updateKudos)
		self.sampler.currentTextChanged.connect(self.updateKudos)
		self.numImages.valueChanged.connect(self.updateKudos)
		self.steps.valueChanged.connect(self.updateKudos)
		self.postProcessing.currentTextChanged.connect(self.updateKudos)
		self.upscale.currentTextChanged.connect(self.updateKudos)
		self.shareWithLAION.stateChanged.connect(self.updateKudos)

	def applyLoadedSettings(self, settings):
		self.denoise_strength.setValue(int(settings["denoise_strength"]*100))
		self.seed.setText(settings["seed"])
		self.steps.setValue(settings["steps"])
		self.prompt.setText(settings["prompt"])
		self.negativePrompt.setText(settings["negativePrompt"])
		#self.CFG.setValue(settings["CFG"])
		self.maxWait.setValue(settings["maxWait"])
		self.clip_skip.setValue(settings["clip_skip"])
		self.nsfw.setChecked(settings["nsfw"])
		self.karras.setChecked(settings["karras"])
		self.apikey.setText(settings["apikey"])
		self.shareWithLAION.setChecked(settings["shared"])

	def getFirstFiveLoras(self):
		loras = []
		n = 0
		for setting in self.loraSettings:
			if setting.checkbox.isChecked():
				loras.append({
					"name": str(setting.id), #horde resolves ID, removes possibility of duplicate names
					"model": setting.unetStrength.value()/10,
					"clip": setting.textEncoderStrength.value()/10,
					#"inject_trigger": setting.trigger.text()
				})
				n += 1
				if n == 5:
					break
		return loras

	def generate(self, img2img = False, inpainting = False):
		qDebug("Generating image from dialog call...")
		doc = Krita.instance().activeDocument()

		# no document
		if doc is None:
			utility.errorMessage("Please open a document. Please check details.", "For image generation a document with color model 'RGB/Alpha', color depth '8-bit integer' and a paint layer is needed.")
			return
		# document has invalid color model or depth
		elif doc.colorModel() != "RGBA" or doc.colorDepth() != "U8":
			utility.errorMessage("Invalid document properties. Please check details.", "For image generation a document with color model 'RGB/Alpha', color depth '8-bit integer' is needed.")
			return
		# no prompt
		elif len(self.prompt.toPlainText()) == 0:
			utility.errorMessage("Please enter a prompt.", "")
			return
		else:
			utility.writeSettings(self.getCurrentSettings())
			self.setEnabledStatus(False)
			self.refreshUser() #doesn't work later in threaded instances, so might as well do it early
			self.statusDisplay.setText("Waiting for generated image...")

			settings = self.getCurrentSettings()
			settings["genImg2img"] = img2img
			settings["genInpainting"] = inpainting
			kudosCost = self.worker.generate(settings) #trigger threaded generation task
			#self.worker.triggerGenerate.emit(settings) #trigger threaded generation task
	
	def img2imgGenerate(self):
		if Krita.instance().activeDocument().selection() is None:
			utility.errorMessage("Make a selection.", "Please select a region of the document before enaging Img2Img mode.")
			return
		self.generate(True, self.maskMode)
		self.toggleMaskMode(True)

	def toggleMaskMode(self, forceDisable = False):
		doc = Krita.instance().activeDocument()
		if self.maskMode or forceDisable:
			qDebug("Disabling mask mode...")
			self.maskMode = False
			self.maskButton.setText("Mask")
			self.img2imgButton.setText("Img2Img")
			self.maskButton.setStyleSheet("background-color:#015F90;")
			self.generateButton.setEnabled(True)
			utility.deleteMaskNode() #get rid of masking layer
			Krita.instance().action("KisToolSelectRectangular").trigger() #change tool to selection
			doc.waitForDone()
		else:
			if doc is None:
				utility.errorMessage("Please open a document. Please check details.", "For image generation a document with a size at or above 384x384, color model 'RGB/Alpha', color depth '8-bit integer' and a paint layer is needed.")
				return
			if doc.selection() is None:
				utility.errorMessage("Make a selection.", "Please select a region of the document before enabling mask mode.")
				return
			qDebug("Enabling mask mode...")
			self.maskMode = True
			self.maskButton.setText("Cancel")
			self.img2imgButton.setText("Inpaint")
			self.maskButton.setStyleSheet("background-color:#890000;")
			self.generateButton.setEnabled(False)

			maskNode = utility.createMaskNode()
			if maskNode is None:
				return
			doc.setActiveNode(maskNode) #activate new layer
			Krita.instance().action("KritaShape/KisToolDyna").trigger() #set tool to brush for inpaint mask
			doc.waitForDone()
		self.updateKudos()	
				
	#override
	def reject(self):
		self.worker.cancel()
		utility.writeSettings(self.getCurrentSettings())

	def setEnabledStatus(self, status):
		#Update these to include all the widgets that should be disabled when generating
		self.CFG.setEnabled(status)
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
		self.img2imgButton.setEnabled(status)
		self.maskButton.setEnabled(status)
		self.priceCheck.setEnabled(status)

	def getCurrentSettings(self):
		payloadData = self.getPayloadData()
		return {
			#basics
			"denoise_strength": self.denoise_strength.value()/100,
			"minSize": self.SizeRange.low()*64,
			"maxSize": self.SizeRange.high()*64,
			"seed": self.seed.text(),
			"model": self.model.currentData(),
			"sampler_name": self.sampler.currentText(),
			"numImages": self.numImages.value(),
			"steps": self.steps.value(),
			"highResFix": self.highResFix.isChecked(),
			"prompt": self.prompt.toPlainText(),
			"negativePrompt": self.negativePrompt.toPlainText(),
			"postProcessing": self.postProcessing.currentText(),
			"upscale": self.upscale.currentText(),
			"facefixer_strength": self.facefixer_strength.value()/100,
			#advanced
			"CFG": self.CFG.value()/4,
			"maxWait": self.maxWait.value(),
			"clip_skip": self.clip_skip.value(),
			"nsfw": self.nsfw.isChecked(),
			"karras": self.karras.isChecked(),
			"tiling": False,
			"useRealInpaint": self.useRealInpaint.isChecked(),
			#user
			"apikey": self.apikey.text(),
			"workers": [],
			#CONTROL NET TO BE ADDED LATER
			#misc
			"maskMode": self.maskMode,
			"trusted_workers": False,
			"slow_workers": True,
			"censor_nsfw": False,
			"shared": self.shareWithLAION.isChecked(),
			"replacement_filter": True,
			#Format for API generation request
			"payloadData": payloadData,
			#Experimental
			"inpaintMode": self.inpaintMode.checkedId()
		}
	
	def getPayloadData(self):
		prompt = self.prompt.toPlainText() + (" ### " + self.negativePrompt.toPlainText() if self.negativePrompt.toPlainText() != "" else "")
		post_processor = [self.postProcessing.currentText()] if self.postProcessing.currentText() != "None" else []
		upscaler = [self.upscale.currentText()] if self.upscale.currentText() != "None" else []
		post_process = post_processor + upscaler
		params = {
			"sampler_name": self.sampler.currentText(),
			"cfg_scale": self.CFG.value()/4,
			"steps": int(self.steps.value()),
			"seed": self.seed.text(),
			"hires_fix": self.highResFix.isChecked(),
			"karras": self.karras.isChecked(),
			"post_processing": post_process,
			"facefixer_strength": self.facefixer_strength.value()/100,
			"clip_skip": self.clip_skip.value(),
			"n": self.numImages.value(),
			"loras": self.getFirstFiveLoras()
		}
		if params["loras"] == []: #not sure if this is necessary, worker was being funky one day
			del params["loras"]

		data = {
			#append negative prompt only if it is not empty
			"prompt": prompt,
			"params": params,
			"nsfw": self.nsfw.isChecked(),
			"trust_workers": False,
			"slow_workers": True,
			"censor_nsfw": not(self.nsfw.isChecked()),
			"r2": True,
			"models": [self.model.currentData()],
			"shared": self.shareWithLAION.isChecked(),
			"replacement_filter": True,
			"dry_run": False
		}

		#add preferred workers if not empty
		if self.preferredWorkers.text() != "":
			workerlist = self.preferredWorkers.text().split(",")
			data["workers"] = workerlist
			data["worker_blacklist"] = False

		return data
	
	def updateKudos(self):
		doc = Krita.instance().activeDocument()
		if doc is None:
			return
		selection = doc.selection()
		minSize = self.SizeRange.low()*64
		maxSize = self.SizeRange.high()*64
		if selection is None:
			width = height = minSize
		else: #stimate gen size
			w = selection.width()
			h = selection.height()
			if max(w, h) > maxSize:
				r = maxSize/min(w, h)
			elif min(w, h) < minSize:
				r = minSize/max(w, h)
			else:
				r = 1
			width = math.ceil(w*r/64)*64
			height = math.ceil(h*r/64)*64
		
		post = [self.postProcessing.currentText(), self.upscale.currentText()]
		denoise = self.denoise_strength.value()/100
		prompt = self.prompt.toPlainText() + " ### " + self.negativePrompt.toPlainText()

		kt = kudos.calculateKudos(width, height, self.steps.value(), self.sampler.currentText(),
			   False, False, denoise, post,
			   False, prompt, self.shareWithLAION.isChecked())

		ki = kudos.calculateKudos(width, height, self.steps.value(), self.sampler.currentText(),
			   True, True, self.denoise_strength.value()/100, post,
			   False, self.prompt.toPlainText(), self.shareWithLAION.isChecked())
		
		txtKudos = round(kt*self.numImages.value(),2)
		imgKudos = round(ki*self.numImages.value(),2)

		self.generateButton.setText("Generate (" + str(txtKudos) + " kudos)")
		if self.maskMode:
			self.img2imgButton.setText("Inpaint (" + str(imgKudos) + " kudos)")
		else:
			self.img2imgButton.setText("Img2Img (" + str(imgKudos) + " kudos)")

	def refreshUser(self):
		qDebug("Updating user info")
		#get user info from server with the find_user API call
		self.userInfo = hordeAPI.find_user(self.apikey.text())
		#update values from userInfo
		if self.userInfo:
			self.userID.setText(self.userInfo["username"])
			self.workerIDs.setText(", ".join(self.userInfo["worker_ids"]))
			self.kudos.setText(str(self.userInfo["kudos"]))
			self.trusted.setText(str(self.userInfo["trusted"]))
			self.concurrency.setText(str(self.userInfo["concurrency"]))
			self.requests.setText(str(self.userInfo["records"]["request"]["image"]))
			self.contributions.setText(str(self.userInfo["records"]["fulfillment"]["image"]))
	
	def transferKudos(self):
		qDebug("Transferring kudos")
		#make sure ammount is a number
		try:
			amount = abs(int(self.transferKudosAmount.text()))
		except ValueError:
			utility.errorMessage("Invalid amount.", "Please enter a number.")
			return
		#make sure targetUsername is not empty
		targetUsername = self.transferUserName.text()
		if targetUsername == "":
			utility.errorMessage("Invalid username.", "Please enter a username.")
			return
		#make sure targetUsername is not the same as current username
		if targetUsername == self.userID.text():
			utility.errorMessage("Invalid username.", "You cannot send kudos to yourself.")
			return
		hordeAPI.transferKudos(self.apikey.text(), targetUsername, amount)

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
				self.setEnabledStatus(True)
			elif ev.updateType == utility.UpdateEvent.TYPE_RESULTS:
				self.rescol.setBuffer(ev.message)
				self.rescol.bufferToDB()
				self.tabs.setCurrentIndex(4)
	
	@pyqtSlot(str)
	def updateStatus(self, status):
		self.statusDisplay.setText(status)