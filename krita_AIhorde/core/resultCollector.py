from krita import *
import re, base64
from ..core import hordeAPI, selectionHandler
from PyQt5.QtCore import qDebug

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

class ResultCollector():
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

	def addBufferNode(self, node: Node, info: dict):
		"""BUFFER FORMAT:
		Buffer = [
		[node, dict], [node, dict], ...
		]"""
		qDebug("addBufferNode")
		#add node and info to the buffer as a tuple
		self.buffer.append([node, info])
		qDebug("Added node to result buffer")
	
	def getBuffer(self):
		return self.buffer
	
	def setBuffer(self, buffer):
		self.buffer = buffer
	
	def bufferToDB(self, id: str = None):
		"""DB FORMAT:
		DB = {
		"groupID1": {
			"groupLayer": nodeUID,
			"index": int,
			"results": {
				"nodeUID": {
					"node": Node,
					"info": dict,
					"UID": nodeUID
				},
				"nodeUID": {
					"node": Node,
					"info": dict,
					"UID": nodeUID
				},
				...
			}
		"groupID2": {
			...
			}
		}
		"""
		try:
			qDebug("bufferToDB")
			resultsDict = {}
			for result in self.buffer["results"]:
				node: Node = result[0]
				nodeUID = node.uniqueId()
				qDebug("node found: " + nodeUID.toString())
				resultsDict[nodeUID.toString()] = {
					"node": node,
					"mask": result[1],
					"bounds": result[2],
					"info": result[3],
					"UID": nodeUID
				}
			doc = Krita.instance().activeDocument()
			root = doc.rootNode()
			if id is None:
				id = "Group " + str(len(self.DB))
			#qDebug("Creating group layer")
			gn = doc.createGroupLayer(id)
			#qDebug("Adding group layer to root")
			#root.addChildNode(gn, None)
			#doc.setActiveNode(gn)
			#doc.waitForDone()
			self.DB[id] = {} #create new group in DB
			self.DB[id]['groupLayer'] = gn.uniqueId() #store the group layer reference
			self.DB[id]['index'] = 0 #set default index to first result
			self.DB[id]['results'] = resultsDict

			qDebug("Result buffer added to DB")
			self.buffer = set() #clear the buffer for the next generation
			self.groupSelector.addItem(id) #add the new group to the dropdown menu
			self.groupSelector.setCurrentText(id) #set the dropdown menu to the new group
			self.showOnlyIndex(0) #show only the first result
			return
			gn: GroupLayer = self.buffer["groupLayer"]
			for result in resultsDict:
				node = resultsDict[result]['node']
				mask: Node = resultsDict[result]['mask']
				if mask is not None:
					xs, ys, ws, hs = resultsDict[result]["bounds"][0]
					maskbytes = mask.pixelData(xs, ys, ws, hs)
					maskImage = QImage(maskbytes.data(), ws, hs, QImage.Format_Grayscale8)
				node.remove()
				res = root.addChildNode(node, None)
				if not res:
					qDebug("Failed to add node to group")
				if mask is not None:
					#gn.addChildNode(mask, node)
					thisMask = doc.createNode(node.name() +" Mask", "transparency_mask")
					node.addChildNode(thisMask, None)
					ptr = maskImage.bits()
					ptr.setsize(maskImage.byteCount())
					thisMask.setPixelData(QByteArray(ptr.asstring()), xs, ys, ws, hs)
					#doc.setActiveNode(mask)
					doc.waitForDone()
					#Krita.instance().action('convert_to_transparency_mask').trigger()


			self.DB[id] = {} #create new group in DB
			self.DB[id]['groupLayer'] = gn.uniqueId() #store the group layer reference
			self.DB[id]['index'] = 0 #set default index to first result
			self.DB[id]['results'] = resultsDict
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
			qDebug("RESCOL ERROR: No results to get")
			return None, None, None
		id = self.groupSelector.currentText()
		index = self.DB[id]['index']
		results = self.DB[id]['results']
		return id, index, results
	
	def changeNextResult(self):
		if self.groupSelector.count() == 0:
			qDebug("RESCOL ERROR: No results to get")
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
			qDebug("RESCOL ERROR: No results to get")
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
			qDebug("RESCOL ERROR: No results to get")
			return
		id, index, results = self.getRef()
		qDebug("Showing only index " + str(newindex) + " of " + str(len(results)) + " results")
		doc = Krita.instance().activeDocument()
		for i, (k, result) in enumerate(results.items()):
			node: Node = doc.nodeByUniqueID(result['UID'])
			if i == newindex:
				qDebug("Showing node: " + result['UID'].toString() + " at index " + str(i))
				node.setVisible(True)
			else:
				node.setVisible(False)
		doc.waitForDone()
		doc.refreshProjection()
	
	def deleteIndex(self):
		if self.groupSelector.count() == 0:
			qDebug("RESCOL ERROR: No results to get")
			return
		id, index, results = self.getRef()
		for i, result in results.items():
			if i == index:
				node: Node = results[index]['node']
				node.remove()
				del result
		if index == len(results):
			index = 0
		self.DB[id]['index'] = index
		self.showOnlyIndex(index)

	def deleteAllOthers(self):
		if self.groupSelector.count() == 0:
			qDebug("RESCOL ERROR: No results to get")
			return
		id, index, results = self.getRef()
		doc = Krita.instance().activeDocument()
		for i, result in enumerate(results):
			node: Node = doc.nodeByUniqueID(result['UID'])
			if i != index:
				node.remove()
		self.showOnlyIndex(0)
	





