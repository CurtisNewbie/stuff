#!/bin/python3

import xml.etree.ElementTree as ET
import sys
from xml.etree.ElementTree import ElementTree

NAMESPACE: str = "{http://maven.apache.org/POM/4.0.0}"

if __name__ == '__main__':
    args = sys.argv[1:]
    l =  len(args)
    if l < 2:
        print("Must specify path to pom.xml file")
        sys.exit(1)

    pom_path = args[0]
    project_name = args[1]
    print("processing pom file: ", pom_path, "project_name: ", project_name)

    ET.register_namespace('', "http://maven.apache.org/POM/4.0.0")
    ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
    tree: "ElementTree" = ET.parse(pom_path)

    pnt = ('name', '')
    project_t = tree.getroot()

    # project.name
    name_t = project_t.find(NAMESPACE + "name")
    name_t.text = project_name
    print(f"set project.name to {project_name}")

    # project.artifactId
    art_t = project_t.find(NAMESPACE + "artifactId")
    art_t.text = project_name
    print(f"set project.artifactId to {project_name}")

    # project.description (optional)
    if l > 2:
        desc_t = project_t.find(NAMESPACE + "description")
        desc_t.text = args[2]
        print(f"set project.description to {args[2]}")

    tree.write(pom_path)
    print(f"reconfigured {pom_path}")
