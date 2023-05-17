from krita import * #fake import for IDE
from PyQt5.QtCore import qDebug
import math

import base64
from ..misc import utility


def limitBounds(w, h, minSize, maxSize):
    qDebug("limitBounds")
    
    if min(w, h) < minSize: #correct to minimum size
        scaleFactor = minSize / (min(w, h))
        if w < h: #expand by width, increase height to next 64 multiple
            gw = minSize
            gh = 64 * math.ceil((h * scaleFactor) / 64)
            h1 = gh // scaleFactor
            w1 = w
            qDebug("Selection too small, expanding")
        else: #expand by height, increase width to next 64 multiple
            gh = minSize
            gw = 64 * math.ceil((w * scaleFactor) / 64)
            w1= gw // scaleFactor
            h1 = h
            qDebug("Selection too small, expanding")
    elif max(w, h) > maxSize: #correct to maximum size
        scaleFactor = maxSize / (max(w, h))
        if w > h: #shrink by width, increase height to next 64 multiple
            gw = maxSize
            gh = 64 * math.ceil((h * scaleFactor) / 64)
            h1 = gh // scaleFactor
            w1 = w
            qDebug("Selection too large, shrinking")
        else: #shrink by height, increase width to next 64 multiple
            gh = maxSize
            gw = 64 * math.ceil((w * scaleFactor) / 64)
            w1 = gw // scaleFactor
            h1 = h
            qDebug("Selection too large, shrinking")
    else: #no limit correction applied, scale up towards nearest multiple of 64 on both
        qDebug("increasing selection to nearest 64 multiples")
        gw = w
        gh = h
        if gw % 64 != 0:
            gw = 64 * ((w // 64) + 1)
        if gh % 64 != 0:
            gh = 64 * ((h // 64) + 1)
        w1 = gw
        h1 = gh
    
    qDebug("gw: " + str(gw) + " gh: " + str(gh))
    if gw > gh: #increase longer side of selection to next increment
        gw += 64
    else:
        gh += 64
    
    return [w1, h1, gw, gh]

def getI2Ibounds(minSize=512, maxSize = 1536):
    qDebug("getI2Ibounds")
    #Returns an image of the current selection with width and height increased to the nearest multiple of 64 when scaled by minSize
    #Result will have the same top left corner of selection with the longer side extended to the nearest upscaled multiple of 64
    #IMPORTANT: Longer side is an integer and may not extend to an even multiple of 64. Need to check again when encoding.
    #bounds[0] is the original selection. bounds[1] is the adjusted selection to an aspect ratio that will fit generation. bounds[2] is the intended generation size.
    doc = Krita.instance().activeDocument()
    selection = doc.selection()
    bounds  = [[], [], []]
    if selection is not None:
        qDebug("selection found")
        x = selection.x()
        y = selection.y()
        w = selection.width()
        h = selection.height()
        bounds[0] = [x, y, w, h] #original selection bounds
        w1, h1, gw, gh = limitBounds(w, h, minSize, maxSize)

        #make sure the adjusted seleciton still fits within the document size
        x1 = min(x, doc.width() - w1)
        y1 = min(y, doc.height() - h1)
        bounds[1] = [x1, y1, w1, h1] #adjusted selection bounds
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
    bounds = [list( map(int,i) ) for i in bounds]
    return bounds


def getEncodedImageFromBounds(bounds, inpainting = False, inpaintMode = 0):
    #Returns a scaled base64 encoded image for sending to the horde server
    qDebug("getEncodedImageFromBounds")
    [x, y, w, h] = bounds[1] #bounds[1] is the adjusted selection bounds
    [gw, gh] = bounds[2]
    qDebug("Values[ x: %d, y: %d, w: %d, h: %d ]" % (x, y, w, h))
    doc = Krita.instance().activeDocument()
    mask = mdata = None

    if inpainting:
        qDebug("Inpainting, using selection bounds")
        maskNode = doc.nodeByName(utility.INPAINT_MASK_NAME)
        if maskNode is None:
            inpainting = False
            qDebug("No inpainting mask found. Did you delete?")
        else:
            qDebug("Found inpainting mask")
            maskbytes = maskNode.pixelData(x, y, w, h)
            mask = QImage(maskbytes.data(), w, h, QImage.Format_RGBA8888)
            utility.deleteMaskNode()
            doc.waitForDone()

    bytes = doc.pixelData(x, y, w, h)
    image = QImage(bytes.data(), w, h, QImage.Format_RGBA8888).rgbSwapped()
    if inpainting and inpaintMode != 3: #CHECKME: masking results is different in Comfy worker versions
        mask.invertPixels(QImage.InvertRgba)
        qDebug("Set alpha channel to mask layer")
    image = image.scaled(gw, gh, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    qDebug("Upscaled image to %dx%d" % (gw, gh))
    bytes = QByteArray()
    buffer = QBuffer(bytes)
    image.save(buffer, "WEBP")
    data = base64.b64encode(bytes.data())
    data = data.decode("ascii")

    mbytes = QByteArray()
    mbuffer = QBuffer(mbytes)
    mask.save(mbuffer, "WEBP")
    mdata = base64.b64encode(mbytes.data())
    mdata = mdata.decode("ascii")
    return data, mdata

def getImg2ImgMask():
    qDebug("getImg2ImgMask")
    doc = Krita.instance().activeDocument()
    maskNode = doc.nodeByName(utility.INPAINT_MASK_NAME)
    if maskNode is None:
        qDebug("No inpainting mask found. Did you delete?")
        return None
    else:
        qDebug("Mask layer found. Will apply to result.")
        mask = maskNode.duplicate() 
        return mask 

def putImageIntoBounds(bytes, bounds, nametag="new generation", groupNode = None, mask = None):
    try:
        qDebug("putImageIntoBounds: " + str(bounds))
        x, y, w, h = bounds[1] #bounds[1] is the adjusted selection bounds
        xs, ys, ws, hs = bounds[0] #bounds[0] is the original selection bounds
        gw, gh = bounds[2]
        qDebug("Reducing into [ x: %d, y: %d, w: %d, h: %d ] from generation of size %dx%d" % (x, y, w, h, gw, gh))
        image = QImage()
        image.loadFromData(bytes, 'WEBP')
        qDebug("Found image size is %dx%d. Resizing to selection bounds" % (image.width(), image.height()))
        
        image = image.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        qDebug("cropping to w: %d, h: %d" % (ws, hs))
        image = image.copy(xs - x, ys - y, ws, hs)
        ptr = image.bits()
        ptr.setsize(image.byteCount())
        doc = Krita.instance().activeDocument()
        if groupNode is None:
            root = doc.rootNode()
        else:
            root = groupNode
        resultNode: GroupLayer = doc.createGroupLayer(nametag + " result")
        root.addChildNode(resultNode, None)
        doc.setActiveNode(resultNode)
        doc.waitForDone()
        node = doc.createNode("Stablehorde " + str(nametag), "paintLayer")
        resultNode.addChildNode(node, None)
        qDebug("node added: " + str(nametag))
        node.setPixelData(QByteArray(ptr.asstring()), xs, ys, ws, hs)
        qDebug("pixel data added")

        thisMask = None #will be returned if inpainting is not used
        if mask is not None:
            qDebug("Applying inpainting mask")
            thisMask: Node = mask.duplicate() #necessary if there were multiple generations
            resultNode.addChildNode(thisMask, node)
            doc.setActiveNode(thisMask)
            doc.waitForDone()
            Krita.instance().action('convert_to_transparency_mask').trigger()
        
        return resultNode, thisMask
            
    except:
        qDebug("failed to display image")
        raise Exception("Failed to display image. Something horrible happened instead.")
        return None