#!/usr/bin/python2

import re
import argparse
from xml.dom.minidom import parse
import lua52

# Helpers
functions = {}
def functionName(type):
    global functions
    if not type in functions:
        functions[type] = 0
        return type
    name = type + str(functions[type])
    functions[type] += 1
    return name
    

parser = argparse.ArgumentParser(description='Process a script')
parser.add_argument('script', metavar='<script>', type=str, help='A script')
USE_UNIQUE_ID = False                   
args = parser.parse_args()
if args.script:
    fileName = args.script
else:
    fileName = raw_input("File: ")
file = open(fileName).read()

dom = parse("actions.xml")
list = []
for element in dom.getElementsByTagName("action"):
        if element.getAttribute("script").split("/")[-1] == fileName or element.getAttribute("value").split("/")[-1] == fileName:
            uniqueid = element.getAttribute("uniqueid")
            if uniqueid:
                list.append(str(uniqueid))
                USE_UNIQUE_ID = True
                continue
            try:
                list.append(int(element.getAttribute("itemid")))
            except:
                for i in range(int(element.getAttribute("fromid")), int(element.getAttribute("toid"))+1):
                    list.append(i)

