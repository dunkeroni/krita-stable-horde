from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ..misc import utility

def addAdvancedTab(tabs: QTabWidget, dialog):
    qDebug("Creating Advanced tab elements")
    advanced = {} #pointer to dictionary
    advancedTab = buildAdvancedTab(advanced, dialog)
    tabs.addTab(advancedTab, "Advanced")

    return advanced #dictionary of tab elements


def buildAdvancedTab(advanced, dialog):
    # ==============Advanced Tab================
    tabAdvanced = QWidget()
    layout = QFormLayout()

    # Prompt Strength
    slider = QSlider(Qt.Orientation.Horizontal, dialog)
    slider.setRange(0, 20)
    slider.setTickInterval(1)
    promptStrength = slider
    labelPromptStrength = QLabel(str(promptStrength.value()))
    promptStrength.valueChanged.connect(lambda: labelPromptStrength.setText(str(promptStrength.value())))
    layoutH = QHBoxLayout()
    layoutH.addWidget(promptStrength)
    layoutH.addWidget(labelPromptStrength)
    container = QWidget()
    container.setLayout(layoutH)
    layout.addRow("CFG", container)
    advanced['promptStrength'] = promptStrength

    # Max Wait
    slider = QSlider(Qt.Orientation.Horizontal, dialog)
    slider.setRange(1, 5)
    slider.setTickInterval(1)
    maxWait = slider
    labelMaxWait = QLabel(str(maxWait.value()))
    maxWait.valueChanged.connect(lambda: labelMaxWait.setText(str(maxWait.value())))
    layoutH = QHBoxLayout()
    layoutH.addWidget(maxWait)
    layoutH.addWidget(labelMaxWait)
    container = QWidget()
    container.setLayout(layoutH)
    layout.addRow("Max Wait (minutes)", container)
    advanced['maxWait'] = maxWait

    #clip_skip slider
    slider = QSlider(Qt.Orientation.Horizontal, dialog)
    slider.setRange(1, 12)
    slider.setTickInterval(1)
    clip_skip = slider
    labelClipSkip = QLabel(str(clip_skip.value()))
    clip_skip.valueChanged.connect(lambda: labelClipSkip.setText(str(clip_skip.value())))
    layoutH = QHBoxLayout()
    layoutH.addWidget(clip_skip)
    layoutH.addWidget(labelClipSkip)
    container = QWidget()
    container.setLayout(layoutH)
    layout.addRow("Clip Skip (broken)", container)
    advanced['clip_skip'] = clip_skip
    
    # NSFW
    nsfw = QCheckBox()
    layout.addRow("NSFW",nsfw)
    advanced['nsfw'] = nsfw

    # Karras
    karras = QCheckBox()
    layout.addRow("Karras",karras)
    advanced['karras'] = karras

    # UseRealInpaint mode
    useRealInpaint = QCheckBox()
    useRealInpaint.setChecked(False)
    layout.addRow("Use Real Inpaint", useRealInpaint)
    advanced['useRealInpaint'] = useRealInpaint

    # Share with LAION
    shareWithLAION = QCheckBox()
    shareWithLAION.setChecked(False)
    layout.addRow("Share with LAION", shareWithLAION)
    advanced['shareWithLAION'] = shareWithLAION

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
    advanced['inpaintMode'] = inpaintMode

    #checkUpdates button
    checkUpdates = QPushButton("Check for Updates")
    checkUpdates.clicked.connect(utility.checkUpdate)
    layout.addRow(checkUpdates)

    tabAdvanced.setLayout(layout)
    return tabAdvanced