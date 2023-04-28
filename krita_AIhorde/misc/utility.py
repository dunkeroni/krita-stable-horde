from PyKrita import * #fake import for IDE
from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import json
import urllib, urllib.request

VERSION = 134

def errorMessage(text, detailed):
   msgBox = QMessageBox()
   msgBox.setWindowTitle("AI Horde")
   msgBox.setText(text)
   msgBox.setDetailedText(detailed)
   msgBox.setStyleSheet("QLabel{min-width: 300px;}")
   msgBox.exec()

def document() -> Document:
   #This function makes it so that only this file has warnings in the IDE. It's a hack, but it works, and it's pretty.
   return Application.activeDocument()

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

def writeSettings(dialog):
   settings = {
      "denoise_strength": dialog.denoise_strength.value(),
      "prompt": dialog.prompt.toPlainText(),
      "negativePrompt": dialog.negativePrompt.toPlainText(),
      "promptStrength": dialog.promptStrength.value(),
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
      Application.writeSetting("Stablehorde", "Config", settings)
   except Exception as ex:
      ex = ex

class Checker():
   updateChecked = False

   def errorMessage(self, text, detailed):
      msgBox = QMessageBox()
      msgBox.setWindowTitle("Stablehorde")
      msgBox.setText(text)
      msgBox.setDetailedText(detailed)
      msgBox.setStyleSheet("QLabel{min-width: 300px;}")
      msgBox.exec()

   def checkUpdate(self):
      if self.updateChecked is False:
         try:
            url = "https://raw.githubusercontent.com/dunkeroni/krita-stable-horde/main/version.json"
            response = urllib.request.urlopen(url)
            data = response.read()
            data = json.loads(data)

            self.updateChecked = True

            if VERSION < int(data["version"]):
               return {"update": True, "message": data["message"]}
            else:
               return {"update": False}
         except Exception as ex:
            return {"update": False}
      else:
         return {"update": False}

   def checkWebpSupport(self):
      formats = QImageReader.supportedImageFormats()
      found = False

      for format in formats:
         if format.data().decode("ascii").lower() == "webp":
            found = True
            break

      return found

class UpdateEvent(QEvent):
   TYPE_CHECKED = 0
   TYPE_ERROR = 1
   TYPE_INFO = 2
   TYPE_FINISHED = 3

   def __init__(self, eventId, updateType, message = ""):
      self.updateType = updateType
      self.message = message
      super().__init__(eventId)