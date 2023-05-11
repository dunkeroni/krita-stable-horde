from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

def addResultsTab(tabs: QTabWidget, dialog):
    qDebug("Creating Experimental tab elements")
    results = {} #pointer to dictionary
    resultsTab = buildAdvancedTab(results, dialog)
    tabs.addTab(resultsTab, "Experimental")

    return results #dictionary of tab elements


def buildAdvancedTab(results, dialog):
    # ==============Advanced Tab================
    tabResults = QWidget()
    layout = QFormLayout()

    #dropdown menu for results groups

    #Previous and Next buttons

    #Delete single button

    #Delete all others button

    #Generation Info box

    tabResults.setLayout(layout)
    return tabResults