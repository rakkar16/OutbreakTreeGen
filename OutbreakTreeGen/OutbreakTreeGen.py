import random
import math
import sys
import warnings
try:
    import ete3
    eteExists = True
except ImportError:
    eteExists = False
    warnings.warn('ETE is not installed.')

sys.setrecursionlimit(1000)

TRANSMISSIONCHANCE = 0.7
POINTTRANSMISSIONCHANCE = 0.3
MUTATIONCHANCE = 0.3
DISCOVERYCHANCE = 0.2
MAXNODES = 100
MAXTICKS = 200
ISPOINTSOURCE = False
OUTPUTMODE = None

nodecount = 0

class TreeNode(object):
    def __init__(self, parent=None, pointSource=False, active=True, children=[]):
        global nodecount
        self.isPointSource = pointSource
        self.parent = parent
        self.children = children
        self.active = active
        self.isLeaf = False
        self.toDelete = False
        nodecount += 1

    def tick(self):
        global isalive
        for child in self.children:
            child.tick()
        if self.active:
            isalive = True
            if random.random() < DISCOVERYCHANCE and not self.isPointSource:
                self.active = False
                if self.children:
                    self.children.append(TreeNode(self, active=False, children=[]))
            elif (random.random() < TRANSMISSIONCHANCE and not self.isPointSource) or (random.random() < POINTTRANSMISSIONCHANCE and self.isPointSource):
                self.children.append(TreeNode(self, children=[]))
            elif random.random() < MUTATIONCHANCE:
                if self.children:
                    self.children.append(TreeNode(self, self.isPointSource, children=[]))
                    self.active = False


    def finalize(self):
        if self.children:
            if len(self.children) == 1:
                self.parent.children += self.children
                self.toDelete = True
            else:
                for child in self.children:
                    child.finalize()
                tempchildren = [child for child in self.children if not child.toDelete]
                self.children = tempchildren 
        else:
            self.isLeaf = True

    def newickOutput(self, mode=None):
        if not self.parent:
            end = ';'           
        else:
            end = ''
        if self.isLeaf:
            return 'x' + end
        else:
            if mode == 'undervalue':
                name = str(self.undervalue)
            elif mode == 'rootvalue':
                name = str(self.rootvalue)
            elif mode == 'test':
                name = 'x'
            else:
                name = ''

            return '(' + ','.join([child.newickOutput(mode) for child in self.children]) + ')' + name + end

    def leafCount(self):
        if self.isLeaf:
            return 1
        else:
            return sum([child.leafCount() for child in self.children])

    def calculateUndervalue(self):
        if self.isLeaf:
            self.undervalue = 0
        else:
            undervalue = len([child for child in self.children if child.isLeaf])
            undervalue += max([child.calculateUndervalue() for child in self.children])
            a = len([child for child in self.children if not child.isLeaf])
            if a > 0:
                undervalue += a - 1
            self.undervalue = undervalue
        return self.undervalue

    def calcMaxContrib(self):
        if self.isLeaf:
            self.rootvalue = 1
        else:
            rootvalue = len([child for child in self.children if child.isLeaf])
            underlist = [child.undervalue for child in self.children]
            underlist.sort(reverse=True)
            rootvalue += sum(underlist[0:2])
            a = len([child for child in self.children if not child.isLeaf])
            if a > 1:
                rootvalue += a - 2
            if self.parent:
                rootvalue += 1
            self.rootvalue = rootvalue
        return max([child.calcMaxContrib() for child in self.children] + [self.rootvalue])

root = TreeNode(pointSource = ISPOINTSOURCE)

def calcMinMaxContrib(n):
    if n == 1:
        return 1

    k = int(math.log2(n))  #n = 2**k + m
    lowbound = 2 ** k
    base = 2 * k
    if n - lowbound == 0:
        return base
    elif n - lowbound <= 2**(k-1):
        return base + 1
    else:
        return base + 2




for tick in range(MAXTICKS):
    global isalive
    isalive = False
    root.tick()
    if nodecount >= MAXNODES or not isalive:
        break

root.finalize()
root.calculateUndervalue()
leafNum = root.leafCount()
maxContrib = root.calcMaxContrib()
minMaxContrib = calcMinMaxContrib(leafNum)
if leafNum != minMaxContrib:
    ratio = (maxContrib - minMaxContrib)/(leafNum - minMaxContrib)
else:
    ratio = 'Not Enough Data'
print('MinMaxContrib = {}'.format(minMaxContrib))
print('MaxMaxContrib = {}'.format(leafNum))
print('MaxContrib = {}'.format(maxContrib))
print('Ratio = {}'.format(ratio))
texttree = root.newickOutput(OUTPUTMODE)
print(texttree)

if eteExists:
    tree = ete3.Tree(texttree, format = 8)

    #print(tree.get_ascii(show_internal=True))

    #ts = ete3.TreeStyle()
    #ts.show_leaf_name = True
    #tree.show(tree_style = ts)