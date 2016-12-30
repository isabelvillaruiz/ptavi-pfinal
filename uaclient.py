#!/usr/bin/python3
# -*- coding: utf-8 -*-

''' USER AGENT CLIENT '''

import socket
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import time
import hashlib


''' READING AND EXTRACTION OF XML DATA'''

#FIRST PARAMETER : XML FILE 
XML_DATA = sys.argv[1]
#SECOND PARAMETRER : REQUEST
REQUEST = sys.argv[2]


if len(sys.argv) != 4:
    sys.exit("Usage: python uaclient.py config method option")

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
#print("Esto es account: ", ACCOUNT)

USERNAME = ACCOUNT['username']
#print("Esto es username:", USERNAME)

PASSWORD = ACCOUNT['passwd']

UASERVER_PORT = data[1]['uaserver']['puerto']
#print("Esto es el puerto de escucha del UAServer:", UASERVER_PORT)

UASERVER_IP = data[1]['uaserver']['ip']
#print("Esto es la direccion IP del UASERVER: ", UASERVER_IP)

RTP_PORT = data[2]['rtpaudio']['puerto']
#print("Esto es el puerdo de escuha de audio RTP: ", RTP_PORT)

PROXY_PORT = data[3]['regproxy']['puerto']
#print("Esto es el puerto del proxy: ", PROXY_PORT)

PROXY_IP = data[3]['regproxy']['ip']
#print("Esto es el puerto del proxy: ", PROXY_IP)

SONG = data[5]['audio']['path']

LOG = data[4]['log']['path']


'''SOCKET'''
# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((PROXY_IP,int(PROXY_PORT)))

'''LOG'''

fich = open('uaclient_log.txt','a')
str_now = time.strftime("%Y%m%d%H%M%S", time.gmtime(time.time()))



'''REQUESTS and their lines '''

if REQUEST == "REGISTER":
    SIP_INFO = USERNAME + ':' + UASERVER_PORT
    SIP_LINE = " sip:" + SIP_INFO + " SIP/2.0\r\n"
    EXPIRES_LINE = "Expires: " + EXPIRES + "\r\n"
    LINE = "REGISTER" + SIP_LINE + EXPIRES_LINE
    print("Esta es la linea que voy a enviar si es REGISTER: ")
    
    print(LINE)
    print("Enviando: " + "\r\n" + LINE)

    ''' LOG '''
    datos_log = str_now + " Sent to " + PROXY_IP + ":" + PROXY_PORT + " REGISTER" 
    datos_log += " sip:" + SIP_INFO + " SIP/2.0 " + EXPIRES_LINE
    fich.write(datos_log)
    '''end log'''  

    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    print(data.decode('utf-8'))
    
    
    LINE = data.decode('utf-8')
    Words_LINES = LINE.split()
    print("Esto es Words Lines" , Words_LINES)

    if Words_LINES[1] == "401":
        print("Hemos recibido un 401 Unauthorized")        
        nonce = Words_LINES[6].split("'")[1]
        print("nonce = ", nonce)
        m = hashlib.sha1()
        m.update(b'nonce')
        m.update(b'PASSWORD')
        m.hexdigest()
        response = m.hexdigest()
        print(m.hexdigest())
        SIP_INFO = USERNAME + ':' + UASERVER_PORT
        SIP_LINE = " sip:" + SIP_INFO + " SIP/2.0\r\n"
        EXPIRES_LINE = "Expires: " + EXPIRES + "\r\n"
        AUTH_LINE = "Authorization: Digest response=" + "'" + response + "'" + "\r\n"
        LINE = "REGISTER" + SIP_LINE + EXPIRES_LINE + AUTH_LINE
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        data = my_socket.recv(1024)
        print(data.decode('utf-8'))     
        
    #if data.decode('utf-8') == ("SIP/2.0 401 Unauthorized\r\n\r\n")
    #    print("UNAUTHORIZED")
    #if data.decode('utf-8') == "SIP/2.0 200 OK\r\n\r\n":
    #    '''LOG'''
    #    datos_log = str_now + " Received from " + PROXY_IP + ":" + PROXY_PORT 
    #    datos_log += "SIP/2.0 " + "200 OK"
    #    fich.write(datos_log)
    #    '''end log''' 

elif REQUEST == "INVITE":
    SIP_INFO = USUARIO
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

    '''LOG '''
    datos_log = str_now + " Sent to " + PROXY_IP + ":" + PROXY_PORT + " INVITE" 
    datos_log += " sip:" + SIP_INFO + " SIP/2.0 " + SDP_LINE
    fich.write(datos_log)
    ''' end log ''' 

    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    print(data.decode('utf-8'))
    
    WERECEIVE = data.decode('utf-8').split('\r\n\r\n')
    WERECEIVE_CODES = WERECEIVE[:3]
    print("WERECEIVE_CODES: ", WERECEIVE_CODES) 
    WERECEIVE_SDP = WERECEIVE[3:]
    SDP_SPLIT = WERECEIVE[3].split("\r\n")
    RTP_PORT_RECEIVE = SDP_SPLIT[5].split(" ")[1]
    print("PRUEBA DEL PUERTO RTP QUE NOS ENVIA EL PROXY DEL SERVER: ", "\r\n", RTP_PORT_RECEIVE)


    MUSTRECEIVE100 = ("SIP/2.0 100 Trying")
    MUSTRECEIVE180 = ("SIP/2.0 180 Ring")
    MUSTRECEIVE200 = ("SIP/2.0 200 OK")
    MUSTRECEIVE = [MUSTRECEIVE100, MUSTRECEIVE180, MUSTRECEIVE200]

    print("MUSTRECEIVE: ", MUSTRECEIVE)
    print("WERECEIVE_CODES: ",WERECEIVE_CODES)
    
    #ENVIO AUTOMATICO DE ACK AL RECIBIR 100 180 200 DEL PROXY POR PARTE DEL SERVIDOR
    if WERECEIVE_CODES == MUSTRECEIVE:
        SIP_INFO = USUARIO
        LINE = "ACK" + " sip:" + SIP_INFO + " SIP/2.0\r\n"
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        data = my_socket.recv(1024)
        print(data.decode('utf-8'))
        print("Reproduciendo")
        aEjecutar = './mp32rtp -i 127.0.0.1 -p ' + RTP_PORT_RECEIVE + ' < ' + SONG
        #aEjecutar = "./mp32rtp -i 127.0.0.1 " -p " + RTP_PORT_RECEIVE
        #aEjecutar += " < " + SONG

        print ('Vamos a ejecutar', aEjecutar)
        os.system(aEjecutar)
        #print("ENVIANDO AUDIO RTP IMAGINARIO AL PUERTO: ", RTP_PORT_RECEIVE)

        #AQUI HABRA QUE VER SI RECIBIMOS EL 100 180 200 DEL PROXY EMPEZAR EL RTP
        #"Ahora tendriamos que recibir en el 200 ok informacion del puerto rtp del servidor"

elif REQUEST == "BYE":
    SIP_INFO = USUARIO
    LINE = "BYE" + " sip:" + SIP_INFO + " SIP/2.0\r\n"
    print("Enviando: " + LINE)
    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    print(data.decode('utf-8'))



# Cerramos todo
my_socket.close()
print("Fin.")


'''
print("Enviando: " + LINE)
my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
data = my_socket.recv(1024)
'''














