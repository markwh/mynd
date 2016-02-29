#! /usr/bin/env python
"""
This module provides functions to merge mindmap trees.
"""

import os, os.path, sys
import argparse
import glob
import xml.etree.cElementTree as ET
import xmlformatter
formatter = xmlformatter.Formatter()

def isChecked(node):
    return node.find("./icon[@BUILTIN='checked']") is not None

def modifyDetails(node, newtext):
    deets = node.find('richcontent[@TYPE="DETAILS"]')
    print deets
    if deets is None:
        htmlString = '<richcontent TYPE="DETAILS"><html><head></head>' + \
        '<body><p>\n%s\n</p></body></html></richcontent>' \
        % newtext
        node.append(ET.fromstring(htmlString))
    else:
        htmlString = ET.tostring(deets.find("html"))
        newhtml = htmlString.replace("<p>", "<p>" + newtext + "</p><p>", 1)
        newhtml = formatter.format_string(newhtml)
        deets.remove(deets.find("html"))
        deets.append(ET.fromstring(newhtml))
    return node

def pruneTree(tree, treename):
    if isChecked(tree):
        # Add details about when was first checked
        tree = modifyDetails(tree, "Completed in: " + treename)
        return tree
    subnodes = tree.findall("node")
    subcopy = subnodes[:]
    for child in subnodes:
        #print child.get("TEXT")
        print "pruning", child.get("TEXT")
        prunedChild = pruneTree(child, treename)
        if prunedChild is None:
            print "removing", child.get("TEXT")
            tree.remove(child)
            subcopy.remove(child)
    if len(subcopy) == 0:
        return None
    return tree

def getSameNode(node, tree):
    textstr = "./node[@TEXT='" + node.get("TEXT") + "']"
    outlist = tree.findall(textstr)
    assert len(outlist) <= 1

    if len(outlist) == 0:
        return None
    else:
        return outlist[0]

def mergeTrees(tree1, tree2):
    subnodes2 = tree2.findall("node")
    for node2 in subnodes2:
        print node2.get("TEXT")
        node1 = getSameNode(node2, tree1)
        if node1 is None:
            tree1.append(node2)
        else:
            print "merging"
            print node1.get("TEXT")
            newnode1 = mergeTrees(node1, node2)
            tree1.remove(node1)
            tree1.append(newnode1)
    return tree1

def pruneAndMerge(masterFile, newFile):
    masterTree = ET.parse(masterFile)
    masterRoot = masterTree.getroot()

    newTree = ET.parse(newFile)
    newRoot = newTree.getroot()
    treename = newRoot.find("node").get("TEXT")
    newPruned = pruneTree(newTree.getroot(), treename)

    if newPruned is None:
        print "No completed tasks to merge"
        return

    # Only merge after root level
    masterNodes = masterRoot.findall("node")
    assert len(masterNodes) == 1
    masterNode1 = masterNodes[0]
    newNodes = newPruned.findall("node")
    assert len(newNodes) == 1
    newNode1 = newNodes[0]

    # Merge first node after root
    newMaster1 = mergeTrees(masterNode1, newNode1)
    masterRoot.remove(masterNode1)
    masterRoot.append(newMaster1)
    masterTree._setroot(masterRoot)

    # write to file
    masterTree.write(masterFile)
    formatter.format_file(masterFile)

def main():
    usage = """syncmm.py <master> <tomerge>
    Simple tool to merge checked mindmap nodes to a master task tracker.
    """
    parser = argparse.ArgumentParser(description = 'merge mindmap files')
    parser.add_argument('master', type = str, help = 'location of mindmap ' + \
                        'file in which to accumulate checked nodes')
    parser.add_argument('tomerge', type = str, help = 'location of mindmap ' + \
                        'file containing newly checked nodes')
    args = parser.parse_args()
    # print type(args.master), args.tomerge, os.getcwd()
    pruneAndMerge(masterFile = args.master, newFile = args.tomerge)


if __name__ == "__main__":
    sys.exit(main())


##------------------------------
## BELOW HERE ARE TEST FUNCTIONS
##------------------------------

def testAll():
    pruneAndMerge(os.environ["HOME"] + "/GoogleDrive/Docear/testMaster.mm", \
    os.environ["HOME"] + "/GoogleDrive/Docear/merge2.mm")


def testMerge():
    print os.getcwd()
    tree1 = ET.parse(os.environ["HOME"] + "/GoogleDrive/Docear/merge1.mm")
    tree2 = ET.parse(os.environ["HOME"] + "/GoogleDrive/Docear/merge2.mm")
    root1 = tree1.getroot()
    root2 = tree2.getroot()
    newroot = mergeTrees(root1, root2)
    tree1._setroot(newroot)
    tree1.write(os.environ["HOME"] + "/GoogleDrive/Docear/mergedTree.mm")
