# v1.1.0

import base64
import json
import ssl
import threading
import urllib

from krita import *

VERSION = 110

class Stablehorde(Extension):
   def __init__(self, parent):
      super().__init__(parent)

   def setup(self):
      pass

   def createActions(self, window):
      action = window.createAction("generate", "Stablehorde", "tools/scripts")
      action.triggered.connect(self.openDialog)

   def openDialog(self):
      dialog = Dialog()
      dialog.exec()

class Dialog(QDialog):
   def __init__(self):
      super().__init__(None)
      global worker

      settings = self.readSettings()

      self.setWindowTitle("Stablehorde")
      self.layout = QFormLayout()

      # Generation Mode
      box = QGroupBox()
      self.modeText2Img = QRadioButton("Text -> Image")
      self.modeImg2Img = QRadioButton("Image -> Image")
      layoutV = QVBoxLayout()
      layoutV.addWidget(self.modeText2Img)
      layoutV.addWidget(self.modeImg2Img)
      box.setLayout(layoutV)
      label = QLabel("Generation Mode")
      label.setStyleSheet("QLabel{margin-top:12px;}")
      self.layout.addRow(label, box)

      group = QButtonGroup()
      group.addButton(self.modeText2Img, worker.MODE_TEXT2IMG)
      group.addButton(self.modeImg2Img, worker.MODE_IMG2IMG)
      group.button(settings["generationMode"]).setChecked(True)
      self.generationMode = group
      self.generationMode.buttonClicked.connect(self.handleModeChanged)

      # Init Strength
      slider = QSlider(Qt.Orientation.Horizontal, self)
      slider.setRange(0, 10)
      slider.setTickInterval(1)
      slider.setValue(settings["initStrength"])
      self.initStrength = slider
      labelInitStrength = QLabel(str(self.initStrength.value()/10))
      self.initStrength.valueChanged.connect(lambda: labelInitStrength.setText(str(self.initStrength.value()/10)))
      layout = QHBoxLayout()
      layout.addWidget(self.initStrength)
      layout.addWidget(labelInitStrength)
      container = QWidget()
      container.setLayout(layout)
      self.layout.addRow("Init Strength", container)

      if self.generationMode.checkedId() == worker.MODE_TEXT2IMG:
         self.initStrength.setEnabled(False)

      # Prompt Strength
      slider = QSlider(Qt.Orientation.Horizontal, self)
      slider.setRange(0, 20)
      slider.setTickInterval(1)
      slider.setValue(settings["promptStrength"])
      self.promptStrength = slider
      labelPromptStrength = QLabel(str(self.promptStrength.value()))
      self.promptStrength.valueChanged.connect(lambda: labelPromptStrength.setText(str(self.promptStrength.value())))
      layout = QHBoxLayout()
      layout.addWidget(self.promptStrength)
      layout.addWidget(labelPromptStrength)
      container = QWidget()
      container.setLayout(layout)
      self.layout.addRow("Prompt Strength", container)

      # Steps
      slider = QSlider(Qt.Orientation.Horizontal, self)
      slider.setRange(10, 200)
      slider.setTickInterval(1)
      slider.setValue(settings["steps"])
      self.steps = slider
      labelSteps = QLabel(str(self.steps.value()))
      self.steps.valueChanged.connect(lambda: labelSteps.setText(str(self.steps.value())))
      layout = QHBoxLayout()
      layout.addWidget(self.steps)
      layout.addWidget(labelSteps)
      container = QWidget()
      container.setLayout(layout)
      self.layout.addRow("Steps", container)

      # Seed
      self.seed = QLineEdit()
      self.seed.setText(settings["seed"])
      self.layout.addRow("Seed (optional)", self.seed)

      # NSFW
      self.nsfw = QCheckBox()
      self.nsfw.setCheckState(settings["nsfw"])
      self.layout.addRow("NSFW",self.nsfw)

      # Prompt
      self.prompt = QTextEdit()
      self.prompt.setText(settings["prompt"])
      self.layout.addRow("Prompt", self.prompt)

      # API Key
      self.apikey = QLineEdit()
      self.apikey.setText(settings["apikey"])
      self.layout.addRow("API Key (optional)", self.apikey)

      # Max Wait
      slider = QSlider(Qt.Orientation.Horizontal, self)
      slider.setRange(1, 5)
      slider.setTickInterval(1)
      slider.setValue(settings["maxWait"])
      self.maxWait = slider
      labelMaxWait = QLabel(str(self.maxWait.value()))
      self.maxWait.valueChanged.connect(lambda: labelMaxWait.setText(str(self.maxWait.value())))
      layout = QHBoxLayout()
      layout.addWidget(self.maxWait)
      layout.addWidget(labelMaxWait)
      container = QWidget()
      container.setLayout(layout)
      self.layout.addRow("Max Wait (minutes)", container)

      # Status
      self.statusDisplay = QTextEdit()
      self.statusDisplay.setReadOnly(True)
      self.layout.addRow("Status", self.statusDisplay)

      # Generate
      self.generateButton = QPushButton("Generate")
      self.generateButton.clicked.connect(self.generate)
      self.layout.addWidget(self.generateButton)

      # Space
      layout = QHBoxLayout()
      layout.addSpacing(50)
      container = QWidget()
      container.setLayout(layout)
      self.layout.addWidget(container)

      # Cancel
      cancelButton = QPushButton("Cancel")
      cancelButton.setFixedWidth(100)
      cancelButton.clicked.connect(self.reject)
      self.layout.addWidget(cancelButton)
      self.layout.setAlignment(cancelButton, Qt.AlignRight)

      self.setLayout(self.layout)
      self.resize(350, 300)

      update = utils.checkUpdate()

      if update["update"] is True:
         self.statusDisplay.setText(update["message"])

   def handleModeChanged(self):
      mode = self.generationMode.checkedId()

      if mode == worker.MODE_TEXT2IMG:
         self.initStrength.setEnabled(False)
      elif mode == worker.MODE_IMG2IMG:
         self.initStrength.setEnabled(True)

   def generate(self):
      mode = self.generationMode.checkedId()
      doc = Application.activeDocument()

      if doc is None:
         utils.errorMessage("Please open a document (check details).", "For image generation a document with size of 512x512, color model 'RGB/Alpha', color depth '8-bit integer' and a paint layer is needed.")
         return
      elif doc.width() != 512 or doc.height() != 512:
         utils.errorMessage("Please use a document with size 512x512 (check details).", "For image generation a document with size of 512x512, color model 'RGB/Alpha', color depth '8-bit integer' and a paint layer is needed.")
         return
      elif doc.colorModel() != "RGBA" or doc.colorDepth() != "U8":
         utils.errorMessage("Please use a document with 'RGB/Alpha' and '8-bit'", "For image generation a document with size of 512x512, color model 'RGB/Alpha', color depth '8-bit integer' and a paint layer is needed.")
         return
      elif mode == worker.MODE_IMG2IMG and worker.getInitNode() is None:
         utils.errorMessage("Please add a visible layer which shows the init image.", "For image generation in mode img -> img a visible layer, which shows the init image, is needed.")
         return
      else:
         self.writeSettings()
         self.setEnabledStatus(False)
         self.statusDisplay.setText("Waiting for generated image...")
         worker.generate(self)

   #override
   def customEvent(self, ev):
      if ev.type() == worker.eventId:
         if ev.updateType == UpdateEvent.TYPE_CHECKED:
            self.statusDisplay.setText(ev.message)
         elif ev.updateType == UpdateEvent.TYPE_TIMEOUT:
            self.statusDisplay.setText(ev.message)
            self.setEnabledStatus(True)
         elif ev.updateType == UpdateEvent.TYPE_ERROR:
            self.statusDisplay.setText("An error occurred: " + ev.message)
            self.setEnabledStatus(True)
         elif ev.updateType == UpdateEvent.TYPE_FINISHED:
            self.close()

   #override
   def reject(self):
      global worker
      worker.cancel()
      self.writeSettings()
      super().reject()

   def readSettings(self):
      defaults = {
         "generationMode": worker.MODE_TEXT2IMG,
         "initStrength": 3,
         "prompt": "",
         "promptStrength": 8,
         "steps": 50,
         "seed": "",
         "nsfw": 0,
         "apikey": "",
         "maxWait": 5
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

   def writeSettings(self):
      settings = {
         "generationMode": self.generationMode.checkedId(),
         "initStrength": self.initStrength.value(),
         "prompt": self.prompt.toPlainText(),
         "promptStrength": self.promptStrength.value(),
         "steps": int(self.steps.value()),
         "seed": self.seed.text(),
         "nsfw": self.nsfw.checkState(),
         "apikey": self.apikey.text(),
         "maxWait": self.maxWait.value()
      }

      try:
         settings = json.dumps(settings)
         Application.writeSetting("Stablehorde", "Config", settings)
      except Exception as ex:
         ex = ex

   def setEnabledStatus(self, status):
      self.modeText2Img.setEnabled(status)
      self.modeImg2Img.setEnabled(status)

      if self.generationMode.checkedId() == worker.MODE_IMG2IMG:
         self.initStrength.setEnabled(status)

      self.promptStrength.setEnabled(status)
      self.steps.setEnabled(status)
      self.seed.setEnabled(status)
      self.nsfw.setEnabled(status)
      self.prompt.setEnabled(status)
      self.apikey.setEnabled(status)
      self.maxWait.setEnabled(status)
      self.generateButton.setEnabled(status)

class Worker():
   API_ROOT = "https://stablehorde.net/api/v2/"
   CHECK_WAIT = 5
   MODE_TEXT2IMG = 1
   MODE_IMG2IMG = 2

   dialog = None
   checkMax = None
   checkCounter = 0
   id = None
   cancelled = False

   eventId = QEvent.registerEventType()

   ssl._create_default_https_context = ssl._create_unverified_context

   def getInitImage(self):
      doc = Application.activeDocument()
      nodeInit = self.getInitNode()

      if nodeInit is not None:
         bytes = nodeInit.pixelData(0, 0, doc.width(), doc.height())
         image = QImage(bytes.data(), doc.width(), doc.height(), QImage.Format_RGBA8888).rgbSwapped()
         bytes = QByteArray()
         buffer = QBuffer(bytes)
         image.save(buffer, "WEBP")
         data = base64.b64encode(bytes.data())
         data = data.decode("ascii")
         return data
      else:
         raise Exception("No layer with init image found.")

   def getInitNode(self):
      doc = Application.activeDocument()
      nodes = doc.topLevelNodes()

      nodeInit = None

      for node in nodes:
         if node.visible() is True:
            nodeInit = node

      return nodeInit

   def displayGenerated(self, images):
      for image in images:
         seed = image["seed"]
         bytes = base64.b64decode(image["img"])
         bytes = QByteArray(bytes)
         image = QImage()
         image.loadFromData(bytes, 'WEBP')
         ptr = image.bits()
         ptr.setsize(image.byteCount())

         doc = Application.activeDocument()
         root = doc.rootNode()
         node = doc.createNode("Stablehorde " + str(seed), "paintLayer")
         root.addChildNode(node, None)
         node.setPixelData(QByteArray(ptr.asstring()), 0, 0, image.width(), image.height())
         doc.waitForDone()
         doc.refreshProjection()

   def getImages(self):
      url = self.API_ROOT + "generate/status/" + self.id
      response = urllib.request.urlopen(url)
      data = response.read()
      data = json.loads(data)

      return data["generations"]

   def checkStatus(self):
      try:
         url = self.API_ROOT + "generate/check/" + self.id
         response = urllib.request.urlopen(url)
         data = response.read()
         data = json.loads(data)

         self.checkCounter = self.checkCounter + 1

         if self.checkCounter < self.checkMax and data["done"] == False and self.cancelled == False:
            if data["processing"] == 0:
               message = "Queue position: " + str(data["queue_position"]) + ", Wait time: " + str(data["wait_time"]) + "s"
            elif data["processing"] > 0:
               message = "Generating..."

            ev = UpdateEvent(worker.eventId, UpdateEvent.TYPE_CHECKED, message)
            QApplication.postEvent(self.dialog, ev)

            timer = threading.Timer(self.CHECK_WAIT, self.checkStatus)
            timer.start()
         elif self.checkCounter == self.checkMax and self.cancelled == False:
            minutes = (self.checkMax * self.CHECK_WAIT)/60

            message = "Image generation timed out after " + str(minutes) + " minutes. Please try it again later."
            ev = UpdateEvent(worker.eventId, UpdateEvent.TYPE_TIMEOUT, message)
            QApplication.postEvent(self.dialog, ev)
         elif data["done"] == True and self.cancelled == False:
            images = self.getImages()
            self.displayGenerated(images)

            ev = UpdateEvent(worker.eventId, UpdateEvent.TYPE_FINISHED)
            QApplication.postEvent(self.dialog, ev)

         return
      except Exception as ex:
         ev = UpdateEvent(worker.eventId, UpdateEvent.TYPE_ERROR, str(ex))
         QApplication.postEvent(self.dialog, ev)

   def generate(self, dialog):
      self.dialog = dialog
      self.checkCounter = 0
      self.cancelled = False
      self.id = None
      self.checkMax = (self.dialog.maxWait.value() * 60)/self.CHECK_WAIT

      try:
         nsfw = True if self.dialog.nsfw.isChecked() else False

         params = {
            "cfg_scale": self.dialog.promptStrength.value(),
            "height": 512,
            "width": 512,
            "steps": int(self.dialog.steps.value()),
            "seed": self.dialog.seed.text()
         }

         data = {
            "prompt": self.dialog.prompt.toPlainText(),
            "params": params,
            "nsfw": nsfw,
            "censor_nsfw": False
         }

         mode = self.dialog.generationMode.checkedId()

         if mode == worker.MODE_IMG2IMG:
            init = self.getInitImage()
            data.update({"source_image": init})
            params.update({"denoising_strength": (1 - self.dialog.initStrength.value()/10)})

         data = json.dumps(data).encode("utf-8")

         apikey = "0000000000" if self.dialog.apikey.text() == "" else self.dialog.apikey.text()
         headers = {"Content-Type": "application/json", "Accept": "application/json", "apikey": apikey}

         url = self.API_ROOT + "generate/async"

         request = urllib.request.Request(url=url, data=data, headers=headers)
         self.dialog.statusDisplay.setText("Waiting for generated image...")

         response = urllib.request.urlopen(request)
         data = response.read()

         try:
            data = json.loads(data)
            self.id = data["id"]
         except Exception as ex:
            raise Exception(data)

         self.checkStatus()
      except Exception as ex:
         ev = UpdateEvent(worker.eventId, UpdateEvent.TYPE_ERROR, str(ex))
         QApplication.postEvent(self.dialog, ev)

      return

   def cancel(self):
      self.cancelled = True

class Utils():
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
            url = "https://raw.githubusercontent.com/blueturtleai/krita-stable-diffusion/main/version.json"
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

class UpdateEvent(QEvent):
   TYPE_CHECKED = 0
   TYPE_ERROR = 1
   TYPE_TIMEOUT = 2
   TYPE_FINISHED = 3

   def __init__(self, eventId, updateType, message = ""):
      self.updateType = updateType
      self.message = message
      super().__init__(eventId)

Krita.instance().addExtension(Stablehorde(Krita.instance()))
utils = Utils()
worker = Worker()
#dialog = Dialog()
#dialog.exec()