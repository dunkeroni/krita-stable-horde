from PyKrita import * #fake import for IDE

from krita import *

import base64
import json
import ssl
import threading
import urllib
import math
import re

from ..misc import utility

class Worker():
   API_ROOT = "https://stablehorde.net/api/v2/"
   CHECK_WAIT = 5
   MODE_TEXT2IMG = 1
   MODE_IMG2IMG = 2
   MODE_INPAINTING = 3

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
         if doc.selection() is not None:
            raise Exception("Selection has to be removed before creating init image.")

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

         if re.match("^https.*", image["img"]):
            response = urllib.request.urlopen(image["img"])
            bytes = response.read()
         else:
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

         if self.checkCounter < self.checkMax and data["done"] is False and self.cancelled is False:
            if data["is_possible"] is True:
               if data["processing"] == 0:
                  message = "Queue position: " + str(data["queue_position"]) + ", Wait time: " + str(data["wait_time"]) + "s"
               elif data["processing"] > 0:
                  message = "Generating..."

               ev = utility.UpdateEvent(self.eventId, utility.UpdateEvent.TYPE_CHECKED, message)
               QApplication.postEvent(self.dialog, ev)

               timer = threading.Timer(self.CHECK_WAIT, self.checkStatus)
               timer.start()
            else:
               self.cancelled = True
               message = "Currently no worker available to generate your image. Please try again later."
               ev = utility.UpdateEvent(self.eventId, utility.UpdateEvent.TYPE_INFO, message)
               QApplication.postEvent(self.dialog, ev)
         elif self.checkCounter == self.checkMax and self.cancelled == False:
            self.cancelled = True
            minutes = (self.checkMax * self.CHECK_WAIT)/60
            message = "Image generation timed out after " + str(minutes) + " minutes. Please try it again later."
            ev = utility.UpdateEvent(self.eventId, utility.UpdateEvent.TYPE_INFO, message)
            QApplication.postEvent(self.dialog, ev)
         elif data["done"] == True and self.cancelled == False:
            images = self.getImages()
            self.displayGenerated(images)

            ev = utility.UpdateEvent(self.eventId, utility.UpdateEvent.TYPE_FINISHED)
            QApplication.postEvent(self.dialog, ev)

         return
      except urllib.error.HTTPError as ex:
         try:
            data = ex.read()
            data = json.loads(data)

            if "message" in data:
               message = data["message"]
            else:
               message = str(ex)
         except Exception:
            message = str(ex)

         ev = utility.UpdateEvent(self.eventId, utility.UpdateEvent.TYPE_ERROR, message)
         QApplication.postEvent(self.dialog, ev)
      except Exception as ex:
         ev = utility.UpdateEvent(self.eventId, utility.UpdateEvent.TYPE_ERROR, str(ex))
         QApplication.postEvent(self.dialog, ev)

   def generate(self, dialog):
      self.dialog = dialog
      self.checkCounter = 0
      self.cancelled = False
      self.id = None
      self.checkMax = (self.dialog.maxWait.value() * 60)/self.CHECK_WAIT

      #post processing = [] if 'None' otherwise get value from dialog
      post_processor = [self.dialog.postProcessing.currentText()] if self.dialog.postProcessing.currentText() != "None" else []
      #same for upscaler
      upscaler = [self.dialog.upscale.currentText()] if self.dialog.upscale.currentText() != "None" else []
      #combine into a single list
      post_process = post_processor + upscaler

      try:
         nsfw = True if self.dialog.nsfw.isChecked() else False

         params = {
            "sampler_name": self.dialog.sampler.currentText(),
            "cfg_scale": self.dialog.promptStrength.value(),
            "steps": int(self.dialog.steps.value()),
            "seed": self.dialog.seed.text(),
            "hires_fix": self.dialog.highResFix.isChecked(),
            "karras": self.dialog.karras.isChecked(),
            "post_processing": post_process,
            "facefixer_strength": self.dialog.facefixer_strength.value()/100,
            "clip_skip": self.dialog.clip_skip.value(),
         }

         data = {
            #append negative prompt only if it is not empty
            "prompt": self.dialog.prompt.toPlainText() + (" ### " + self.dialog.negativePrompt.toPlainText() if self.dialog.negativePrompt.toPlainText() != "" else ""),
            "params": params,
            "nsfw": nsfw,
            "censor_nsfw": False,
            "r2": True,
            "models": [self.dialog.model.currentData()]
         }

         doc = Application.activeDocument()

         if doc.width() % 64 != 0:
            width = math.floor(doc.width()/64) * 64
         else:
            width = doc.width()

         if doc.height() % 64 != 0:
            height = math.floor(doc.height()/64) * 64
         else:
            height = doc.height()

         params.update({"width": width})
         params.update({"height": height})

         mode = self.dialog.generationMode.checkedId()

         if mode == self.MODE_IMG2IMG:
            init = self.getInitImage()
            data.update({"source_image": init})
            data.update({"source_processing": "img2img"})
            params.update({"hires_fix": False})
            params.update({"denoising_strength": self.dialog.denoise_strength.value()/100})
         elif mode == self.MODE_INPAINTING:
            init = self.getInitImage()
            models = ["stable_diffusion_inpainting"]
            data.update({"source_image": init})
            data.update({"source_processing": "inpainting"})
            data.update({"models": models})
            params.update({"hires_fix": False})

         data = json.dumps(data).encode("utf-8")

         apikey = "0000000000" if self.dialog.apikey.text() == "" else self.dialog.apikey.text()
         headers = {"Content-Type": "application/json", "Accept": "application/json", "apikey": apikey, "Client-Agent": "dunkeroni's crappy Krita plugin"}

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
      except urllib.error.HTTPError as ex:
         try:
            data = ex.read()
            data = json.loads(data)

            if "message" in data:
               message = data["message"]
            else:
               message = str(ex)
         except Exception:
            message = str(ex)

         ev = utility.UpdateEvent(self.eventId, utility.UpdateEvent.TYPE_ERROR, message)
         QApplication.postEvent(self.dialog, ev)
      except Exception as ex:
         ev = utility.UpdateEvent(self.eventId, utility.UpdateEvent.TYPE_ERROR, str(ex))
         QApplication.postEvent(self.dialog, ev)

      return

   def cancel(self):
      self.cancelled = True
