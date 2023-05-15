from krita import *
from PyQt5.QtCore import qDebug

import base64
import re, time

from ..misc import utility
from ..core import hordeAPI, selectionHandler, resultCollector
from ..core.statusChecker import StatusChecker

class Worker(QObject): #QObject allows threaded running
	#inbound signal
	triggerGenerate = pyqtSignal(dict) #trigger the generate function

	#outbound signals
	enableGUI = pyqtSignal(bool) #enable/disable the main GUI
	statusUpdate = pyqtSignal(str) #update the status block
	generateDone = pyqtSignal() #return results node dictionary
	newBufferEntry = pyqtSignal(Node, dict) #add a new node to the buffer
	resultsReady = pyqtSignal(dict) #return results

	CHECK_WAIT = 5

	def __init__(self, dialog, statusBox = None):
		super(Worker, self).__init__()
		self.statusBox: QTextEdit = statusBox
		self.dialog = dialog
		self.canceled = False
		self.maxWait = 300
		self.checkCounter = 0
		self.id = None
		self.eventId = QEvent.registerEventType()
		self.triggerGenerate.connect(self.generate)

	@pyqtSlot(dict)
	def displayGenerated(self, data):
		doc = Krita.instance().activeDocument()
		images = data["generations"]
		for image in images:
			seed = image["seed"]

			if re.match("^https.*", image["img"]):
				bytes = hordeAPI.pullImage(image)
			else:
				bytes = base64.b64decode(image["img"])
				bytes = QByteArray(bytes)

			#selectionHandler.putImageIntoBounds(bytes, self.bounds, seed)
			if bytes is None:
				qDebug("ERROR: bytes is None")
				return
			selectionHandler.putImageIntoBounds(bytes, self.bounds, seed, self.initMask)
			doc.waitForDone()
			#get the active node
			#node = doc.activeNode()
			#qDebug("Adding node to buffer...")
			#self.newBufferEntry.emit(node, {'seed': seed}) #add result node to the buffer
			#qDebug("worker continuing...")
		self.dialog.setEnabledStatus(True)

	def pushEvent(self, message, eventType = utility.UpdateEvent.TYPE_CHECKED):
		#posts an event through a new UpdateEvent instance for the current multithreaded instance to provide status messages without crashing krita
		ev = utility.UpdateEvent(self.eventId, eventType, message)
		QApplication.postEvent(self.dialog, ev)

	def generate(self, settings: dict):
		img2img = settings["genImg2img"]
		inpainting = settings["genInpainting"]
		self.cancelled = False
		self.id = None
		self.maxWait = (settings["maxWait"] * 60)
		self.initMask = None
		data: dict = settings["payloadData"]
		params: dict = data["params"]

		self.bounds = selectionHandler.getI2Ibounds(settings["minSize"], settings["maxSize"])
		[gw, gh] = self.bounds[2] #generation bounds already sized correctly and fit to multiple of 64
		params.update({"width": gw})
		params.update({"height": gh})

		if img2img:
			if inpainting and (settings["inpaintMode"] == 0 or settings["inpaintMode"] == 2):
				self.initMask = selectionHandler.getImg2ImgMask() #saved for later displaying
			else:
				self.initMask = None
			init, mask = selectionHandler.getEncodedImageFromBounds(self.bounds, inpainting, settings['inpaintMode'])#inpainting) inpainting removed for img2img workaround
			data.update({"source_image": init})
			data.update({"source_processing": "img2img"})
			params.update({"hires_fix": False})
			params.update({"denoising_strength": settings["denoise_strength"]})
			if inpainting and settings["inpaintMode"] >= 1:
				data.update({"source_mask": mask})
		if inpainting and settings["inpaintMode"] == 3: #implies img2img
			data.update({"source_processing": "inpainting"})

		apikey = "0000000000" if settings["apikey"] == "" else settings["apikey"]
		#utility.errorMessage("generation info:", str(data))
		jobInfo = hordeAPI.generate_async(data, apikey) #submit request for async generation

		#jobInfo will only have a "message" field and no "id" field if the request failed
		if "id" in jobInfo:
			self.id = jobInfo["id"]
		else:
			self.cancel()
			utility.errorMessage("horde.generate() error", str(jobInfo))
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.checkStatus)
		self.checkStatus() #start checking status of the job, repeats every CHECK_WAIT seconds
		return

	def checkStatus(self, timeout = 300):
		#get the status of the current generation
		qDebug("Checking status...")
		data = hordeAPI.generate_check(self.id)
		self.checkCounter = self.checkCounter + 1
		self.checkMax = timeout // self.CHECK_WAIT
		self.checkCounter = 0
		#escape conditions

		if not data:
			self.pushEvent("Error calling Horde. Are you connected to the internet?")
			self.cancelled = True
		if not data["is_possible"]:
			self.pushEvent("Currently no worker available to generate your image. Please try a different model or lower resolution.")
			self.cancelled = True
		if self.checkCounter >= self.checkMax:
			self.pushEvent("Generation Fault: Image generation timed out after " + (self.checkMax * self.CHECK_WAIT)/60 + " minutes. Please try it again later.")
			self.cancelled = True
		
		#success - completed generation
		if self.cancelled == False and data["done"] == True:
			images = hordeAPI.generate_status(self.id) #self.getImages()
			self.pushEvent("Generation completed.")
			self.timer.stop() #stop the timer so it doesn't trigger forever
			self.displayGenerated(images)
			return
		
		if self.cancelled:
			self.pushEvent("Generation cancelled.")
			return

		#pending condition, update progress
		if data["processing"] == 0:
			self.pushEvent("Queue position: " + str(data["queue_position"]) + ", Wait time: " + str(data["wait_time"]) + "s")
		elif data["processing"] > 0:
			self.pushEvent("Generating...\nWaiting: " + str(data["waiting"]) + "\nProcessing: " + str(data["processing"]) + "\nFinished: " + str(data["finished"]))

		self.timer.start(self.CHECK_WAIT * 1000)


	def cancel(self, message="Generation canceled."):
		self.cancelled = True
		self.pushEvent(message, utility.UpdateEvent.TYPE_FINISHED)
