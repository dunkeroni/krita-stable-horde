from PyKrita import * #fake import for IDE

from krita import *

import json
import urllib

VERSION = 134

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