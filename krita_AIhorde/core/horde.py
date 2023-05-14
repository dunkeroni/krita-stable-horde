from krita import *
from PyQt5.QtCore import qDebug

import base64
import re

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

	def __init__(self, dialog):
		super(Worker, self).__init__()
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
		
		self.createStatusChecker() #start checking status of the job, repeats every CHECK_WAIT seconds
		return

	def createStatusChecker(self):
		#starts a threaded instance of an object that queries the status of the job
		#object will connect to the DisplayGenerated function when the job is finished
		#self.thread = QThread()
		self.checker = StatusChecker(self.id, self.maxWait)
		#self.checker.moveToThread(self.thread)
		#self.thread.started.connect(self.checker.checkStatus)
		self.checker.message.connect(self.checkerMessage) #updates the status block
		self.checker.done.connect(self.displayGenerated) #passes message result to display function
		#self.checker.finished.connect(self.thread.quit)
		#self.checker.finished.connect(self.checker.deleteLater)
		#self.thread.finished.connect(self.thread.deleteLater)

		qDebug("starting status checker thread...")
		#self.thread.start()
		self.checker.checkStatus()


	def cancel(self, message="Generation canceled."):
		self.cancelled = True
		self.pushEvent(message, utility.UpdateEvent.TYPE_FINISHED)

	@pyqtSlot(str)
	def checkerMessage(self, message: str):
		self.pushEvent(message)
