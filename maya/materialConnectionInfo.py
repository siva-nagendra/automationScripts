'''
Prints out the information of Car:Seats_SHD material to Maya console.
Written solely using MayaPythonAPI 1.0 and 2.0
'''

import maya.OpenMaya as om1 # MayaAPI 1.0
import maya.api.OpenMaya as om # MayaAPI 2.0

# defaultdict is used to store the compound attributes
from collections import defaultdict

nodeName = "Car:Seats_SHD"
connections = []
compoundAttrs = defaultdict(list)
uvAttrs = []

def makeDependencyNode(nodeName):
    # A Helper function to use later that returns MFnDependencyNode based on the provided Node name
    selection = om.MGlobal.getSelectionListByName(nodeName)
    mobject = selection.getDependNode(0)
    mfnDependencyNode = om.MFnDependencyNode(mobject)
    return mfnDependencyNode

def getAllConnections():
    # Travarsing the Dependency Graph to find all the connection of Car:Seats_SHD
    mfnDependencyNode = makeDependencyNode(nodeName)
    object_name = mfnDependencyNode.name().encode()
    mcommand_result = om1.MCommandResult()
    om1.MGlobal.executeCommand(
        'listHistory %s' % object_name, mcommand_result, False, True)          
    results = []
    mcommand_result.getResult(results)
    for each_result in results:
        connections.append(each_result.encode())
    return connections

def getCompoundUvAttrs(uvAttrCheck):
    # Getting all the attributes and filtering all the Compound Attributes
    # Also using the same function to get the U and V coordinate Attribues
    networkConnections = getAllConnections()
    for eachNode in networkConnections:       
        node = makeDependencyNode(eachNode)
        ports = node.getConnections()
        for port in ports:
            if port.isCompound:
                portValue = []
                for i in range(port.numChildren()):
                    childPort = port.child(i)
                    attrValue = childPort.asDouble()
                    
                    portValue.append('{} = {}'.format(childPort, attrValue))
                    compoundAttrs[str(port).split(":")[-1]] = portValue
                    
                    if "Coord" in childPort.name():
                        # Filtering based on the "Coord" instead of "U" or "V" as it gives all the u and v coordinates as asked.
                        # Also storing the Value of the attribute. Just in case if needed.
                        uvAttrs.append(('{} = {}'.format(childPort, attrValue)))

def prettyPrint(heading, attrs = [], values = []):
    # A helper function to print the attributes in a fun way.
    print ("\n\n\n\n\n")
    print ('*' * (len(heading)+6))
    print ('** %s **' % heading)
    print ('*' * (len(heading)+6))
    
    for index in range(len(attrs)):
        attr = '\n%s' % str(attrs[index])
        print (attr)
        print ('-' * int(len(heading) + 6))
        for eachValue in values[index]:
            print (eachValue)

def materialConnectionInfo(allConnectionsCheck, compoundAttrsCheck, uvAttrCheck):
    # Gets the values and prints them using prettyPrint
    allConnHeading = "All Connections"
    compAttrHeading = "Compound Attributes"
    uvAttrHeading = "U and V Attributes"
    getCompoundUvAttrs(uvAttrCheck)
    
    if allConnectionsCheck:
        attrs = ["Node = {}".format(nodeName)]
        prettyPrint(allConnHeading, attrs, [connections])

    if compoundAttrsCheck and not uvAttrCheck:
        compAttr = compoundAttrs.keys()
        comValues = compoundAttrs.values()
        prettyPrint(compAttrHeading, compAttr, comValues)
    elif not compoundAttrsCheck and uvAttrCheck:
        attrs = ["Node = {}".format(nodeName)]
        uvValues = [uvAttrs]
        prettyPrint(uvAttrHeading, attrs, uvValues)
    elif compoundAttrsCheck and uvAttrCheck:
        compAttr = compoundAttrs.keys()
        comValues = compoundAttrs.values()
        prettyPrint(compAttrHeading, compAttr, comValues)
        
        attrs = ["Node = {}".format(nodeName)]
        uvValues = [uvAttrs]
        prettyPrint(uvAttrHeading, attrs, uvValues)
        
if __name__ == "__main__":
    # Please change the parameter values to True in order to print
    # Eg: To print Compound Attributes, change the compoundAttrsCheck to True and run the code.
    materialConnectionInfo(allConnectionsCheck = True, compoundAttrsCheck = False, uvAttrCheck = False)