# Copyright 2014, Sandia Corporation. Under the terms of Contract
# DE-AC04-94AL85000 with Sandia Corporation, the U.S. Government retains certain
# rights in this software.

import copy
import io
import xml.etree.ElementTree as xml

def append_element(graph, name, inputs):
    parent = copy.copy(inputs.getone("parent"))
    child = inputs.getone("child")
    parent.append(child)
    return parent


def create_element(tag, attrib={}, **extra):
    def implementation(graph, name, inputs):
        return xml.Element(tag, attrib=attrib, **extra)
    return implementation


def dump(element, level=0):
    indent = "  " * level
    attributes = "".join(f" {key}=\"{str(value)}\"" for key, value in element.items())
    if len(element) or element.text:
        print(f"{indent}<{element.tag}{attributes}>")
        if element.text:
            print(f"{indent}  {element.text}")
        for child in element:
            dump(child, level+1)
        print(f"{indent}</{element.tag}>")
    else:
        print(f"{indent}<{element.tag}{attributes}/>")


def set_attribute(key, value):
    def implementation(graph, name, inputs):
        original = inputs.getone(None)
        modified = xml.Element(original.tag, attrib=original.attrib)
        for child in original:
            modified.append(child)
        modified.set(key, value)
        return modified
    return implementation

def tostring(element):
    attributes = "".join(f" {key}=\"{str(value)}\"" for key, value in element.items())
    if len(element) or element.text:
        result = f"<{element.tag}{attributes}>"
        if element.text:
            result += element.text
        for child in element:
            result += tostring(child)
        return result + f"</{element.tag}>"
    return f"<{element.tag}{attributes}/>"

