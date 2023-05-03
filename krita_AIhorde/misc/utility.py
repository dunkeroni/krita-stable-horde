from krita import *
from PyQt5.QtCore import *

import json
import urllib, urllib.request
from ..frontend import widget

VERSION = 200
INPAINT_MASK_NAME = "Inpaint Mask"

def errorMessage(text, detailed):
   msgBox = QMessageBox()
   msgBox.setWindowTitle("AI Horde")
   msgBox.setText(text)
   msgBox.setDetailedText(detailed)
   msgBox.setStyleSheet("QLabel{min-width: 300px;}")
   msgBox.exec()

def document() -> Document:
   return Krita.instance().activeDocument()

def readSettings():
   defaults = {
      "denoise_strength": 30,
      "prompt": "",
      "negativePrompt": "",
      "promptStrength": 7,
      "steps": 20,
      "seed": "",
      "nsfw": True,
      "apikey": "",
      "maxWait": 5,
      "karras": True,
      "clip_skip": 1,
   }

   try:
      settings = Krita.instance().readSetting("Stablehorde", "Config", None)

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

def writeSettings(dialog: widget.Dialog):
   settings = {
      "denoise_strength": dialog.denoise_strength.value(),
      "prompt": dialog.prompt.toPlainText(),
      "negativePrompt": dialog.negativePrompt.toPlainText(),
      "promptStrength": dialog.CFG.value(),
      "steps": int(dialog.steps.value()),
      "seed": dialog.seed.text(),
      "nsfw": dialog.nsfw.checkState(),
      "apikey": dialog.apikey.text(),
      "maxWait": dialog.maxWait.value(),
      "karras": dialog.karras.checkState(),
      "clip_skip": dialog.clip_skip.value(),
   }
   qDebug("Settings saved to file")
   try:
      settings = json.dumps(settings)
      Krita.instance().writeSetting("Stablehorde", "Config", settings)
   except Exception as ex:
      ex = ex

def checkUpdate():
   try:
      url = "https://raw.githubusercontent.com/dunkeroni/krita-stable-horde/main/version.json"
      response = urllib.request.urlopen(url)
      data = response.read()
      data = json.loads(data)

      if VERSION < int(data["version"]):
         return {"update": True, "message": data["message"]}
      else:
         return {"update": False}
   except Exception as ex:
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

   def __init__(self, eventId, updateType, message = ""):
      self.updateType = updateType
      self.message = message
      super().__init__(eventId)

def deleteMaskNode():
   doc = document()
   if doc is None:
      return None
   maskNode = doc.nodeByName(INPAINT_MASK_NAME)
   if maskNode is not None:
      doc.setActiveNode(maskNode)
      Krita.instance().action('remove_layer').trigger()
      doc.waitForDone() #wait for the mask to be deleted, otherwise it leaves glitches in the img2img
      doc.refreshProjection()

def createMaskNode():
   doc = document()
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