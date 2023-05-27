from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ..misc import utility
import urllib.request, urllib.error, json, copy

def addExperimentTab(tabs: QTabWidget, dialog):
    qDebug("Creating Experimental tab elements")
    experiment = {} #pointer to dictionary
    experimentTab, loraSettings = buildLoRATab(experiment, dialog)
    tabs.addTab(experimentTab, "Experimental")

    return experiment, loraSettings #dictionary of tab elements


def buildLoRATab(experiment, dialog):
    # ==============Advanced Tab================
    tabExperiment = QWidget()
    tabExperiment.setFixedWidth(400)
    scrollArea = QScrollArea()
    layout = QVBoxLayout(scrollArea)
    #set width to 350
    #scrollArea.setMinimumWidth(350)
    #scrollArea.setFixedWidth(400)

    #get loras button
    getloras = QPushButton("Get LoRAs")
    #getLoRAS.clicked.connect(lambda: refreshLoRA())
    layout.addWidget(getloras)
    experiment["getLoRAS"] = getloras
    loraSettings = refreshLoRA(layout)

    tabExperiment.setLayout(layout)
    #add to scroll area
    scrollArea.setWidgetResizable(True)
    scrollArea.setWidget(tabExperiment)

    return scrollArea, loraSettings #tabExperiment

def getLoraList():
    qDebug("Getting LoRAS from Civitai")

    #10GB limit
    targetKB = 10 * 1024 * 1024
    totalKB = 0
    n = 0
    loraList = []
    nextURL = "https://civitai.com/api/v1/models?types=LORA&sort=Highest%20Rated"
    while (totalKB < targetKB) and (n < 50):
        n += 1 #escape condition
        qDebug(nextURL)
        response = urllib.request.urlopen(urllib.request.Request(url=nextURL, headers={'User-Agent': 'Mozilla/5.0'}))
        lorablob = json.loads(response.read())
        qDebug(str(len(lorablob["items"])) + " LoRAS")
        for lora in lorablob["items"]: #list of dicts of dicts of dicts
            info = {} #clear object reference
            file = lora["modelVersions"][0]["files"][0]
            #get filename left of . sparator
            name = str(file["name"].split(".")[0])
            #convert name to ascii
            name = name.encode("ascii", "ignore").decode()
            info["name"] = name
            qDebug(info["name"])
            description = lora["description"]
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
            info["description"] = description
            info["rating"] = lora["stats"]["rating"]
            info["size"] = file["sizeKB"]
            info["trainedWords"] = lora["modelVersions"][0]["trainedWords"]

            loraList.append(info)
            totalKB += file["sizeKB"]
            if totalKB >= targetKB:
                break
        nextURL = lorablob["metadata"]["nextPage"]
    
    qDebug("Got " + str(len(loraList)) + " LoRAS")

    return loraList

def refreshLoRA(layout: QFormLayout):
    qDebug("Refreshing LoRAS")
    loraList = getLoraList()
    loraSettings = []
    for lora in loraList:
        loraSettings.append(LoraSetting(lora, layout))
        #add to layout
        #layout.addWidget(loraSettings[-1].layout)

    return loraSettings

class LoraSetting():
    def __init__(self, lora, layout: QFormLayout):
        #self.widget = QWidget()
        self.layout = layout
        #self.layout.setWidget(self.widget)
        self.lora = lora

        qDebug("Adding controls for " + lora["name"])
        #add checkbox
        checkbox = QCheckBox()
        checkbox.setChecked(False)
        label = QLabel(lora["name"])
        #add to layout
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(checkbox) 
        Hlayout.addWidget(label)
        Hlayout.setAlignment(Qt.AlignLeft)
        lablecontainer = QWidget()
        lablecontainer.setLayout(Hlayout)
        self.layout.addWidget(lablecontainer)
        label.setToolTip(lora["description"])

        #add lineEdit for trained words
        lineEdit = QLineEdit(str(lora["trainedWords"]))
        lineEdit.setReadOnly(True)
        trainedWordslabel = QLabel("Trained Words:")
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(trainedWordslabel)
        Hlayout.addWidget(lineEdit)
        trainedWordscontainer = QWidget()
        trainedWordscontainer.setLayout(Hlayout)
        self.layout.addWidget(trainedWordscontainer)
        
        #add lineEdit for custom trigger word, default to name
        lineEdit = QLineEdit(lora["name"])
        triggerlabel = QLabel("Prompt Trigger:")
        Hlayout = QHBoxLayout()
        Hlayout.addWidget(triggerlabel)
        Hlayout.addWidget(lineEdit)
        triggercontainer = QWidget()
        triggercontainer.setLayout(Hlayout)
        self.layout.addWidget(triggercontainer)
        lineEdit.setText(lora["name"])

        #Add two strength sliders
        # Unet Strength
        unetStrength = QSlider(Qt.Orientation.Horizontal)
        unetStrength.setRange(0, 10)
        unetStrength.setTickInterval(1)
        unetStrength.setValue(10)
        labelUnetStrength = QLabel(str(unetStrength.value()/10))
        unetStrength.valueChanged.connect(lambda: labelUnetStrength.setText(str(unetStrength.value()/10)))
        l2US = QLabel("Unet Strength")
        layoutH = QHBoxLayout()
        layoutH.addWidget(l2US)
        layoutH.addWidget(unetStrength)
        layoutH.addWidget(labelUnetStrength)
        UScontainer = QWidget()
        UScontainer.setLayout(layoutH)
        self.layout.addWidget(UScontainer)

        # Text Encoder Strength
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 10)
        slider.setTickInterval(1)
        slider.setValue(10)
        textEncoderStrength = slider
        labelTextEncoderStrength = QLabel(str(textEncoderStrength.value()/10))
        textEncoderStrength.valueChanged.connect(lambda: labelTextEncoderStrength.setText(str(textEncoderStrength.value()/10)))
        l2CS = QLabel("Text Encoder Strength")
        layoutH = QHBoxLayout()
        layoutH.addWidget(l2CS)
        layoutH.addWidget(textEncoderStrength)
        layoutH.addWidget(labelTextEncoderStrength)
        CScontainer = QWidget()
        CScontainer.setLayout(layoutH)
        self.layout.addWidget(CScontainer)

        #connect show/hide to checkbox
        #label.setVisible(False)
        trainedWordscontainer.setVisible(False)
        triggercontainer.setVisible(False)
        UScontainer.setVisible(False)
        CScontainer.setVisible(False)
        
        #checkbox.stateChanged.connect(lambda: label.setVisible(checkbox.isChecked()))
        """checkbox.stateChanged.connect(lambda: lineEdit.setVisible(checkbox.isChecked()))
        checkbox.stateChanged.connect(lambda: triggerlabel.setVisible(checkbox.isChecked()))
        checkbox.stateChanged.connect(lambda: unetStrength.setVisible(checkbox.isChecked()))
        checkbox.stateChanged.connect(lambda: labelUnetStrength.setVisible(checkbox.isChecked()))
        checkbox.stateChanged.connect(lambda: l2US.setVisible(checkbox.isChecked()))
        checkbox.stateChanged.connect(lambda: textEncoderStrength.setVisible(checkbox.isChecked()))
        checkbox.stateChanged.connect(lambda: labelTextEncoderStrength.setVisible(checkbox.isChecked()))
        checkbox.stateChanged.connect(lambda: l2CS.setVisible(checkbox.isChecked()))"""
        checkbox.stateChanged.connect(lambda: triggercontainer.setVisible(checkbox.isChecked()))
        checkbox.stateChanged.connect(lambda: UScontainer.setVisible(checkbox.isChecked()))
        checkbox.stateChanged.connect(lambda: CScontainer.setVisible(checkbox.isChecked()))
        checkbox.stateChanged.connect(lambda: trainedWordscontainer.setVisible(checkbox.isChecked()))

        self.name = label.text()
        self.checkbox = checkbox
        self.trigger = lineEdit
        self.unetStrength = unetStrength
        self.textEncoderStrength = textEncoderStrength

