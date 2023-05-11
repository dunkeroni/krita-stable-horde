from krita import *

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
    def __init__(self):
        self.buffer = set()
        self.DB = {}
        self.activeID = None
    
    def addBufferNode(self, node: Node, info: dict):
        #add node and info to the buffer as a tuple
        self.buffer.add((node, info))
        qDebug("Added node to result buffer")
    
    def bufferToDB(self, id: str):
        qDebug("bufferToDB")
        nodeDict = {}
        for result in self.buffer:
            node: Node = result[0]
            nodeUID = node.uniqueId()
            qDebug("node found: " + nodeUID.toString())
            nodeDict[nodeUID] = {
                "node": result[0],
                "info": result[1],
                "UID": nodeUID
            }
        self.DB[id] = nodeDict
        qDebug("Result buffer added to DB")
        self.buffer = set() #clear the buffer for the next generation

    





