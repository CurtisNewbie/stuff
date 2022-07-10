#!/bin/python3

import xml.etree.ElementTree as ET
import sys
from xml.etree.ElementTree import ElementTree

NAMESPACE: str = "{http://maven.apache.org/POM/4.0.0}"

def nexttag(t: str) -> str:
    if t is None:
        return None

    dt = t.find(".")
    return t if dt == -1 else t[0:dt]

def trimtag(t: str) -> str:
    if t is None:
        return None

    dt = t.find(".")
    return None if dt == -1 else t[dt+1:]

if __name__ == '__main__':
    args = sys.argv[1:]
    l = len(args)
    if l < 2:
        print("[0] - path to pom.xml")
        print("[1] - tag name (e.g., project.version)")
        sys.exit(1)

    nested_tags = args[0]

    pom_path = args[1]

    ET.register_namespace('', "http://maven.apache.org/POM/4.0.0")
    ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
    tree: "ElementTree" = ET.parse(pom_path)

    root_t = tree.getroot()
    curr_t = root_t

    t = nexttag(nested_tags)

    if t == 'project':
        nested_tags = trimtag(nested_tags)
        t = nexttag(nested_tags)


    while t is not None:
        print(f"t: {t}, nested_tags: {nested_tags}, curr: {curr_t}")
        curr_t = curr_t.find(NAMESPACE + t)
        if curr_t is None:
            raise RuntimeError(f"Element for tag: '{t}' is not found") 

        nested_tags = trimtag(nested_tags)
        t = nexttag(nested_tags)

        # special case
        if nexttag(trimtag(nested_tags)) == 'version': 
            t += '.version' 
            nested_tags = trimtag(nested_tags)
    
    print(f"tag: '{args[1]}', value: '{curr_t.text}'")

