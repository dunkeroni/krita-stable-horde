from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

def addResultsTab(tabs: QTabWidget, dialog):
    qDebug("Creating Results tab elements")
    results = {} #pointer to dictionary
    resultsTab = buildAdvancedTab(results, dialog)
    tabs.addTab(resultsTab, "Results")

    return results #dictionary of tab elements


def buildAdvancedTab(results, dialog):
    # ==============Advanced Tab================
    tabResults = QWidget()
    layout = QFormLayout()

    #dropdown menu for results groups
    groupSelector = QComboBox()
    layout.addRow("Layer", groupSelector)
    results['groupSelector'] = groupSelector

    #Previous and Next buttons
    prevResult = QPushButton("<<<")
    nextResult = QPushButton(">>>")
    layout.addRow(prevResult, nextResult)
    results['prevResult'] = prevResult
    results['nextResult'] = nextResult

    #Delete single button
    deleteButton = QPushButton("Delete")
    layout.addRow(deleteButton)
    results['deleteButton'] = deleteButton

    #Delete all others button
    deleteAllButton = QPushButton("Delete All Others")
    layout.addRow(deleteAllButton)
    results['deleteAllButton'] = deleteAllButton

    #Generation Info box
    genInfo = QTextEdit()
    genInfo.setReadOnly(True)
    layout.addRow(genInfo)
    results['genInfo'] = genInfo

    tabResults.setLayout(layout)
    return tabResults