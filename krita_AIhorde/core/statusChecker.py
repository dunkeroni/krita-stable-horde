from krita import *
from PyQt5.QtCore import qDebug

import threading
from ..core import hordeAPI

class StatusChecker(QObject):
	CHECK_WAIT = 5
	done = pyqtSignal(dict)
	finished = pyqtSignal()
	message = pyqtSignal(str)
	def __init__(self, id, timeout):
		super(StatusChecker, self).__init__()
		self.cancelled = False
		self.checkMax = timeout // self.CHECK_WAIT
		self.checkCounter = 0
		self.id = id

	def checkStatus(self):
		#get the status of the current generation
		qDebug("Checking status...")
		data = hordeAPI.generate_check(self.id)
		self.checkCounter = self.checkCounter + 1
		#escape conditions

		if not data:
			self.message.emit("Error calling Horde. Are you connected to the internet?")
			self.cancelled = True
		if not data["is_possible"]:
			self.message.emit("Currently no worker available to generate your image. Please try a different model or lower resolution.")
			self.cancelled = True
		if self.checkCounter >= self.checkMax:
			self.message.emit("Generation Fault: Image generation timed out after " + (self.checkMax * self.CHECK_WAIT)/60 + " minutes. Please try it again later.")
			self.cancelled = True
		
		#success - completed generation
		if self.cancelled == False and data["done"] == True:
			images = hordeAPI.generate_status(self.id) #self.getImages()
			self.message.emit("Generation completed.")
			self.done.emit(images)
			self.finished.emit()
			return
		
		if self.cancelled:
			self.message.emit("Generation cancelled.")
			self.finished.emit()
			return

		#pending condition, update progress
		if data["processing"] == 0:
			self.message.emit("Queue position: " + str(data["queue_position"]) + ", Wait time: " + str(data["wait_time"]) + "s")
		elif data["processing"] > 0:
			self.message.emit("Generating...\nWaiting: " + str(data["waiting"]) + "\nProcessing: " + str(data["processing"]) + "\nFinished: " + str(data["finished"]))

		timer = threading.Timer(self.CHECK_WAIT, self.checkStatus)
		timer.start()