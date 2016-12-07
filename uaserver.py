#!/usr/bin/python3
# -*- coding: utf-8 -*-

''' USER AGENT SERVER'''

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


class EchoHandler(socketserver.DatagramRequestHandler):

def handle(self):
        """Escribe dirección y puerto del cliente (de tupla client_address)."""
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            text = self.rfile.read()
            line = self.rfile.read()
            print("El cliente nos manda " + text.decode('utf-8'))
            LINE = text.decode('utf-8')
            Words_LINES = LINE.split()
            REQUEST = Words_LINES[0]
            print("La peticion es: ", REQUEST)
            print("Listening...")

            if REQUEST == 'INVITE':
                answer100 = b"SIP/2.0 100 Trying\r\n\r\n"
                answer180 = b"SIP/2.0 180 Ring\r\n\r\n"
                answer200 = b"SIP/2.0 200 OK\r\n\r\n"
                ANSWER = answer100 + answer180 + answer200
                self.wfile.write(ANSWER)

            elif REQUEST == 'ACK':
                SONG = (sys.argv[3])
                aEjecutar = './mp32rtp -i 127.0.0.1 -p 23032 < ' + self.SONG
                print ('Vamos a ejecutar', aEjecutar)
                os.system(aEjecutar)
            elif REQUEST == 'BYE':
                self.wfile.write(b'SIP/2.0 200 OK\r\n\r\n')

            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((sys.argv[1], int(sys.argv[2])), EchoHandler)
    print("Lanzando servidor UDP de eco...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
















