from esprima import NodeVisitor, parseScript
from graphviz import Digraph, Source
from pickler import Pickler
import json


class Converter(NodeVisitor):
    def __init__(self):
        # Initialize property
        self.input_file = None
        self._operator = []
        self._obj_type = []
        self._prop_name = []
        self._right_ele = []
        self._class_names = []
        self._class_methods = []
        self._attributes = []
        self._dict_of_everything = {}
        self._index = 0

    def dump_data(self):
        with open('result.json', 'w') as fp:
            json.dump(self._dict_of_everything, fp)

    def load_data(self, input_file):
        self.input_file = input_file
        return input_file

    def extract_data(self, con_class):
        filecontents = ""
        try:
            with open(self.input_file, 'r') as f:
                for line in f:
                    filecontents += line
            data = parseScript(filecontents, delegate=con_class)
            print('Data has been extracted')
            return data
        except Exception as e:
            print('There was an error in the JavaScript file: ' + str(e))

    def visit_ClassDeclaration(self, node):
        self._class_names.append(node.id.name)
        self.generic_visit(node)

    def is_constructor(self, node):
        result = False
        if node.key.name == 'constructor':
            result = True
        return result

    def visit_MethodDefinition(self, node):
        if self.is_constructor(node):
            self._class_methods = []
            self._attributes = []
            self._index += 1
            body = node.value.body.body
            self.set_class_attributes(body)
            # print("-------------")
            # print(self._prop_name)
            # print(self._operator)
            # print(self._right_ele)
            # print("-------------")
        self._class_methods.append(node.key.name)
        class_values = {
            'classname': self._class_names[self._index - 1],
            'classmethod': self._class_methods,
            'attributes': self._attributes
        }
        class_num = "class" + str(self._index)
        self._dict_of_everything[class_num] = class_values

    def set_class_attributes(self, body):
        for key in body:
            expr = key.expression
            result = 'this.'
            # self._attributes.append(expr.left.property.name)

            if expr.left is not None:
                result += expr.left.property.name

            # self._attributes.append(expr.operator)
            result += expr.operator
            if expr.right.type == 'ArrayExpression':
                # self._attributes.append(expr.right.elements)
                result += str(expr.right.elements)
            elif expr.right.type == 'Literal':
                # self._attributes.append(expr.right.raw)
                result += expr.right.raw
            else:
                # self._attributes.append(expr.right.name)
                result += expr.right.name
            self._attributes.append(result)

    def convert_to_uml(self):
        dot = Digraph(comment='UML Diagram')
        if bool(self._dict_of_everything) is True:
            for key in self._dict_of_everything:
                class_info = self._dict_of_everything.get(key)
                classname = class_info.get('classname')
                methods = class_info.get('classmethod')
                attributes = class_info.get('attributes')
                dot.node(classname,
                         "{{{classname}|{attributes}|{methods}}}".format(
                             classname=classname,
                             attributes="\l".join(attributes),
                             methods="()\l".join(methods) + "()"
                         ),
                         shape="record",
                         )
                # print(class_info)
            # dot.edge('CycleLog', 'Ride')
            s = Source(dot.source, filename="test.gv", format="png")
            s.view()
        else:
            return None

    def make_pickle(self):
        pickle = Pickler()
        try:
            assert len(self._dict_of_everything.keys()) > 0
            pickle.serialise(self._dict_of_everything)
            with open('result.json', 'w', encoding='utf8') as json_file:
                json.dump(self._dict_of_everything ,json_file)

        except FileNotFoundError as e:
            print(e)
        except AssertionError:
            print('Dictionary is empty, try loading then extracting data first')