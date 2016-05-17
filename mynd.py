#! /usr/bin/env python
"""
A command-line tool to merge completed tasks from a Freeplane/Docear to-do list.
"""

import os, os.path, sys
import argparse
import glob
import xml.etree.cElementTree as ET
import xmlformatter
formatter = xmlformatter.Formatter()

def isChecked(node):
    return node.find("./icon[@BUILTIN='checked']") is not None

def modifyRootNodeText(root, newtext):
    rootnode = root.find("node")
    # print rootnode.get("TEXT")
    rootnode.set("TEXT", newtext)
    # print rootnode.get("TEXT")
    # print ET.tostring(rootnode)
    # rootnode.append()
    return root

def modifyDetails(node, newtext):
    """
    Add an html <p>newtext</p> entry in details of node
    This is added before any existing html <p></p> entries
    """
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
    """
    Recursive function that removes any branches that do not conatin a checked
    node.
    """
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

def pruneChecked(tree):
    """
    Like pruneTree, but instead of keeping all checked nodes, this instead
    removes them.
    """
    # if isChecked(tree):
    #     # Add details about when was first checked
    #     tree = modifyDetails(tree, "Completed in: " + treename)
    #     return tree
    subnodes = tree.findall("node")
    subcopy = subnodes[:]
    for child in subnodes:
        if isChecked(child):
            tree.remove(child)
            subcopy.remove(child)
        else:
            child = pruneChecked(child)
        # #print child.get("TEXT")
        # print "pruning", child.get("TEXT")
        # prunedChild = pruneChecked(child)
        # if isChecked(prunedChild) is None:
        #     print "removing", child.get("TEXT")
        #     tree.remove(child)
        #     subcopy.remove(child)
    if len(subcopy) == 0:
        return None
    return tree

def getSameNode(node, tree):
    """
    Finds a node in `tree` with the same TEXT as `node`
    """
    textstr = "./node[@TEXT='" + node.get("TEXT") + "']"
    textstr = textstr.replace("'", "\'")
    # print textstr
    outlist = tree.findall(textstr)
    assert len(outlist) <= 1

    if len(outlist) == 0:
        return None
    else:
        return outlist[0]

def mergeBranches(branch1, branch2):
    """
    Merges `branch1` with `branch2` using node TEXT. Nodes with same TEXT, found
    using `getSameNode`, are merged recursively.
    """
    subnodes2 = branch2.findall("node")
    for node2 in subnodes2:
        print node2.get("TEXT")
        node1 = getSameNode(node2, branch1)
        if node1 is None:
            branch1.append(node2)
        else:
            print "merging"
            print node1.get("TEXT")
            newnode1 = mergeBranches(node1, node2)
            branch1.remove(node1)
            branch1.append(newnode1)
    return branch1

def mergeTrees(masterRoot, newRoot):
    """
    Prunes unchecked branches in `newFile`, then merges the remaining pruned
    tree with `masterFile`. Both files are given as a string with the file
    location.
    """

    if newRoot is None:
        print "No completed tasks to merge"
        return masterRoot

    treename = newRoot.find("node").get("TEXT")

    # Only merge after root level
    masterNodes = masterRoot.findall("node")
    assert len(masterNodes) == 1
    masterNode1 = masterNodes[0]
    newNodes = newRoot.findall("node")
    assert len(newNodes) == 1
    newNode1 = newNodes[0]

    # Merge first node after root
    newMaster1 = mergeBranches(masterNode1, newNode1)
    masterRoot.remove(masterNode1)
    masterRoot.append(newMaster1)
    # masterTree._setroot(masterRoot)

    return masterRoot

def getTreeName(tree):
    troot = tree.getroot()
    trname = troot.find("node").get("TEXT")
    return trname

def main():
    usage = """mynd.py <map>
    Simple tool to merge checked mindmap nodes to a master task tracker.
    """
    parser = argparse.ArgumentParser(description = 'merge mindmap files')
    parser.add_argument('map', type = str, help = 'location of mindmap ' + \
                        'file to operate upon')
    parser.add_argument('-u', help = 'keep only Unchecked nodes (default ' + \
                        'is to keep only branches with checked nodes)',
                        dest = 'unchecked', default = False,
                        action = 'store_true')
    parser.add_argument('-w', type = str, help = 'file to write output to')
    parser.add_argument('-m', type = str, help = 'file to merge results into')
    parser.add_argument('-n', type = str, help = 'name of root node in new map')

    args = parser.parse_args()
    # print type(args.master), args.tomerge, os.getcwd()
    intree = ET.parse(args.map)
    outroot = intree.getroot() # to be replaced depending on args
    if args.unchecked:
        # Prune away the checked nodes
        prunedroot = pruneChecked(intree.getroot())

    else:
        # Prune away unchecked branches
        prunedroot = pruneTree(intree.getroot(), getTreeName(intree))

    if args.m is not None:
        outfile = args.m
        print outfile
        mergeInto = ET.parse(outfile)
        outroot = mergeTrees(mergeInto.getroot(), prunedroot)
    elif args.w is not None:
        outfile = args.w
    else:
        outfile = args.map
        outroot = prunedroot

    if args.n is not None:
        outroot = modifyRootNodeText(outroot, args.n)
    intree._setroot(outroot)
    intree.write(outfile)
    formatter.format_file(outfile)

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
    branch1 = ET.parse(os.environ["HOME"] + "/GoogleDrive/Docear/merge1.mm")
    branch2 = ET.parse(os.environ["HOME"] + "/GoogleDrive/Docear/merge2.mm")
    root1 = branch1.getroot()
    root2 = branch2.getroot()
    newroot = mergeBranches(root1, root2)
    branch1._setroot(newroot)
    branch1.write(os.environ["HOME"] + "/GoogleDrive/Docear/mergedTree.mm")

def testPrune():
    branch1 = ET.parse(os.environ["HOME"] + \
    "/GoogleDrive/Docear/scripts/examples/originals/map1.mm")
    branch1_nocheck = pruneChecked(branch1)
    branch1_nocheck.write(os.environ["HOME"] + \
    "/GoogleDrive/Docear/scripts/noMoreCheckedNodes.mm")

def testFoo():
    branch1 = ET.parse(os.environ["HOME"] + \
    "/GoogleDrive/Docear/scripts/examples/originals/map1.mm")
    modifyRootNodeText(branch1, "HI THERE")

# testFoo()
