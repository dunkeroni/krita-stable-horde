from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ..misc import utility

def addExperimentTab(tabs: QTabWidget, dialog):
    qDebug("Creating Experimental tab elements")
    experiment = {} #pointer to dictionary
    experimentTab = buildAdvancedTab(experiment, dialog)
    tabs.addTab(experimentTab, "Experimental")

    return experiment #dictionary of tab elements


def buildAdvancedTab(experiment, dialog):
    # ==============Advanced Tab================
    tabExperiment = QWidget()
    layout = QFormLayout()

    #Inpaint Mode QbuttonGroup - Img2Img PostMask, Img2Img PreMask, Img2Img DoubleMask, Inpaint Raw Mask
    inpaintMode = QButtonGroup()
    inpaintMode.setExclusive(True)
    postmask = QRadioButton("Img2Img PostMask")
    premask = QRadioButton("Img2Img PreMask")
    doublemask = QRadioButton("Img2Img DoubleMask")
    rawmask = QRadioButton("Inpaint Raw Mask")
    inpaintMode.addButton(postmask, 0)
    inpaintMode.addButton(premask, 1)
    inpaintMode.addButton(doublemask, 2)
    inpaintMode.addButton(rawmask, 3)
    inpaintMode.buttons()[2].setChecked(True)
    layoutV = QVBoxLayout()
    for button in inpaintMode.buttons():
        layoutV.addWidget(button)
    layout.addRow("Inpaint Mode", layoutV)
    experiment['inpaintMode'] = inpaintMode

    tabExperiment.setLayout(layout)
    return tabExperiment