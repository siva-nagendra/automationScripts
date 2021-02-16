'''
Disconneects all the disabled nodes and places them in a backdrop
'''
import nuke, nukescripts.autobackdrop

distance = 0
backdropName = "Garbage"
sel = []

# Colors for the node tiles. Adjust the r, g, b values to change colors.
r = 0.8
g = 0
b = 0
hexColor = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,1),16)

# Disconncting all the disabled nodes from selection and moving them away.
if nuke.selectedNodes():
    for each in nuke.selectedNodes():
        for inputIndex in range(each.inputs()):
            input = each.input(inputIndex)
            if nuke.toNode(input.name()).knob('disable').value()==True:
                lastNode = each.input(inputIndex)
                each.setInput(inputIndex, None)
                input.setInput(inputIndex, lastNode)
        # moving the nodes
        if nuke.toNode(each.name()).knob('disable').value()==True:
            each.setXpos(500 + distance)
            sel.append(each)
        distance += 20
        each["selected"].setValue(False)

    # selecting all the disabled objects
    for item in sel:
        n = nuke.toNode(item.name())
        n.knob('tile_color').setValue(hexColor)
        n.knob('selected').setValue(True)
    # adding a backdrop
    if len(sel) >= 1:
        backdrop = nukescripts.autobackdrop.autoBackdrop()
        backdrop.knob('tile_color').setValue(hexColor)
        backdrop.setName(backdropName)
    else:
        print ("No disabled objects in the scene")
else:
    print ("No objects are selected.")