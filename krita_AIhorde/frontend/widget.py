from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import math

from ..misc import utility, range_slider, kudos
from ..core import hordeAPI, horde
from ..frontend import UIactions, basicTab, advancedTab, userTab

class Dialog(QWidget):
	def __init__(self):
		super().__init__()

		self.maskMode = False

		self.setWindowTitle("AI Horde")
		self.layout = QVBoxLayout()

		self.actor = UIactions.UIActor(self)
		
		# Create tabs
		tabs = QTabWidget()
		self.basic = basicTab.addBasicTab(tabs, self.actor, self)
		self.advanced = advancedTab.addAdvancedTab(tabs, self.actor, self)
		self.user = userTab.addUserTab(tabs, self.actor)
		self.layout.addWidget(tabs)

		self.setLayout(self.layout)
		self.resize(350, 300)

		self.collectElements()
		self.settings = utility.readSettings()
		self.applyLoadedSettings(self.settings)
		
		self.connectFunctions()
		#self.updateKudos()

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
		self.SizeRange: range_slider.RangeSlider = self.basic['SizeRange']
		self.seed: QLineEdit = self.basic['seed']
		self.model: QComboBox = self.basic['model']
		self.sampler: QComboBox = self.basic['sampler']
		self.numImages: QSpinBox = self.basic['numImages']
		self.steps: QSlider = self.basic['steps']
		self.highResFix: QCheckBox = self.basic['highResFix']
		self.prompt: QLineEdit = self.basic['prompt']
		self.negativePrompt: QLineEdit = self.basic['negativePrompt']
		self.postProcessing: QComboBox = self.basic['postProcessing']
		self.facefixer_strength: QSlider = self.basic['facefixer_strength']
		self.upscale: QComboBox = self.basic['upscale']
		self.statusDisplay: QLabel = self.basic['statusDisplay']
		self.cancelButton: QPushButton = self.basic['cancelButton']

		### Advanced ###
		self.CFG: QSlider = self.advanced['promptStrength'] #UPDATE THIS
		self.maxWait: QSlider = self.advanced['maxWait']
		self.clip_skip: QSlider = self.advanced['clip_skip']
		self.nsfw: QCheckBox = self.advanced['nsfw']
		self.karras: QCheckBox = self.advanced['karras']
		self.useRealInpaint: QCheckBox = self.advanced['useRealInpaint']

		### User ###
		self.apikey: QLineEdit = self.user['apikey']
		self.userID: QLineEdit = self.user['userID']
		self.kudos: QLineEdit = self.user['kudos']
		self.trusted: QLineEdit = self.user['trusted']
		self.concurrency: QLineEdit = self.user['concurrency']
		self.requests: QLineEdit = self.user['requests']
		self.contributions: QLineEdit = self.user['contributions']
		self.refreshUserButton: QPushButton = self.user['refreshUserButton']

	def connectFunctions(self):
		#User button connections
		self.generateButton.clicked.connect(self.generate)
		self.maskButton.clicked.connect(self.toggleMaskMode)
		self.img2imgButton.clicked.connect(self.img2imgGenerate)
		self.cancelButton.clicked.connect(self.reject)
		self.refreshUserButton.clicked.connect(self.refreshUser)

		#kudos update connections
		self.priceCheck.clicked.connect(self.updateKudos)
		self.denoise_strength.valueChanged.connect(self.updateKudos)
		self.SizeRange.sliderMoved.connect(self.updateKudos)
		self.sampler.currentTextChanged.connect(self.updateKudos)
		self.numImages.valueChanged.connect(self.updateKudos)
		self.steps.valueChanged.connect(self.updateKudos)
		self.postProcessing.currentTextChanged.connect(self.updateKudos)
		self.upscale.currentTextChanged.connect(self.updateKudos)

	def applyLoadedSettings(self, settings):
		self.denoise_strength.setValue(settings["denoise_strength"])
		self.seed.setText(settings["seed"])
		self.steps.setValue(settings["steps"])
		self.prompt.setText(settings["prompt"])
		self.negativePrompt.setText(settings["negativePrompt"])
		self.CFG.setValue(settings["promptStrength"])
		self.maxWait.setValue(settings["maxWait"])
		self.clip_skip.setValue(settings["clip_skip"])
		self.nsfw.setChecked(settings["nsfw"])
		self.karras.setChecked(settings["karras"])
		self.apikey.setText(settings["apikey"])

	def generate(self):
		self.actor.generate(False, False)
	
	def img2imgGenerate(self):
		self.actor.img2imgGenerate(True, self.maskMode)

	def toggleMaskMode(self, forceDisable = False):
		doc = utility.document()
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
		self.actor.worker.cancel()
		utility.writeSettings(self)

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
		prompt = self.prompt.toPlainText() + (" ### " + self.negativePrompt.toPlainText() if self.negativePrompt.toPlainText() != "" else "")
		
		#post processing = [] if 'None' otherwise get value
		post_processor = [self.postProcessing.currentText()] if self.postProcessing.currentText() != "None" else []
		upscaler = [self.upscale.currentText()] if self.upscale.currentText() != "None" else []
		post_process = post_processor + upscaler
		
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
			"prompt": prompt,
			"postProcessing": post_process,
			"facefixer_strength": self.facefixer_strength.value()/100,
			#advanced
			"CFG": self.CFG.value(),
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
			"shared": False,
			"replacement_filter": True
		}
	
	def getPayloadData(self):
		prompt = self.prompt.toPlainText() + (" ### " + self.negativePrompt.toPlainText() if self.negativePrompt.toPlainText() != "" else "")
		post_processor = [self.postProcessing.currentText()] if self.postProcessing.currentText() != "None" else []
		upscaler = [self.upscale.currentText()] if self.upscale.currentText() != "None" else []
		post_process = post_processor + upscaler
		params = {
			"sampler_name": self.sampler.currentText(),
			"cfg_scale": self.CFG.value(),
			"steps": int(self.steps.value()),
			"seed": self.seed.text(),
			"hires_fix": self.highResFix.isChecked(),
			"karras": self.karras.isChecked(),
			"post_processing": post_process,
			"facefixer_strength": self.facefixer_strength.value()/100,
			"clip_skip": self.clip_skip.value(),
			"n": self.numImages.value(),
		}

		data = {
			#append negative prompt only if it is not empty
			"prompt": prompt,
			"params": params,
			"nsfw": self.nsfw.isChecked(),
			"trust_workers": False,
			"slow_workers": True,
			"censor_nsfw": False,
			"r2": True,
			"models": [self.model.currentData()],
			"shared": False,
			"replacement_filter": True
		}

		return data
	
	def updateKudos(self):
		if utility.document() is None:
			return
		settings = self.getCurrentSettings()
		k = self.actor.calculateKudos(settings)
		self.generateButton.setText("Generate (" + str(k[0]) + " kudos)")
		if self.maskMode:
			self.img2imgButton.setText("Inpaint (" + str(k[1]) + " kudos)")
		else:
			self.img2imgButton.setText("Img2Img (" + str(k[1]) + " kudos)")

	def refreshUser(self):
		qDebug("Updating user info")
		#get user info from server with the find_user API call
		self.userInfo = hordeAPI.find_user(self.apikey.text())
		#update values from userInfo
		if self.userInfo:
			self.userID.setText(self.userInfo["username"])
			self.kudos.setText(str(self.userInfo["kudos"]))
			self.trusted.setText(str(self.userInfo["trusted"]))
			self.concurrency.setText(str(self.userInfo["concurrency"]))
			self.requests.setText(str(self.userInfo["records"]["request"]["image"]))
			self.contributions.setText(str(self.userInfo["records"]["fulfillment"]["image"]))
	
		#override
	def customEvent(self, ev):
		if ev.type() == self.actor.worker.eventId:
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