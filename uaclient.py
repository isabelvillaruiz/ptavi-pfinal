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
#SECOND PARAMETRER : REQUEST
REQUEST = sys.argv[2]

if REQUEST == 'REGISTER':
    EXPIRES = sys.argv[3]
elif REQUEST == 'INVITE':
    USUARIO = sys.argv[3]
elif REQUEST == 'BYE':
    USUARIO = sys.argv[3]


class Handler(ContentHandler):

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
cHandler = Handler()
parser.setContentHandler(cHandler)
parser.parse(open(XML_DATA))
data = cHandler.get_tags()
print(data)



'xml data'
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
print("Esto es el puerdo de escuha de audio RTP: ", RTP_PORT)

PROXY_PORT = data[3]['regproxy']['puerto']
print("Esto es el puerto del proxy: ", PROXY_PORT)

PROXY_IP = data[3]['regproxy']['ip']
print("Esto es el puerto del proxy: ", PROXY_IP)





'''SOCKET'''
# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((PROXY_IP,int(PROXY_PORT)))




'''REQUESTS and their lines '''

if REQUEST == "REGISTER":
    SIP_INFO = USERNAME + ':' + UASERVER_PORT
    SIP_LINE = " sip:" + SIP_INFO + " SIP/2.0\r\n"
    EXPIRES_LINE = "Expires: " + EXPIRES + "\r\n"
    LINE = "REGISTER" + SIP_LINE + EXPIRES_LINE
    print("Esta es la linea que voy a enviar si es REGISTER: ")
    print(LINE)
    print("Enviando: " + "\r\n" + LINE)
    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    print(data.decode('utf-8'))
elif REQUEST == "INVITE":
    SIP_INFO = USERNAME
    SIP_LINE = " sip:" + SIP_INFO + " SIP/2.0\r\n"
    SDP_LINE_CT = "Content-Type: application/sdp" + "\r\n"
    print()
    v = "v=0"
    o = "o=" + USERNAME + " " + UASERVER_IP
    s = "s=SesionGhibli"
    t = "t=0"
    m = "m=audio " + RTP_PORT + " RTP"
    SDP_LINE_1 = "\r\n" + v + "\r\n" + o + "\r\n" + s + "\r\n"
    SDP_LINE_2 = t + "\r\n" + m + "\r\n"
    SDP_LINE = SDP_LINE_CT + SDP_LINE_1 + SDP_LINE_2
    #print("ESTA ES UNA PRUEBA DE LA LINEA SDP", SDP_LINE)
    LINE = "INVITE" + SIP_LINE + SDP_LINE
    print("Esta es la linea que voy a enviar si es INVITE: ")
    print(LINE)
    print("Enviando: " + LINE)
    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    print(data.decode('utf-8'))
elif REQUEST == "BYE":
    SIP_INFO = USERNAME
    LINE = "BYE" + " sip:" + SIP_INFO + " SIP/2.0\r\n"
    print("Enviando: " + LINE)
    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    print(data.decode('utf-8'))

'''
print("Enviando: " + LINE)
my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
data = my_socket.recv(1024)
'''

# Cerramos todo
my_socket.close()
print("Fin.")

















