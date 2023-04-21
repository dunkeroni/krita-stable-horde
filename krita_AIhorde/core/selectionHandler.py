from PyKrita import * #fake import for IDE
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import json
import base64
from ..misc import utility
from ..core import hordeAPI, horde


def getI2Ibounds():
    qDebug("getI2Ibounds")
    #Returns an image of the current selection with width and height increased to the nearest multiple of 64
    doc = utility.document()
    selection = doc.selection()
    if selection is not None:
        qDebug("selection found")
        x = selection.x()
        y = selection.y()
        w = selection.width()
        h = selection.height()
        #correct bounds to a multiple of 64 centered on the existing selection
        dw = 64 - (w % 64)
        dh = 64 - (h % 64)
        x = min(0, x - dw/2)
        y = min(0, y- dh/2)
        w += dw
        h += dh
    else:
        #nothing is selected, so choose a 512x512 square in the middle of the document
        qDebug("no selection found, using default bounds")
        x = doc.width()/2 - 256
        y = doc.height()/2 - 256
        w = min(512, doc.width())
        h = min(512, doc.height())
    qDebug("Adjusted values[ x: %d, y: %d, w: %d, h: %d ]" % (x, y, w, h))
    return x, y, w, h


def getEncodedImageFromBounds(x, y, w, h):
    qDebug("getEncodedImageFromBounds")
    qDebug("Adjusted values[ x: %d, y: %d, w: %d, h: %d ]" % (x, y, w, h))
    #Returns a base64 encoded image for sending to the horde server
    doc = utility.document()
    bytes = doc.pixelData(x, y, w, h)
    image = QImage(bytes.data(), w, h, QImage.Format_RGBA8888).rgbSwapped()
    bytes = QByteArray()
    buffer = QBuffer(bytes)
    image.save(buffer, "WEBP")
    data = base64.b64encode(bytes.data())
    data = data.decode("ascii")
    return data


