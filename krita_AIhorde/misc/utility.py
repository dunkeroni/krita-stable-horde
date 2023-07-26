from krita import *
from PyQt5.QtCore import *

import json
import urllib, urllib.request
from ..misc import version

INPAINT_MASK_NAME = "Inpaint Mask"

def errorMessage(text, detailed):
	msgBox = QMessageBox()
	msgBox.setWindowTitle("AI Horde")
	msgBox.setText(text)
	msgBox.setDetailedText(detailed)
	msgBox.setStyleSheet("QLabel{min-width: 300px;}")
	msgBox.exec()

def readSettings():
	defaults = {
		"denoise_strength": 30, #divides by 100
		"prompt": "",
		"negativePrompt": "",
		#"CFG": 28, #divides by 4
		"steps": 20,
		"seed": "",
		"nsfw": True,
		"apikey": "",
		"maxWait": 5,
		"karras": True,
		"clip_skip": 1,
		"shared": False,
	}

	try:
		settings = Krita.instance().readSetting("Stablehorde", "Config", None)

		if not settings:
			settings = defaults
		else:
			settings = json.loads(settings)

		for key in defaults:
			if not key in settings:
				settings[key] = defaults[key]
				break
	except Exception as ex:
		settings = defaults

	return settings

def writeSettings(dialogSettings: dict):
	settings = {
		"denoise_strength": dialogSettings["denoise_strength"],
		"prompt": dialogSettings["prompt"],
		"negativePrompt": dialogSettings["negativePrompt"],
		#"CFG": dialogSettings["CFG"],
		"steps": dialogSettings["steps"],
		"seed": dialogSettings["seed"],
		"nsfw": dialogSettings["nsfw"],
		"apikey": dialogSettings["apikey"],
		"maxWait": dialogSettings["maxWait"],
		"karras": dialogSettings["karras"],
		"clip_skip": dialogSettings["clip_skip"],
		"shared": dialogSettings["shared"],
	}
	qDebug("Settings saved to file")
	try:
		settings = json.dumps(settings)
		Krita.instance().writeSetting("Stablehorde", "Config", settings)
	except Exception as ex:
		ex = ex

def checkUpdate():
	try:
		url = "https://raw.githubusercontent.com/dunkeroni/krita-stable-horde/main/krita_AIhorde/misc/version.py"
		response = urllib.request.urlopen(url)
		data: str = response.read().decode('utf-8')
		remoteVersion = int(data.replace("VERSION = ", ""))
		qDebug("Remote version: " + str(remoteVersion))
		qDebug("Local version: " + str(version.VERSION))
		if remoteVersion > version.VERSION:
			errorMessage("New version of the AI Horde plugin is available.", "Please update at: https://github.com/dunkeroni/krita-stable-horde")
			return {"update": True, "message": "New version of the AI Horde plugin is available. Please update at: https://github.com/dunkeroni/krita-stable-horde"}
		else:
			return {"update": False}
	except Exception as ex:
		qDebug("Update check failed: " + str(ex))
		return {"update": False}

def checkWebpSupport():
	formats = QImageReader.supportedImageFormats()
	found = False

	for format in formats:
		if format.data().decode("ascii").lower() == "webp":
			found = True
			break

	return found

class UpdateEvent(QEvent): #used to create status messages from threaded functions
	TYPE_CHECKED = 0
	TYPE_ERROR = 1
	TYPE_INFO = 2
	TYPE_FINISHED = 3
	TYPE_RESULTS = 4

	def __init__(self, eventId, updateType, message = ""):
		self.updateType = updateType
		self.message = message
		super().__init__(eventId)

def deleteMaskNode():
	doc = Krita.instance().activeDocument()
	if doc is None:
		return None
	maskNode = doc.nodeByName(INPAINT_MASK_NAME)
	if maskNode is not None:
		doc.setActiveNode(maskNode)
		Krita.instance().action('remove_layer').trigger()
		doc.waitForDone() #wait for the mask to be deleted, otherwise it leaves glitches in the img2img
		doc.refreshProjection()

def createMaskNode():
	doc = Krita.instance().activeDocument()
	if doc is None:
		return None
	maskNode = doc.nodeByName(INPAINT_MASK_NAME)
	if maskNode is not None:
		qDebug("Mask node already exists, deleting...")
		deleteMaskNode() #get rid of existing mask node
	maskNode = doc.createNode(INPAINT_MASK_NAME, "paintlayer")
	doc.rootNode().addChildNode(maskNode, None)
	qDebug("Created mask node.")
	return maskNode