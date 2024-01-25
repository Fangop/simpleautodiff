from math import log as math_log
from math import sin as math_sin
from math import cos as math_cos


class Node:
    verbose = False
    input_count = 0
    intermediate_count = 0

    def __init__(self, value, parent_nodes=[], operator="input", grad_wrt_parents=[]):
        self.value = value
        self.parent_nodes = parent_nodes
        self.child_nodes = []
        self.operator = operator
        self.grad_wrt_parents = grad_wrt_parents
        self.partial_derivative = 0

        if operator == "input":
            Node.input_count += 1
            self.name = "x%d" % (Node.input_count)
        else:
            Node.intermediate_count += 1
            self.name = "v%d" % (Node.intermediate_count)

        if Node.verbose == True:
            print("{:<2} = {:>5}{:<12} = {:<8}".format(
                self.name,
                self.operator,
                str([p.name for p in self.parent_nodes]),
                self.value.__round__(3))
            )


def add(node1, node2):
    value = node1.value + node2.value
    parent_nodes = [node1, node2]
    grad_wrt_parents = [1, 1]
    newNode = Node(value, parent_nodes, "add", grad_wrt_parents)
    node1.child_nodes.append(newNode)
    node2.child_nodes.append(newNode)
    return newNode


def sub(node1, node2):
    value = node1.value - node2.value
    parent_nodes = [node1, node2]
    grad_wrt_parents = [1, -1]
    newNode = Node(value, parent_nodes, "sub", grad_wrt_parents)
    node1.child_nodes.append(newNode)
    node2.child_nodes.append(newNode)
    return newNode


def mul(node1, node2):
    value = node1.value * node2.value
    parent_nodes = [node1, node2]
    grad_wrt_parents = [node2.value, node1.value]
    newNode = Node(value, parent_nodes, "mul", grad_wrt_parents)
    node1.child_nodes.append(newNode)
    node2.child_nodes.append(newNode)
    return newNode


def log(node):
    value = math_log(node.value)
    parent_nodes = [node]
    grad_wrt_parents = [1/(node.value)]
    newNode = Node(value, parent_nodes, "log", grad_wrt_parents)
    node.child_nodes.append(newNode)
    return newNode


def sin(node):
    value = math_sin(node.value)
    parent_nodes = [node]
    grad_wrt_parents = [math_cos(node.value)]
    newNode = Node(value, parent_nodes, "sin", grad_wrt_parents)
    node.child_nodes.append(newNode)
    return newNode


def topological_order(rootNode):
    def add_children(node):
        if node not in visited:
            visited.add(node)
            for child in node.child_nodes:
                add_children(child)
            ordering.append(node)
    ordering, visited = [], set()
    add_children(rootNode)
    return reversed(ordering)


def forward(rootNode):
    rootNode.partial_derivative = 1
    ordering = topological_order(rootNode)
    for node in ordering:
        partial_derivative = 0
        process = ["",""]
        for i in range(len(node.parent_nodes)):
            dnode_dparent = node.grad_wrt_parents[i]
            dparent_droot = node.parent_nodes[i].partial_derivative
            partial_derivative += dnode_dparent * dparent_droot
            node.partial_derivative = partial_derivative
            process[0]+="(d" + node.name + "/d" + node.parent_nodes[i].name + ")"\
                              + "(d" + node.parent_nodes[i].name + "/d" + rootNode.name + ") + "
            process[1]+="(" + str(dnode_dparent.__round__(3)) + ")(" + \
                    str(node.parent_nodes[i].partial_derivative.__round__(3)) + ") + "
        if Node.verbose == True:
            print('d{:<2}/d{:<2} = {:<45} \n\t= {:<30} = {:<5}'.format(
                node.name,
                rootNode.name,
                process[0].strip(" + "), # Remove the tailing " + "
                process[1].strip(" + "), # Remove the tailing " + "
                str(node.partial_derivative.__round__(3)))
            )
