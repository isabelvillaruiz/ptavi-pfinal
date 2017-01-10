#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""USER AGENT SERVER."""

import socket
import socketserver
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import time

"""READING AND EXTRACTION OF XML DATA."""

if len(sys.argv) != 2:
    sys.exit("Usage: python uaserver.py config")

#FIRST PARAMETER :  XML FILE
XML_DATA = sys.argv[1]


class SmallSMILHandler(ContentHandler):
    """CLASE DE LECTURA DE XML."""

    def __init__(self):
        """Diccionario xml."""
        self.list = []
        self.dicc = {"account": ["username", "passwd"],
                     "uaserver": ["ip", "puerto"],
                     "rtpaudio": ["puerto"],
                     "regproxy": ["ip", "puerto"],
                     "log": ["path"],
                     "audio": ["path"]}

    def startElement(self, name, attrib):
        """Start Element."""
        if name in self.dicc:
            dicc = {}
            for item in self.dicc[name]:
                dicc[item] = attrib.get(item, "")
            diccname = {name: dicc}
            self.list.append(diccname)

    def get_tags(self):
        """Devuelve la lista xml."""
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
#print("Esto es account: ", ACCOUNT)
USERNAME = ACCOUNT['username']
#print("Esto es username:", USERNAME)
UASERVER_PORT = data[1]['uaserver']['puerto']
#print("Esto es el puerto de escucha del UAServer:", UASERVER_PORT)
UAS_IP = data[1]['uaserver']['ip']
#print("Esto es la direccion IP del UASERVER: ", UAS_IP)
RTP_PORT = data[2]['rtpaudio']['puerto']
SONG = data[5]['audio']['path']
LOG_FILE = data[4]['log']['path']
PROXY_PORT = data[3]['regproxy']['puerto']
PROXY_IP = data[3]['regproxy']['ip']

'''LOG'''
fichero = LOG_FILE
fich = open(fichero, 'a')
str_now = time.strftime("%Y%m%d%H%M%S", time.gmtime(time.time()))


class EchoHandler(socketserver.DatagramRequestHandler):
    """Echo."""

    PORT_RTP = []

    def handle(self):
            u"""Escribe dirección y puerto cliente (tupla client_address)."""
            while 1:
                # Leyendo línea a línea lo que nos envía el cliente
                text = self.rfile.read()
                line = self.rfile.read()
                print("Proxy manda cliente: ")
                print(text.decode('utf-8'))
                LINE = text.decode('utf-8')
                REQUESTS = ['INVITE', 'ACK', 'BYE']
                Words_LINES = LINE.split()
                print("Esta es la linea que me envia el proxy", Words_LINES)
                REQUEST = Words_LINES[0]
                #PORT_RTP = []
                if REQUEST == 'INVITE':
                    RTP_PORT_RECEIVE = Words_LINES[11]
                    self.PORT_RTP.append(RTP_PORT_RECEIVE)
                    #Hemos añadido el puerto a un diccionario
                    print("LISTA RECIEN INVENTADA", self.PORT_RTP)
                    print("Puerto RTP nos envia el cliente en INVITE: ")
                    print(RTP_PORT_RECEIVE)

                if not REQUEST in REQUESTS:
                    LINE_405 = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                    self.wfile.write(LINE_405)

                if REQUEST == 'INVITE':
                    '''LOG'''
                    datos_log1 = str_now + " Received from "
                    datos_log1 += self.client_address[0] + ":"
                    datos_log1 += str(self.client_address[1])
                    datos_log1 += " " + LINE.replace("\r\n", " ") + "\r\n"
                    fich.write(datos_log1)
                    answer = "SIP/2.0 100 Trying\r\n\r\n"
                    answer += "SIP/2.0 180 Ring\r\n\r\n"
                    answer += "SIP/2.0 200 OK\r\n\r\n"
                    answer += "Content-Type: application/sdp\r\n\r\n"
                    answer += "v=0\r\n" + "o=" + USERNAME + " "
                    answer += UAS_IP + " \r\n" + "s=SesionGhibli\r\n"
                    answer += "t=0\r\n" + "m=audio " + RTP_PORT
                    answer += " RTP\r\n\r\n"
                    self.wfile.write(bytes(answer, 'utf-8'))
                    '''LOG'''
                    datos_log2 = str_now + " Sent to " + PROXY_IP + ":"
                    datos_log2 += PROXY_PORT + " "
                    datos_log2 += answer.replace("\r\n", " ") + "\r\n"
                    fich.write(datos_log2)

                elif REQUEST == 'ACK':
                    '''LOG'''
                    datos_log1 = str_now + " Received from "
                    datos_log1 += self.client_address[0] + ":"
                    datos_log1 += str(self.client_address[1])
                    datos_log1 += " " + LINE.replace("\r\n", " ") + "\r\n"
                    fich.write(datos_log1)
                    #print("imprimiendo la lista inventada", self.PORT_RTP)
                    PUERTO = self.PORT_RTP[0]
                    print("Reproduciendo")
                    aEjecutar = './mp32rtp -i 127.0.0.1 -p ' + PUERTO + ' < '
                    aEjecutar += SONG
                    #aEjecutar = "./mp32rtp -i " + DIR_DEST + " -p " + PUERTO
                    #aEjecutar += " < " + SONG
                    os.system(aEjecutar)
                    print('End')
                    #print("ENVIANDO AUDIO RTP IMAGINARIO AL PUERTO: ", PUERTO)
                elif REQUEST == 'BYE':
                    '''LOG'''
                    datos_log1 = str_now + " Received from "
                    datos_log1 += PROXY_IP + ":"
                    datos_log1 += str(self.client_address[1])
                    datos_log1 += " " + LINE.replace("\r\n", " ") + "\r\n"
                    fich.write(datos_log1)
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                    '''LOG'''
                    datos_log2 = str_now + " Sent to "
                    datos_log2 += PROXY_IP + ":" + PROXY_PORT
                    datos_log2 += " " + "SIP/2.0 200 OK" + "\r\n"
                    fich.write(datos_log2)

                # Si no hay más líneas salimos del bucle infinito
                if not line:
                    break

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((UAS_IP, int(UASERVER_PORT)), EchoHandler)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
