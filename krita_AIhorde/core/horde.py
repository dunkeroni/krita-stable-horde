from krita import *
from PyQt5.QtCore import qDebug

import base64
import ssl
import threading
import urllib, urllib.request, urllib.error
import re

from ..misc import utility
from ..core import hordeAPI, selectionHandler

class Worker():
    CHECK_WAIT = 5

    def __init__(self, dialog):
        self.dialog = dialog
        self.canceled = False
        self.checkMax = None
        self.checkCounter = 0
        self.id = None
        self.eventId = QEvent.registerEventType()

    ssl._create_default_https_context = ssl._create_unverified_context

    def displayGenerated(self, images):
        for image in images:
            seed = image["seed"]

            if re.match("^https.*", image["img"]):
                response = urllib.request.urlopen(image["img"])
                bytes = response.read()
            else:
                bytes = base64.b64decode(image["img"])
                bytes = QByteArray(bytes)

            #selectionHandler.putImageIntoBounds(bytes, self.bounds, seed)
            selectionHandler.putImageIntoBounds(bytes, self.bounds, seed, self.initMask)
        self.pushEvent(str(len(images)) + " images generated.")
        utility.UpdateEvent(self.eventId, utility.UpdateEvent.TYPE_FINISHED)

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

    def generate(self, settings: dict, img2img = False, inpainting = False):
        #self.dialog = dialog
        self.checkCounter = 0
        self.cancelled = False
        self.id = None
        self.checkMax = (self.dialog.maxWait.value() * 60)/self.CHECK_WAIT
        self.initMask = None
        data: dict = settings["payloadData"]
        params: dict = data["params"]

        self.bounds = selectionHandler.getI2Ibounds(settings["minSize"], settings["maxSize"])
        [gw, gh] = self.bounds[2] #generation bounds already sized correctly and fit to multiple of 64
        params.update({"width": gw})
        params.update({"height": gh})

        if img2img:
            if inpainting:
                self.initMask = selectionHandler.getImg2ImgMask() #saved for later displaying
            init, mask = selectionHandler.getEncodedImageFromBounds(self.bounds, inpainting)#inpainting) inpainting removed for img2img workaround
            data.update({"source_image": init})
            data.update({"source_processing": "img2img"})
            params.update({"hires_fix": False})
            params.update({"denoising_strength": settings["denoise_strength"]})
            if inpainting:
                data.update({"source_mask": mask})
        #if inpainting: #implies img2img
            #data.update({"source_processing": "inpainting"})

        apikey = "0000000000" if settings["apikey"] == "" else settings["apikey"]
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
