#!/usr/bin/python3
# -*- coding: utf-8 -*-

''' USER AGENT SERVER'''

import socket
import socketserver
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler




''' READING AND EXTRACTION OF XML DATA'''

if len(sys.argv) != 2:
    sys.exit("Usage: python uaserver.py config")

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
UASERVER_PORT = data[1]['uaserver']['puerto']
print("Esto es el puerto de escucha del UAServer:", UASERVER_PORT)
UASERVER_IP = data[1]['uaserver']['ip']
print("Esto es la direccion IP del UASERVER: ", UASERVER_IP)
RTP_PORT = data[2]['rtpaudio']['puerto']


class EchoHandler(socketserver.DatagramRequestHandler):

    def handle(self):
            """Escribe dirección y puerto del cliente (de tupla client_address)."""
            while 1:
                # Leyendo línea a línea lo que nos envía el cliente
                text = self.rfile.read()
                line = self.rfile.read()
                print("El proxy nos manda del cliente " + "\r\n" + text.decode('utf-8'))
                LINE = text.decode('utf-8')
                METHODS = ['INVITE', 'ACK', 'BYE']
                Words_LINES = LINE.split()
                print("Esta es la linea que me envia el proxy", Words_LINES)                
                REQUEST = Words_LINES[0]
                print("FUNCIONA")

                #Ahora que lo pienso es estupido porq el 405 lo detectara el prxy antes XD
                if not REQUEST in METHODS:
                    LINE_405 = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                    self.wfile.write(LINE_405)           

                if REQUEST == 'INVITE': 
                    answer = "SIP/2.0 100 Trying\r\n\r\n"
                    answer += "SIP/2.0 180 Ring\r\n\r\n"
                    answer += "SIP/2.0 200 OK\r\n\r\n"
                    answer += "Content-Type: application/sdp\r\n\r\n"
                    answer += "v=0\r\n" + "o=" + USERNAME + " "
                    answer += UASERVER_IP + " \r\n" + "s=SesionGhibli\r\n"
                    answer += "t=0\r\n" + "m=audio " + RTP_PORT + " RTP\r\n\r\n"
                    self.wfile.write(bytes(answer, 'utf-8'))
                elif REQUEST == 'BYE':
                    print("HOWL!")

                # Si no hay más líneas salimos del bucle infinito
                if not line:
                    break






if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((UASERVER_IP, int(UASERVER_PORT)), EchoHandler)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
