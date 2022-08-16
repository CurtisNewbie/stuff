#!/bin/python3

import xml.etree.ElementTree as ET
import sys
from xml.etree.ElementTree import ElementTree
import argparse

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


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Tool for reading attributes in pom.xml (by Yongj.Zhuang)")
    parser.add_argument('-p', '--path', type=str,
                        help="path to pom.xml", default="pom.xml")

    ag = parser.add_argument_group("required arguments")
    ag.add_argument('-t', '--tag', type=str,
                    help="tag name (e.g., project.version)", required=True)
    return parser


if __name__ == '__main__':

    parser = parser()
    args = parser.parse_args()

    nested_tags = args.tag
    pom_path = args.path

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
        # print(f"t: {t}, nested_tags: {nested_tags}, curr: {curr_t}")
        curr_t = curr_t.find(NAMESPACE + t)
        if curr_t is None:
            raise RuntimeError(f"Element for tag: '{t}' is not found")

        nested_tags = trimtag(nested_tags)
        t = nexttag(nested_tags)

        # special case
        if nexttag(trimtag(nested_tags)) == 'version':
            t += '.version'
            nested_tags = trimtag(nested_tags)

    print(f"tag: '{args.tag}', value: '{curr_t.text}'")
