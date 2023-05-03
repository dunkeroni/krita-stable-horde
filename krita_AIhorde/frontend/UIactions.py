from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import math

from ..frontend import widget
from ..core import horde, hordeAPI
from ..misc import utility, kudos

class UIActor():
	def __init__(self, dialog):
		self.dialog = dialog #save reference
		self.worker = horde.Worker() #create a new worker instance to handle requests
	
	def getSettings(self):
		return self.dialog.getCurrentSettings()

	def generate(self, img2img = False, inpainting = False):
		qDebug("Generating image from dialog call...")
		doc = utility.document()

		# no document
		if doc is None:
			utility.errorMessage("Please open a document. Please check details.", "For image generation a document with color model 'RGB/Alpha', color depth '8-bit integer' and a paint layer is needed.")
			return
		# document has invalid color model or depth
		elif doc.colorModel() != "RGBA" or doc.colorDepth() != "U8":
			utility.errorMessage("Invalid document properties. Please check details.", "For image generation a document with color model 'RGB/Alpha', color depth '8-bit integer' is needed.")
			return
		# no prompt
		elif len(self.dialog.prompt.toPlainText()) == 0:
			utility.errorMessage("Please enter a prompt.", "")
			return
		else:
			utility.writeSettings(self.dialog)
			self.dialog.setEnabledStatus(False)
			self.dialog.refreshUser() #doesn't work later in threaded instances, so might as well do it early
			self.dialog.statusDisplay.setText("Waiting for generated image...")
			self.worker.generate(self.dialog, img2img, inpainting)
	

	def img2imgGenerate(self):
		if utility.document().selection() is None:
			utility.errorMessage("Make a selection.", "Please select a region of the document before enaging Img2Img mode.")
			return
		self.generate(True, self.dialog.maskMode)
		self.dialog.toggleMaskMode(True)


	def calculateKudos(self, settings):
		doc = utility.document()
		if doc is None:
			return
		selection = doc.selection()
		if selection is None:
			width = height = settings["minSize"]
		else: #stimate gen size
			w = selection.width()
			h = selection.height()
			if max(w, h) > settings["maxSize"]:
				r =settings["maxSize"]/min(w, h)
			elif min(w, h) < settings["minSize"]:
				r = settings["minSize"]/max(w, h)
			else:
				r = 1
			width = math.ceil(w*r/64)*64
			height = math.ceil(h*r/64)*64

		kt = kudos.calculateKudos(width, height, settings["steps"], settings["sampler"],
			   False, False, settings["denoise_strength"], settings["postProcessing"],
			   False, settings["prompt"], settings["shared"])
		
		ki = kudos.calculateKudos(width, height, settings["steps"], settings["sampler"],
			   True, True, settings["denoise_strength"], settings["postProcessing"],
			   False, settings["prompt"], settings["shared"])
		
		txtKudos = round(kt*self.dialog.numImages.value(),2)
		imgKudos = round(ki*self.dialog.numImages.value(),2)

		return [txtKudos, imgKudos]