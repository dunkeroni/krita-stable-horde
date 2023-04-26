from PyKrita import * #fake import for IDE
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import json
import base64
from ..misc import utility
from ..core import hordeAPI, horde


def getI2Ibounds(minSize=512):
    qDebug("getI2Ibounds")
    #Returns an image of the current selection with width and height increased to the nearest multiple of 64 when scaled by minSize
    #Result will have the same top left corner of selection with the longer side extended to the nearest upscaled multiple of 64
    #IMPORTANT: Longer side is an integer and may not extend to an even multiple of 64. Need to check again when encoding.
    #bounds[0] is the original selection. bounds[1] is the adjusted selection to an aspect ratio that will fit generation. bounds[2] is the intended generation size.
    doc = utility.document()
    selection = doc.selection()
    bounds  = [[], [], []]
    if selection is not None:
        qDebug("selection found")
        x = selection.x()
        y = selection.y()
        w = selection.width()
        h = selection.height()
        bounds[0] = [x, y, w, h] #original selection bounds
        qDebug("Initial selection[ x: %d, y: %d, w: %d, h: %d ]" % (x, y, w, h))
        scaleFactor = minSize / (min(w, h))
        if w > h:
            gh = minSize
            gw = int(w * scaleFactor)
            gw += 64 - (gw % 64)
            w = gw // scaleFactor
            qDebug("Selection too small, expanding Width to " + str(w))
        else:
            gw = minSize
            gh = int(h * scaleFactor)
            gh += 64 - (gh % 64)
            h = gh // scaleFactor
            qDebug("Selection too small, expanding Height to " + str(h))
        #make sure x + w still fits within the document size
        x = min(x, doc.width() - w)
        #same for y
        y = min(y, doc.height() - h)
        bounds[1] = [x, y, w, h] #adjusted selection bounds
    else:
        #nothing is selected, so choose a 512x512 square in the middle of the document
        qDebug("no selection found, using default bounds")
        x = doc.width()/2 - minSize/2
        y = doc.height()/2 - minSize/2
        w = min(minSize, doc.width())
        h = min(minSize, doc.height())
        gw = (w // 64)*64
        gh = (h // 64)*64
        bounds[0] = bounds[1] = [x, y, w, h] #adjusted is default selection bounds
    qDebug("Adjusted values[ x: %d, y: %d, w: %d, h: %d ]" % (x, y, w, h))
    qDebug("Will scale and generate an image of %dx%d" % (gw, gh))
    bounds[2] = [gw, gh] #intended generation size
    return bounds


def getEncodedImageFromBounds(bounds):
    #Returns a scaled base64 encoded image for sending to the horde server
    qDebug("getEncodedImageFromBounds")
    [x, y, w, h] = bounds[1] #bounds[1] is the adjusted selection bounds
    [gw, gh] = bounds[2]
    qDebug("Values[ x: %d, y: %d, w: %d, h: %d ]" % (x, y, w, h))
    doc = utility.document()
    bytes = doc.pixelData(x, y, w, h)
    image = QImage(bytes.data(), w, h, QImage.Format_RGBA8888).rgbSwapped()
    image = image.scaled(gw, gh, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    qDebug("Upscaled image to %dx%d" % (gw, gh))
    bytes = QByteArray()
    buffer = QBuffer(bytes)
    image.save(buffer, "WEBP")
    data = base64.b64encode(bytes.data())
    data = data.decode("ascii")
    return data

def putImageIntoBounds(bytes, bounds, nametag="new generation"):
    try:
        qDebug("putImageIntoBounds")
        x, y, w, h = bounds[1] #bounds[1] is the adjusted selection bounds
        xs, ys, ws, hs = bounds[0] #bounds[0] is the original selection bounds
        gw, gh = bounds[2]
        qDebug("Reducing into [ x: %d, y: %d, w: %d, h: %d ] from generation of size %dx%d" % (x, y, w, h, gw, gh))
        image = QImage()
        image.loadFromData(bytes, 'WEBP')
        qDebug("Found image size is %dx%d. Resizing to selection bounds" % (image.width(), image.height()))
        image = image.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        qDebug("cropping to w: %d, h: %d" % (ws, hs))
        image = image.copy(0, 0, ws, hs)
        ptr = image.bits()
        ptr.setsize(image.byteCount())
        qDebug("adding node " + str(nametag) + "...")
        doc = utility.document()
        root = doc.rootNode()
        node = doc.createNode("Stablehorde " + str(nametag), "paintLayer")
        root.addChildNode(node, None)
        qDebug("node added")
        node.setPixelData(QByteArray(ptr.asstring()), x, y, ws, hs)
        qDebug("pixel data added")
    except:
        qDebug("failed to display image")
        raise Exception("Failed to display image. Something horrible happened instead.")
    doc.waitForDone()
    doc.refreshProjection()