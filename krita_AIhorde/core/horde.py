from PyKrita import * #fake import for IDE
from krita import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import base64
import ssl
import threading
import urllib, urllib.request, urllib.error
import math
import re

from ..misc import utility
from ..core import hordeAPI, selectionHandler
from ..frontend import widget

class Worker():
    API_ROOT = "https://aihorde.net/api/v2/"
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
        doc = utility.document()
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

    def getInitNode(self) -> Node:
        #convert visible pixels into a new top layer node
        Krita.instance().action('new_from_visible').trigger() ##ISSUE: THIS BLOCK GETS CALLED TWICE ON IMG2IMG

        doc = utility.document()
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

            selectionHandler.putImageIntoBounds(bytes, self.bounds, seed)
        self.pushEvent(str(len(images)) + " images generated.")
        self.dialog.setEnabledStatus(True)
        self.dialog.updateUserInfo(self.dialog.apikey.text())


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
            images = hordeAPI.generate_status(self.id) #self.getImages()
            self.displayGenerated(images["generations"])
            self.pushEvent("Generation completed.", utility.UpdateEvent.TYPE_FINISHED)
            return

        #pending condition, check again
        if data["processing"] == 0:
            self.pushEvent("Queue position: " + str(data["queue_position"]) + ", Wait time: " + str(data["wait_time"]) + "s")
        elif data["processing"] > 0:
            self.pushEvent("Generating...\nWaiting: " + str(data["waiting"]) + "\nProcessing: " + str(data["processing"]) + "\nFinished: " + str(data["finished"]))

        timer = threading.Timer(self.CHECK_WAIT, self.checkStatus)
        timer.start()
        return

    def generate(self, dialog: widget.Dialog, img2img = False, inpainting = False):
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
            "n": self.dialog.numImages.value(),
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

        self.bounds = selectionHandler.getI2Ibounds(self.dialog.SizeRange.low()*64, self.dialog.SizeRange.high()*64)
        [gw, gh] = self.bounds[2] #generation bounds already sized correctly and fit to multiple of 64
        params.update({"width": gw})
        params.update({"height": gh})

        if img2img:
            init = selectionHandler.getEncodedImageFromBounds(self.bounds, inpainting)
            data.update({"source_image": init})
            data.update({"source_processing": "img2img"})
            params.update({"hires_fix": False})
            params.update({"denoising_strength": self.dialog.denoise_strength.value()/100})
        if inpainting: #implies img2img
            data.update({"source_processing": "inpainting"})

        apikey = "0000000000" if self.dialog.apikey.text() == "" else self.dialog.apikey.text()
        #utility.errorMessage("generation info:", str(data))
        jobInfo = hordeAPI.generate_async(data, apikey) #submit request for async generation

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
