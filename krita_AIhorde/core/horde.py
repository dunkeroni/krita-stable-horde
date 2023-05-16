from krita import *
from PyQt5.QtCore import qDebug

import base64
import re

from ..misc import utility
import threading
from ..core import hordeAPI, selectionHandler, resultCollector

class Worker():
	CHECK_WAIT = 5

	def __init__(self, dialog):
		super(Worker, self).__init__()
		self.dialog = dialog
		self.buffer = []
		self.canceled = False
		self.maxWait = 300
		self.checkCounter = 0
		self.id = None
		self.eventId = QEvent.registerEventType()

	def displayGenerated(self, images):
		doc = Krita.instance().activeDocument()
		for image in images:
			seed = image["seed"]
			if re.match("^https.*", image["img"]):
				bytes = hordeAPI.pullImage(image)
			else:
				bytes = base64.b64decode(image["img"])
				bytes = QByteArray(bytes)
			node: Node = selectionHandler.putImageIntoBounds(bytes, self.bounds, seed, self.initMask)
			if node is not None:
				self.buffer.append([node, {'seed': seed}]) #Buffer is List[List[node, dict]]

		self.pushEvent(str(len(images)) + " images generated.")
		utility.UpdateEvent(self.eventId, utility.UpdateEvent.TYPE_FINISHED)
		self.pushEvent(self.buffer, utility.UpdateEvent.TYPE_RESULTS) #push nodes to result collector
		self.buffer = [] #clear buffer

	def pushEvent(self, message, eventType = utility.UpdateEvent.TYPE_CHECKED):
		#posts an event through a new UpdateEvent instance for the current multithreaded instance to provide status messages without crashing krita
		ev = utility.UpdateEvent(self.eventId, eventType, message)
		QApplication.postEvent(self.dialog, ev)


	def checkStatus(self):
		#get the status of the current generation
		qDebug("Checking status...")
		data = hordeAPI.generate_check(self.id)
		self.checkCounter = self.checkCounter + 1

		#escape conditions
		if self.cancelled:
			self.pushEvent("Generation cancelled.", utility.UpdateEvent.TYPE_CANCELLED)
			qDebug("Generation cancelled.")
			return
		if not data:
			self.cancel("Error calling Horde. Are you connected to the internet?")
			return
		if not data["is_possible"]:
			self.cancel("Currently no worker available to generate your image. Please try a different model or lower resolution.")
			return
		if self.checkCounter >= self.checkMax:
			self.cancel("Generation Fault: Image generation timed out after " + (self.checkMax * self.CHECK_WAIT)/60 + " minutes. Please try it again later.")
			return
		
		#success - completed generation
		if data["done"] == True and self.cancelled == False:
			images = hordeAPI.generate_status(self.id)
			self.displayGenerated(images["generations"])
			self.pushEvent("Generation completed.", utility.UpdateEvent.TYPE_FINISHED)
			return

		#pending condition, check again
		if data["processing"] == 0:
			self.pushEvent("Queue position: " + str(data["queue_position"]) + ", Wait time: " + str(data["wait_time"]) + "s")
		elif data["processing"] > 0:
			self.pushEvent("Generating...\nWaiting: " + str(data["waiting"]) + "\nProcessing: " + str(data["processing"]) + "\nFinished: " + str(data["finished"]))

		"""NOTE TO FUTURE SELF:
		Functions being called by PyQT5's signals and slots handle threading differently.
		Even if the object is not sectioned into its own thread, the function will be called in its own thread-safe environment.
		This environement will not respect state alignments like document.waitForDone() and cannot correctly add child nodes to new nodes.
		As a result, attempting to display nodes and apply transparency masks will not work if A.B.connect(function) is used in the pipeline.

		Default Python threading is ok, but it does force up-level data passes to go through events which is messy.
		"""
		timer = threading.Timer(self.CHECK_WAIT, self.checkStatus)
		timer.start() #Initiate this check again later, until then the thread is free to do other things

	def generate(self, settings: dict):
		self.checkMax = (settings["maxWait"] * 60)/self.CHECK_WAIT
		self.checkCounter = 0
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
		jobInfo = hordeAPI.generate_async(data, apikey) #submit request for async generation
		if jobInfo == {}:
			self.cancel("Error calling Horde. Are you connected to the internet?")
			return

		#jobInfo will only have a "message" field and no "id" field if the request failed
		if "id" in jobInfo:
			self.id = jobInfo["id"]
		else:
			self.cancel()
			utility.errorMessage("horde.generate() error", str(jobInfo))
		
		self.checkStatus() #start checking status of the job, repeats every CHECK_WAIT seconds
		return

	def cancel(self, message="Generation canceled."):
		self.cancelled = True
		self.pushEvent(message, utility.UpdateEvent.TYPE_FINISHED)
