from krita import *
import re, base64
from ..core import hordeAPI, selectionHandler

"""ResultCollector Class Description:
The Result Collector will store references to krita nodes as well as image parameters for later reference.
(Possible to save into krita document file? Need to investigate.)

Expected actions by Horde.py:
	When Node is created with image result:
		Node + Parameters --> results Buffer

	When Request is completed:
		results Buffer --> results DB
		Group all nodes into new Node Group

Actions from Dialog interface:
- Select result group
- Rotate through results in group
- Delete specific result from group
- Delete all other results from group
- Copy prompt from result info
"""

class ResultCollector(QObject):
	def __init__(self, results: dict = None):
		super(ResultCollector, self).__init__()
		self.buffer = []
		self.DB = {}

		if results is not None:
			qDebug("ResultCollector: Loading from dict")
			self.groupSelector: QComboBox = results['groupSelector']
			self.nextResult: QPushButton = results['nextResult']
			self.prevResult: QPushButton = results['prevResult']
			self.deleteButton: QPushButton = results['deleteButton']
			self.deleteAllButton: QPushButton = results['deleteAllButton']
			self.genInfo: QTextEdit = results['genInfo']

			#connect qwidgets to functions
			self.nextResult.clicked.connect(self.changeNextResult)
			self.prevResult.clicked.connect(self.changePrevResult)
			self.deleteButton.clicked.connect(self.deleteIndex)
			self.deleteAllButton.clicked.connect(self.deleteAllOthers)
		
	@pyqtSlot(dict)
	def displayGenerated(self, displayInfo):
		qDebug("displayGenerated")
		images = displayInfo["generations"]
		bounds = displayInfo["bounds"]
		initMask = displayInfo["initMask"]
		doc = Krita.instance().activeDocument()
		for image in images:
			seed = image["seed"]

			if re.match("^https.*", image["img"]):
				bytes = hordeAPI.pullImage(image["img"])
			else:
				bytes = base64.b64decode(image["img"])
				bytes = QByteArray(bytes)

			#selectionHandler.putImageIntoBounds(bytes, self.bounds, seed)
			selectionHandler.putImageIntoBounds(bytes, bounds, seed, initMask)
			doc.waitForDone()
			#get the active node
			node = doc.activeNode()
			self.addBufferNode(node, {'seed': seed}) #add result node to the buffer

	@pyqtSlot(Node, dict)
	def addBufferNode(self, node: Node, info: dict):
		qDebug("addBufferNode")
		#add node and info to the buffer as a tuple
		self.buffer.append([node, info])
		qDebug("Added node to result buffer")
	
	def getBuffer(self):
		return self.buffer
	
	def setBuffer(self, buffer):
		self.buffer = buffer
	
	@pyqtSlot()
	def bufferToDB(self, id: str = None):
		try:
			qDebug("bufferToDB")
			nodeDict = {}
			for index in self.buffer:
				node: Node = self.buffer[index][0]
				nodeUID = node.uniqueId()
				qDebug("node found: " + nodeUID.toString())
				nodeDict[nodeUID] = {
					"node": node,
					"info": self.buffer[index][1],
					"UID": nodeUID
				}
			doc = Krita.instance().activeDocument()
			root = doc.rootNode()
			if id is None:
				id = "Group " + str(len(self.DB))
			gn = doc.createGroupLayer(id)
			for nodeUID in nodeDict:
				gn.addChildNode(nodeDict[nodeUID]['node'], None)
			root.addChildNode(gn, None)
			doc.setActiveNode(gn)

			self.DB[id]['index'] = 0 #set default index to first result
			self.DB[id]['results'] = nodeDict
		except Exception as e:
			qDebug("bufferToDB: " + str(e))
			raise e
		qDebug("Result buffer added to DB")
		self.buffer = set() #clear the buffer for the next generation
		self.groupSelector.addItem(id) #add the new group to the dropdown menu
		self.groupSelector.setCurrentText(id) #set the dropdown menu to the new group
		self.showOnlyIndex(0) #show only the first result
	
	def getRef(self): #standardize the way we get the current result
		if self.groupSelector.count() == 0:
			return None, None, None
		id = self.groupSelector.currentText()
		index = self.DB[id]['index']
		results = self.DB[id]['results']
		return id, index, results
	
	def changeNextResult(self):
		if self.groupSelector.count() == 0:
			return
		id, index, results = self.getRef()
		if index == len(results) - 1:
			index = 0
		else:
			index += 1
		self.DB[id]['index'] = index
		self.showOnlyIndex(index)
	
	def changePrevResult(self):
		if self.groupSelector.count() == 0:
			return
		id, index, results = self.getRef()
		if index == 0:
			index = len(results) - 1
		else:
			index -= 1
		self.DB[id]['index'] = index
		self.showOnlyIndex(index)
	
	def showOnlyIndex(self, newindex):
		if self.groupSelector.count() == 0:
			return
		id, index, results = self.getRef()
		doc = Krita.instance().activeDocument()
		for i, result in enumerate(results):
			node: Node = doc.nodeByUniqueID(result['UID'])
			if i == newindex:
				node.setVisible(True)
			else:
				node.setVisible(False)
	
	def deleteIndex(self):
		if self.groupSelector.count() == 0:
			return
		id, index, results = self.getRef()
		node: Node = results[index]['node']
		node.remove()
		del results[index]
		if index == len(results):
			index = 0
		self.DB[id]['index'] = index
		self.showOnlyIndex(index)

	def deleteAllOthers(self):
		if self.groupSelector.count() == 0:
			return
		id, index, results = self.getRef()
		doc = Krita.instance().activeDocument()
		for i, result in enumerate(results):
			node: Node = doc.nodeByUniqueID(result['UID'])
			if i != index:
				node.remove()
		self.showOnlyIndex(0)
	





