from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import urllib.request, urllib.error, json
from ..core.loraSetting import LoraSetting

def addLoraTab(tabs: QTabWidget, dialog):
    qDebug("Creating Experimental tab elements")
    loraWidgets = {} #pointer to dictionary
    loraTab, loraSettings = buildLoRATab(loraWidgets, dialog)
    tabs.addTab(loraTab, "LoRA")

    return loraSettings #dictionary of tab elements


def buildLoRATab(lora, dialog):
    # ==============Advanced Tab================
    tabLora = QWidget()
    tabLora.setFixedWidth(400)
    scrollArea = QScrollArea()
    layout = QVBoxLayout(scrollArea)
    loramessage = "PLEASE NOTE:\nLoRA is an experimental feature on the Horde right now.\nNot many workers are supporting it at this time.\nUntil it is more stable, you will likely only be able to generate \na few of the most popular models."
    layout.addWidget(QLabel(loramessage))
    try:
        loraSettings = getLoraList(layout)
    except urllib.error.URLError:
        loraSettings = []
        layout.addWidget(QLabel("Failed to get LoRAS from Civitai. Is the site down? Check your network connection and restart Krita."))

    tabLora.setLayout(layout)
    #add to scroll area
    scrollArea.setWidgetResizable(True)
    scrollArea.setWidget(tabLora)

    return scrollArea, loraSettings #tabExperiment

def getDefaultLoraList():
    url = "https://raw.githubusercontent.com/Haidra-Org/AI-Horde-image-model-reference/main/lora.json"
    try:
        response = urllib.request.urlopen(urllib.request.Request(url=url, headers={'User-Agent': 'Mozilla/5.0'}))
        defaultLoras = json.loads(response.read())
    except:
        return []
    return defaultLoras #list of ID numbers


def getLoraList(layout: QFormLayout):
    qDebug("Getting LoRAS from Civitai")

    #10GB limit
    targetKB = 10 * 1024 * 1024
    totalKB = 0
    n = 0
    loraList = []
    nextURL = "https://civitai.com/api/v1/models?types=LORA&sort=Highest%20Rated"
    while (totalKB < targetKB) and (n < 10):
        n += 1 #escape condition
        qDebug(nextURL)
        response = urllib.request.urlopen(urllib.request.Request(url=nextURL, headers={'User-Agent': 'Mozilla/5.0'}))
        lorablob = json.loads(response.read())
        qDebug(str(len(lorablob["items"])) + " LoRAS")

        for lora in lorablob["items"]: #list of dicts of dicts of dicts
            sett = LoraSetting(layout)

            sett.name = lora["name"].encode("ascii", "ignore").decode()
            file = lora["modelVersions"][0]["files"][0] #dict referencing latest version file
            #get filename left of . separator
            filename = str(file["name"].split(".")[0])
            #convert name to ascii
            sett.filename = filename.encode("ascii", "ignore").decode()
            qDebug(sett.name)
            sett.description = pruneDescription(lora["description"])
            sett.rating = lora["stats"]["rating"]
            sett.sizeKB = file["sizeKB"]
            sett.trainedWords = lora["modelVersions"][0]["trainedWords"]
            sett.id = str(lora["id"])

            sett.build() #create widgets and add them to the layout
            loraList.append(sett)

            totalKB += file["sizeKB"]
            if totalKB >= targetKB:
                break
        nextURL = lorablob["metadata"]["nextPage"]
    
    qDebug("Got " + str(len(loraList)) + " LoRAS")

    return loraList

def pruneDescription(description:str):
    if description is None:
        description = "No Description given."
    #strip description to ascii
    description = ''.join(i for i in description if ord(i)<128)
    #replace HTML paragraphs with newline
    description = description.replace("<p>", "\n")
    #find and remove all substrings bewteen < and >, including the brackets
    while "<" in description:
        start = description.find("<")
        end = description.find(">")
        #remove text between < and >
        description = description[:start] + description[end+1:]
    
    return description

"""
def refreshLoRA(layout: QFormLayout):
    qDebug("Refreshing LoRAS")
    loraList = getLoraList()
    loraSettings = []
    for lora in loraList:
        loraSettings.append(LoraSetting(lora, layout))

    return loraSettings
    """

