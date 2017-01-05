#!/usr/bin/python3
# -*- coding: utf-8 -*-

''' PROXY - REGISTRO '''

import socketserver
import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
#from time import time, gmtime, strftime
import time
import json
import hashlib

''' READING AND EXTRACTION OF XML DATA'''

#FIRST PARAMETER : XML FILE
XML_DATA = sys.argv[1]


if len(sys.argv) != 2:
    sys.exit("Usage: python proxy_registrar.py config")


class Handler(ContentHandler):

    def __init__(self):

        self.list = []
        self.dicc = {"server": ["name", "ip", "puerto"],
                     "database": ["path", "passwdpath"],
                     "log": ["path"]}

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
#print(data)


'xml data'

PROXY_IP = data[0]['server']['ip']
#print("Esta es la ip del proxy: ", PROXY_IP)
PROXY_PORT = data[0]['server']['puerto']
#print("Este es el puerto del proxy: ", PROXY_PORT)
PROXY_NAME = data[0]['server']['name']
PASS_FILE = data[1]['database']['passwdpath']
LOG_FILE = data[2]['log']['path']

'''LOG'''
fichero = LOG_FILE
fich = open(fichero, 'a')
str_now = time.strftime("%Y%m%d%H%M%S", time.gmtime(time.time()))

'passwords data'

file_passwd = PASS_FILE
passwd_file = open(file_passwd, 'r')
passwd_data = passwd_file.read()
print("Datos del archivo passwords: ")
print(passwd_data)
PASSWORD1 = passwd_data.split()[1].split("'")[1]
PASSWORD2 = passwd_data.split()[3].split("'")[1]
print("PASSWORD1: ", PASSWORD1)
print("PASSWORD2: ", PASSWORD2)

'''Recepcion SOCKET'''


class EchoHandler(socketserver.DatagramRequestHandler):

    dicc = {}

    def register2json(self):
        json_file = open("registered.json", "w")
        json.dump(self.dicc, json_file)
        json_file.close()

    def json2registered(self):

        try:
            #("Estamos probando")
            with open("registered.json") as JsonFile:
                self.dicc = json.load(JsonFile)
        except:
                pass

    def handle(self):
        while 1:
            """Escribe dirección y puerto del cliente(tupla client_address)."""
            # Leyendo línea a línea lo que nos envía el cliente
            text = self.rfile.read()
            line = self.rfile.read()
            print("El cliente nos manda " + "\r\n" + text.decode('utf-8'))
            LINE = text.decode('utf-8')
            Words_LINES = LINE.split()
            print("PRUEBA CON MIKE:", Words_LINES)
            REQUEST = Words_LINES[0]
            LINE_SIP = Words_LINES[1].split(":")
            nonce = "898989898989898989898989898988989"
            print("Esto es split de lo que me manda el cliente", Words_LINES)
            print("La peticion es: ", REQUEST)
            print("Listening...")

            if REQUEST == 'REGISTER':

                print(len(Words_LINES))
                if len(Words_LINES) == 8:

                    '''COMPROBACION DE LAS CONTRASEÑAS'''

                    Words_LINES = LINE.split()
                    LINE_SIP = Words_LINES[1].split(":")
                    USUARIO_SIP = LINE_SIP[1]
                    print("WORDS_LINES",Words_LINES)
                    RCV_PORT = Words_LINES[1].split(":")[2]
                    
                    response = Words_LINES[7].split("'")[1]
                    print("response: ", response)

                    ''' LOG. '''
                    datos_log1 = str_now + " Received from " 
                    datos_log1 += self.client_address[0] + ":" + RCV_PORT 
                    datos_log1 += " " + LINE.replace("\r\n", " ") + "\r\n"
                    fich.write(datos_log1)

                    if USUARIO_SIP == "totoro@ghibli.com":
                        PASSWORD = PASSWORD2
                        m = hashlib.sha1()
                        m.update(b'nonce')
                        m.update(b'PASSWORD')
                        m.hexdigest()
                        exp_response = m.hexdigest()
                        print("exp_response: ", exp_response)
                        if exp_response == response:
                            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                            '''LOG.'''
                            datos_log2 = str_now + " Sent to "
                            datos_log2 += self.client_address[0] + ":"
                            datos_log2 += RCV_PORT + " SIP/2.0 200 OK" + "\r\n"
                            fich.write(datos_log2)
                        elif exp_response != response:
                            self.wfile.write(b"SIP/2.0 489 Bad Event\r\n\r\n")
                            '''LOG.'''
                            datos_log3 = str_now + " Sent to "
                            datos_log3 += self.client_address[0] + ":"
                            datos_log3 += RCV_PORT + " SIP/2.0 489 Bad Event"
                            datos_log3 += "\r\n"
                            fich.write(datos_log3)
                    elif USUARIO_SIP == "calcifer@ghibli.com":
                        PASSWORD = PASSWORD1
                        m = hashlib.sha1()
                        m.update(b'nonce')
                        m.update(b'PASSWORD')
                        m.hexdigest()
                        exp_response = m.hexdigest()
                        print("exp_response: ", exp_response)
                        if exp_response == response:
                            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                            '''LOG.'''
                            datos_log4 = str_now + " Sent to "
                            datos_log4 += self.client_address[0] + ":"
                            datos_log4 += RCV_PORT + " SIP/2.0 200 OK" + "\r\n"
                            fich.write(datos_log4)
                        elif exp_response != response:
                            self.wfile.write(b"SIP/2.0 489 Bad Event\r\n\r\n")
                            '''LOG.'''
                            datos_log5 = str_now + " Sent to "
                            datos_log5 += self.client_address[0] + ":"
                            datos_log5 += RCV_PORT + " SIP/2.0 489 Bad Event"
                            datos_log5 += "\r\n"
                            fich.write(datos_log5)
                            break

                    print("LINE_SIP:", LINE_SIP)
                    self.json2registered()
                    USUARIO_SIP = LINE_SIP[1]
                    print(USUARIO_SIP)
                    PUERTO_SIP = LINE_SIP[2]
                    print("Puerto sip de la linea que nos envia el cliente: ")
                    print(PUERTO_SIP)
                    REQUEST = Words_LINES[0]
                    Expires = int(Words_LINES[4])
                    print(Expires)
                    DIR_ip = self.client_address[0]
                    #PUERTO = self.client_address[1]
                    print("Direccion ip client_addres : ", DIR_ip)

                    #expiration = time.gmtime(int(time.time()) + Expires)
                    #str_exp = time.strftime('%Y-%m-%d %H:%M:%S', expiration)
                    #now = time.gmtime(time.time())
                    #str_now = time.strftime('%Y-%m-%d %H:%M:%S', now)

                    now = int(time.time())
                    #str_now = strftime('%Y-%m-%d %H:%M:%S', gmtime(now))
                    time_exval = int(Expires) + now
                    #str_ex = strftime('%Y-%m-%d %H:%M:%S', gmtime(time_exval))

                    self.dicc[USUARIO_SIP] = {'address': DIR_ip,
                                              'port': PUERTO_SIP,
                                              'expires': time_exval}
                    #Comprobacion de usuarios expirados
                    lista_expirados = []
                    for user in self.dicc:

                        if self.dicc[user]['expires'] <= now:
                            lista_expirados.append(user)
                    for name in lista_expirados:
                        del self.dicc[name]
                    self.register2json()
                    print("El diccionario: ")
                    print(self.dicc)

                elif len(Words_LINES) == 5:
                    RCV_PORT = Words_LINES[1].split(":")[2]
                    '''LOG.'''
                    datos_log7 = str_now + " Received from " 
                    datos_log7 += self.client_address[0] + ":"
                    datos_log7 += RCV_PORT + " " + LINE.replace("\r\n", " ") 
                    datos_log7 += "\r\n"
                    fich.write(datos_log7)
                    

                    print("Enviamos un 401 Unauthorized")
                    LINE_SIP = ("SIP/2.0 401 Unauthorized\r\n\r\n")
                    LINE_DIGEST = LINE_SIP + "WWW Authenticate: Digest "
                    LINE_DIGEST += "nonce=" + "'" + nonce + "'"
                    self.wfile.write(bytes(LINE_DIGEST, 'utf-8'))

                    '''LOG.'''
                    datos_log6 = str_now + " Sent to " 
                    datos_log6 += self.client_address[0] + ":"
                    datos_log6 += RCV_PORT + LINE_DIGEST.replace("\r\n", " ")
                    datos_log6 += "\r\n"
                    fich.write(datos_log6)

            elif REQUEST == 'INVITE':
                print("Imprimiendo sabiendo que es un invite: ", Words_LINES)

                USUARIO_SIP = LINE_SIP[1]
                #print("USUARIO_SIP", USUARIO_SIP)
                US_INVITE = Words_LINES[1].split(":")[1]
                #print("US_INVITE", US_INVITE)
                US_ORIGIN = Words_LINES[6].split("=")[1]

                
                print("Este es el usuario al que queremos invitar", US_INVITE)
                with open('registered.json') as file:
                    data = json.load(file)
                    datos = data
                    #print("IMPRIMIENDO EL DICCIONARIO", data)
                    #dataipdata = data[USUARIO_SIP]['address']
                    #print("ESTO ES DATA IP DATA", dataipdata)
                    
                    ''' LECTURA DE DATOS DEL REGISTRO '''
                    for user in data:                    
                        if user == "totoro@ghibli.com":
                            totoro_port = data["totoro@ghibli.com"]['port']
                            totoro_ip = data["totoro@ghibli.com"]['address']
                            print("TOTORO PORT", totoro_port)
                            print("TOTORO IP", totoro_ip)
                        if user == "calcifer@ghibli.com":
                            clfer_port = data["calcifer@ghibli.com"]['port']
                            clfer_ip = data["calcifer@ghibli.com"]['address']
                            print("CALCIFER PORT", clfer_port)
                            print("CALCIFER IP", clfer_ip)
                    '''Comprobacion de la existencia del usuario. '''
                    for user in data:
                        if user == US_INVITE:
                            print("PODEMOS COMUNICARNOS CON ESTE USUARIO!")
                            print('Este es el usuario registrado', user)
                            print("Usuario que queremos invitar: ", US_INVITE)
                            dataipdata = data[USUARIO_SIP]['address']
                            dataportdata = data[USUARIO_SIP]['port']
                            print("Puerto del invitado", dataportdata)
                            '''LOG'''
                            datos_log1 = str_now + " Received from " 
                            datos_log1 += self.client_address[0] + ":"
                            datos_log1 += str(self.client_address[1]) + " "
                            datos_log1 += LINE.replace("\r\n", " ") + "\r\n"
                            fich.write(datos_log1)
                            '''SOCKET'''
                            # Creamos el socket y  atamos un servidor/puerto
                            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            my_socket.connect((dataipdata, int(dataportdata)))
                            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
                            '''LOG.'''
                            datos_log2 = str_now + " Sent to " 
                            datos_log2 += dataipdata + ":" +  dataportdata
                            datos_log2 += " " + LINE.replace("\r\n", " ") 
                            datos_log2 += "\r\n"
                            fich.write(datos_log2)
                            data = my_socket.recv(1024)
                            print("Hemos recibido del servidor:", "\r\n")
                            print(data.decode('utf-8'))
                            DATA = data.decode('utf-8')
                            WERECEIVE = DATA.split('\r\n\r\n')[0:-1]
                            WERECEIVE_CODES = WERECEIVE[:3]
                            WERECEIVE_SDP = WERECEIVE[3:]
                            SDP_SPLIT = WERECEIVE[4].split("\r\n")
                            VERSION = WERECEIVE[4].split("\r\n")[0]
                            ORIGIN = SDP_SPLIT[1]
                            SESION = SDP_SPLIT[2]
                            TIME = SDP_SPLIT[3]
                            MULTIMEDIA = SDP_SPLIT[4]
                            #Mensaje SDP
                            answer = WERECEIVE_SDP[0] + "\r\n" + VERSION
                            answer += "\r\n" + ORIGIN + "\r\n" + SESION
                            answer += "\r\n" + TIME + "\r\n" + MULTIMEDIA

                            print("Prueba del WE RECEIVE: ", WERECEIVE)
                            MUSTRECEIVE100 = ("SIP/2.0 100 Trying")
                            MUSTRECEIVE180 = ("SIP/2.0 180 Ring")
                            MUSTRECEIVE200 = ("SIP/2.0 200 OK")
                            MUSTRECEIVE = [MUSTRECEIVE100,
                                           MUSTRECEIVE180, MUSTRECEIVE200]
                            #print("WERECEIVE_CODES", WERECEIVE_CODES)
                            #print("MUSTRECEIVE", MUSTRECEIVE)

                            if WERECEIVE_CODES == MUSTRECEIVE:
                                '''LOG'''
                                datos_log1 = str_now + " Received from "
                                datos_log1 += dataipdata + ":" + dataportdata
                                datos_log1 += " " + DATA.replace("\r\n", " ") 
                                datos_log1 += "\r\n"
                                fich.write(datos_log1)
                                self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                                self.wfile.write(b"SIP/2.0 180 Ring\r\n\r\n")
                                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                                self.wfile.write(bytes(answer, 'utf-8'))
                                '''LOG '''
                                datos_log1 = str_now + " Sent to "
                                datos_log1 +=  self.client_address[0] + ":"
                                datos_log1 += str(self.client_address[1])
                                datos_log1 += " SIP/2.0 100 Trying"
                                datos_log1 += " SIP/2.0 180 Ring"
                                datos_log1 += " SIP/2.0 200 OK "
                                datos_log1 += answer.replace("\r\n", " ")
                                datos_log1 += "\r\n"
                                fich.write(datos_log1)

                        elif user != US_INVITE and user != US_ORIGIN:
                            answer404 = ("SIP/2.0 404 User Not Found\r\n\r\n")
                            self.wfile.write(bytes(answer404, 'utf-8'))
                            '''LOG'''
                            datos_log = str_now + " Sent to "
                            datos_log +=  self.client_address[0] + ":"
                            datos_log += str(self.client_address[1]) + " "
                            datos_log += answer404.replace("\r\n", " ")
                            datos_log += "\r\n"
                            fich.write(datos_log)
            elif REQUEST == 'ACK':
                '''LOG'''
                datos_log1 = str_now + " Received from "
                datos_log1 +=  self.client_address[0] + ":"
                datos_log1 += str(self.client_address[1]) + " "
                datos_log1 += LINE.replace("\r\n", " ") + "\r\n"
                fich.write(datos_log1)
                LINE = text.decode('utf-8')
                LINE_ACK = LINE
                print(LINE)
                USUARIO_SIP = LINE_SIP[1]
                print('USUARIO_SIP:', USUARIO_SIP)
                US_INVITE = Words_LINES[1].split(":")[1]
                print("US_INVITE", US_INVITE)

                print("Enviando ACK al servidor")
                #Es lo mismo USUARIO_SIP que US_INVITE.

                with open('registered.json') as file:
                    data = json.load(file)
                    datos = data
                    for user in data:
                        if user == US_INVITE:
                            dataportdata = data[USUARIO_SIP]['port']
                            dataipdata = data[USUARIO_SIP]['address']
                            #print("dataportdata: ", dataportdata)
                            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            my_socket.connect((dataipdata, int(dataportdata)))
                            my_socket.send(bytes(LINE_ACK, 'utf-8') + b'\r\n')
                            '''LOG.'''
                            datos_log2 = str_now + " Sent to " 
                            datos_log2 += dataipdata + ":" +  dataportdata
                            datos_log2 += " " + LINE_ACK.replace("\r\n", " ") 
                            datos_log2 += "\r\n"
                            fich.write(datos_log2)
                            data = my_socket.recv(1024)
                            print(data.decode('utf-8'))

            elif REQUEST == 'BYE':
                ''' LOG.'''
                datos_log1 = str_now + " Received from "
                datos_log1 += self.client_address[0] + ":"
                datos_log1 += str(self.client_address[1]) + " "
                datos_log1 += LINE.replace("\r\n", " ") + "\r\n"
                fich.write(datos_log1)
                Words_LINES = LINE.split()
                LINE = text.decode('utf-8')
                USUARIO_SIP = LINE_SIP[1]
                US_BYE = Words_LINES[1].split(":")[1]
                with open('registered.json') as file:
                    data = json.load(file)
                    datos = data
                    for user in data:
                        if user == US_BYE:
                            dataportdata = data[USUARIO_SIP]['port']
                            dataipdata = data[USUARIO_SIP]['address']
                            #print("dataportdata: ", dataportdata)
                            print("Enviando: " + LINE)
                            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            my_socket.connect((dataipdata, int(dataportdata)))
                            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
                            '''LOG.'''
                            datos_log1 = str_now + " Sent to " 
                            datos_log1 += dataipdata + ":" +  dataportdata
                            datos_log1 += " " +  LINE.replace("\r\n", " ") 
                            datos_log1 += "\r\n"
                            fich.write(datos_log1)
                            data = my_socket.recv(1024)
                            print(data.decode('utf-8'))
                            MUSTRECEIVE200 = ("SIP/2.0 200 OK")
                            MUSTRECEIVE = [MUSTRECEIVE200]
                            DATA = data.decode('utf-8')
                            WERECEIVE = DATA.split('\r\n\r\n')[0:-1]

                            if WERECEIVE == MUSTRECEIVE:
                                ''' LOG.'''
                                datos_log2 = str_now + " Received "
                                datos_log2 += dataipdata + ":" +  dataportdata
                                datos_log2 += " SIP/2.0 200 OK" + "\r\n"
                                fich.write(datos_log2)

                                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                                ''' LOG.'''
                                datos_log3 = str_now + " Sent to "
                                datos_log3 +=  self.client_address[0] + ":"
                                datos_log3 += str(self.client_address[1])
                                datos_log3 += " SIP/2.0 200 OK" + "\r\n"
                                fich.write(datos_log3)
                #Ahora debemos volver a entrar en el fichero y
                # coger para el usuario sip
                # su puerto del servidor para poder enviarle un ACK

            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((PROXY_IP, int(PROXY_PORT)), EchoHandler)
    print("Server " + PROXY_NAME + " listening at port " + PROXY_PORT + " ...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado PROXY")
