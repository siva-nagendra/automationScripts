'''
An Export tool that gets the scene hierarchy in XML format.
'''

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import pymel.core as pm

import os, fnmatch

import xml.etree.ElementTree as et

import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om

def mayaMainWindow():
    # Parenting the widget to Maya's main window
    mainWindowPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mainWindowPtr), QtWidgets.QWidget)

class ExportAsXml(QtWidgets.QDialog):
    def __init__(self, parent = mayaMainWindow()):
        super(ExportAsXml, self).__init__(parent)
        self.setWindowTitle("Export Hierarchy as XML")
        self.setMinimumSize(300, 140)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint) # Remove help button
        self.createWidgets()
        self.createLayouts()
        self.createConnections()
    
    def createWidgets(self):
        self.filepath_le = QtWidgets.QLineEdit()
        self.selectFilepath_btn = QtWidgets.QPushButton()
        self.selectFilepath_btn.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.selectFilepath_btn.setToolTip("Select the Export path.")
        
        self.iShapes_chkb = QtWidgets.QCheckBox("Include Intermediate Shapes")
        self.iShapes_chkb.setToolTip("Includes the Intermediate Shapes.")
        
        self.export_btn = QtWidgets.QPushButton("Export Selected Hierarchy")
        self.export_btn.setToolTip("Exports the selected Hierarchy in XML format.")
        
        self.close_btn = QtWidgets.QPushButton("Close")
    
    def createLayouts(self):
        filepath_layout = QtWidgets.QHBoxLayout()
        filepath_layout.addWidget(self.filepath_le)
        filepath_layout.addWidget(self.selectFilepath_btn)
        
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Path:", filepath_layout)
        form_layout.addWidget(self.iShapes_chkb)
        
        btn_layout = QtWidgets.QVBoxLayout()
        btn_layout.addStretch()
        
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.close_btn)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(btn_layout)
        
    def createConnections(self):
        self.selectFilepath_btn.clicked.connect(self.showFileSelect_dialog)
        self.export_btn.clicked.connect(self.exportXml)
        self.iShapes_chkb.toggled.connect(self.getInterShapesState)
        self.close_btn.clicked.connect(self.close)
        
    def showFileSelect_dialog(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
        directory = dialog.getExistingDirectory(self, 'Choose Export path', "")
        if directory:
            self.filepath_le.setText(directory)
            
    def selectionHierarchy(self, start):
        # With PyMel, using recursion to get the scene hierarchy
        hierarchyDict = {}
        startNode = pm.PyNode(start)
        children = startNode.getChildren()
        interShapes = self.getInterShapesState()
        if children:
            for child in children:
                if "|" in child:
                    continue
                if not interShapes:
                    if not (child.isIntermediate()):
                        hierarchyDict[child.name()] = self.selectionHierarchy(child.name())
                else:
                    hierarchyDict[child.name()] = self.selectionHierarchy(child.name())
        return hierarchyDict

    def getFinalHeirarchy(self):
        # Creating a nested dictionary from the scene heirarchy data
        selection = pm.selected()[0]
        finalHierarchyDict = {selection.name() : self.selectionHierarchy(selection.name())}
        return finalHierarchyDict

    def prettify(self, element, indent='  '):
        # I use this function to format XML better
        # Got this from Stackoverflow
        queue = [(0, element)]
        while queue:
            level, element = queue.pop(0)
            children = [(level + 1, child) for child in list(element)]
            if children:
                element.text = '\n' + indent * (level+1)
            if queue:
                element.tail = '\n' + indent * queue[0][0]
            else:
                element.tail = '\n' + indent * (level-1)
            queue[0:0] = children
    
    def dictToXml(self, hierarchicalDict, parent = None):
        # Iterating through the Nested Dictionary using recursion to get the scene DAG structure in XML
        for key,value in hierarchicalDict.iteritems():
            self.node = et.SubElement(parent, "objectName")
            self.node.set("name", cmds.ls(sl = True)[0])
            self.child = et.SubElement(self.node, key)
            dict_to_xml(value, self.child)
    
    def writeXmlData(self):
        # Creating the tree structure in XML with Car: as namespace
        self.rootNode = et.Element("DAGData")
        self.rootNode.set("xmlns:Car", "NameSpace")
        self.finalHierarchyDict = self.getFinalHeirarchy()
        self.dictToXml(self.finalHierarchyDict, self.rootNode)
        self.prettify(self.rootNode)
        self.tree = et.ElementTree(self.rootNode)
        return self.tree
        
    def find(self, pattern, path):
        # A helper function to find files from a directory
        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
        return result
    
    def getXmlFileName(self, xmlOutPath, xmlName):
        # Handling versioning to create a unique filename for XML
        xmlFiles = self.find("*.xml", xmlOutPath)
        if xmlFiles:
            for xmlFile in xmlFiles:
                head_tail = os.path.split(xmlFile)
                tail = head_tail[1]
                if xmlName in tail:
                    cur_version = tail.split(".")[0].split("_")[-1]
                    version = int(cur_version) + 1
                else:
                    version = 1
        else:
            version = 1
        xmlFileName = xmlName + "_{}.xml".format(str(version).zfill(4))
        return xmlFileName
        
    def exportXml(self):
        # Writes out an XML based on the selection and the path provided
        # Handling basic Exceptions
        if cmds.ls(sl = True):
            xmlData = self.writeXmlData()
            xmlOutPath = self.filepath_le.text()
            if xmlOutPath:
                xmlName = "car_RIG_hierarchy"
                xmlFileName = self.getXmlFileName(xmlOutPath, xmlName)
                with open(xmlOutPath + "/" + xmlFileName, "w") as xmlFile:
                    self.tree.write(xmlFile, encoding = "UTF-8", xml_declaration = True)
                om.MGlobal.displayInfo("XML File Name: {} \nExported Successfully!!".format(xmlOutPath + "/" + xmlFileName))
            else:
                om.MGlobal.displayWarning("Please specify a path to export.")
        else:
            om.MGlobal.displayWarning("Please select something to export.")
    
    def getInterShapesState(self):
        # Gets the status of intermediate shapes checkbox
        if self.iShapes_chkb.isChecked():
            self.interShapes = True
        else:
            self.interShapes = False
        return self.interShapes
        
if __name__ == "__main__":
    try:
        exportAsXmlDialog.close()
        exportAsXmlDialog.deleteLater()
    except:
        pass
    exportAsXmlDialog = ExportAsXml()
    exportAsXmlDialog.show()