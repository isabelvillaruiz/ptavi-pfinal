#!/usr/bin/python3
# -*- coding: utf-8 -*-

''' USER AGENT CLIENT '''

import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

''' READING AND EXTRACTION OF XML DATA'''

#FIRST PARAMETER : XML FILE 
XML_DATA = sys.argv[1]


class SmallSMILHandler(ContentHandler):

    def __init__(self):

        self.list = []
        self.dicc = {"account": ["username", "passwd"],
                     "uaserver": ["ip", "puerto"],
                     "rtpaudio": ["puerto"],
                     "regproxy": ["ip", "puerto"],
                     "log": ["path"],
                     "audio": ["path"]}

    def startElement(self, name, attrib):
        if name in self.dicc:
            dicc = {}
            for item in self.dicc[name]:
                dicc[item] = attrib.get(item, "")
            diccname = {name: dicc}
            self.list.append(diccname)

    def get_tags(self):

        return self.list


parser = make_parser()
cHandler = SmallSMILHandler()
parser.setContentHandler(cHandler)
parser.parse(open(XML_DATA))
data = cHandler.get_tags()
print(data)



'DATOS'
#Vamos a probar a sacar algun dato del diccionario creado con los datos del xml 

ACCOUNT = data[0]['account']
print("Esto es account: ", ACCOUNT)
USERNAME = ACCOUNT['username']
print("Esto es username:", USERNAME)
