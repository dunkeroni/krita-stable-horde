from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

def addUserTab(tabs: QTabWidget):
    qDebug("Creating User tab elements")
    user = {} #pointer to dictionary
    advancedTab = buildUserTab(user)
    tabs.addTab(advancedTab, "User")

    return user #dictionary of tab elements


def buildUserTab(user):
    tabUser = QWidget()
    layout = QFormLayout()

    # API Key
    apikey = QLineEdit()
    #make the apikey text hidden
    apikey.setEchoMode(QLineEdit.Password)
    layout.addRow("API Key (optional)", apikey)
    user['apikey'] = apikey

    #user ID
    userID = QLineEdit()
    userID.setReadOnly(True)
    layout.addRow("User ID", userID)
    user['userID'] = userID

    #kudos
    kudos = QLineEdit()
    kudos.setReadOnly(True)
    layout.addRow("Kudos", kudos)
    user['kudos'] = kudos

    #trusted
    trusted = QLineEdit()
    trusted.setReadOnly(True)
    layout.addRow("Trusted", trusted)
    user['trusted'] = trusted

    #concurrency
    concurrency = QLineEdit()
    concurrency.setReadOnly(True)
    layout.addRow("Concurrency", concurrency)
    user['concurrency'] = concurrency

    # usage["requests"]
    requests = QLineEdit()
    requests.setReadOnly(True)
    layout.addRow("Requests", requests)
    user['requests'] = requests

    # usage["contributions"]
    contributions = QLineEdit()
    contributions.setReadOnly(True)
    layout.addRow("Contributions", contributions)
    user['contributions'] = contributions

    #add a refresh button
    refreshUserButton = QPushButton("Refresh")
    layout.addRow(refreshUserButton)
    user['refreshUserButton'] = refreshUserButton

    #preferred workers textbox
    preferredWorkers = QLineEdit()
    layout.addRow("Preferred Workers", preferredWorkers)
    user['preferredWorkers'] = preferredWorkers

    #updateUserInfo() #populate actual values if they exist

    tabUser.setLayout(layout)

    return tabUser