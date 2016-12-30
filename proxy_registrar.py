#!/usr/bin/python3
# -*- coding: utf-8 -*-

''' PROXY - REGISTRO '''

import socketserver
import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from time import time, gmtime, strftime
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



'passwords data'

passwd_file  = open('passwords.txt','r')
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
            """Escribe dirección y puerto del cliente (de tupla client_address).""" 
            # Leyendo línea a línea lo que nos envía el cliente
            text = self.rfile.read()
            line = self.rfile.read()
            print("El cliente nos manda " +"\r\n" + text.decode('utf-8'))
            LINE = text.decode('utf-8')
            Words_LINES = LINE.split()
            print("PRUEBA CON MIKE:", Words_LINES)
            REQUEST = Words_LINES[0]
            LINE_SIP = Words_LINES[1].split(":")
            nonce = "898989898989898989898989898988989"
            print("Esto es mi split de lo que me manda el cliente" , Words_LINES)
            print("La peticion es: ", REQUEST)
            print("Listening...")


        
            


            if REQUEST == 'REGISTER':
                
                print(len(Words_LINES))
                if len(Words_LINES) == 8:


                    '''COMPROBACION DE LAS CONTRASEÑAS'''

                    Words_LINES = LINE.split()
                    LINE_SIP = Words_LINES[1].split(":")
                    USUARIO_SIP = LINE_SIP[1]
                    print(Words_LINES)
                    response = Words_LINES[7].split("'")[1]
                    print("response: ", response)
                    
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
                        elif exp_response != response:
                            self.wfile.write(b"SIP/2.0 412 Conditional Request Failed\r\n\r\n") 
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
                        elif exp_response != response:
                            self.wfile.write(b"SIP/2.0 412 Conditional Request Failed\r\n\r\n")
                            break
                    
                    print("LINE_SIP:" , LINE_SIP)
                    self.json2registered()
                    USUARIO_SIP = LINE_SIP[1]
                    print(USUARIO_SIP)
                    PUERTO_SIP = LINE_SIP[2]
                    print("Este es el puerto sip de la linea que nos envia el cliente: ", PUERTO_SIP)
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
        

                    now = int(time())
                    #str_now = strftime('%Y-%m-%d %H:%M:%S', gmtime(now))
                    time_exval = int(Expires) + now
                    #str_exp = strftime('%Y-%m-%d %H:%M:%S', gmtime(time_exval))

                    self.dicc[USUARIO_SIP] = {'address' : DIR_ip, 'port' : PUERTO_SIP,  'expires' : time_exval}
                    #self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
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
                    print("Enviamos un 401 Unauthorized")
                    LINE_SIP = ("SIP/2.0 401 Unauthorized\r\n\r\n")
                    LINE_DIGEST = LINE_SIP + "WWW Authenticate: Digest "
                    LINE_DIGEST += "nonce=" + "'" + nonce + "'" 
                    self.wfile.write(bytes(LINE_DIGEST, 'utf-8'))

                    
                    
                    

  
            elif REQUEST == 'INVITE':
                print("Imprimiendo sabiendo que es un invite: ", Words_LINES)
                
                USUARIO_SIP = LINE_SIP[1]
                #print("USUARIO_SIP", USUARIO_SIP)
                US_INVITE = Words_LINES[1].split(":")[1]
                #print("US_INVITE", US_INVITE)
                US_ORIGIN = Words_LINES[6].split("=")[1]
                

                print("Este es el usuario al que queremos invitar" , US_INVITE)
                with open('registered.json') as file:
                    data = json.load(file)
                    datos = data
                    #print("IMPRIMIENDO EL DICCIONARIO", data)
                    #dataipdata = data[USUARIO_SIP]['address']
                    #print("ESTO ES DATA IP DATA", dataipdata)
                    
                    

                    for user in data:
                        if user == US_INVITE:
                            print("PODEMOS COMUNICARNOS CON ESTE USUARIO!")
                            print('Este es el usuario o usuarios registrados', user)
                            print("Este es el usuario al que queremos invitar: ", US_INVITE)
                            dataipdata = data[USUARIO_SIP]['address']
                            dataportdata = data[USUARIO_SIP]['port']
                            print("Puerto del invitado", dataportdata)
                            '''SOCKET'''
                            # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
                            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            my_socket.connect((dataipdata,int(dataportdata)))
                            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
                            data = my_socket.recv(1024)
                            print("Hemos recibido del servidor:", "\r\n")
                            print(data.decode('utf-8'))
                            WERECEIVE = data.decode('utf-8').split('\r\n\r\n')[0:-1]
                            WERECEIVE_CODES = WERECEIVE[:3]
                            WERECEIVE_SDP = WERECEIVE[3:]
                            SDP_SPLIT = WERECEIVE[4].split("\r\n")
                            VERSION = WERECEIVE[4].split("\r\n")[0]
                            ORIGIN = SDP_SPLIT[1]
                            SESION = SDP_SPLIT[2]
                            TIME = SDP_SPLIT[3]
                            MULTIMEDIA = SDP_SPLIT[4]
                            
                            
                            answer = WERECEIVE_SDP[0] + "\r\n" 
                            answer +=  VERSION + "\r\n" + ORIGIN + "\r\n" + SESION
                            answer += "\r\n" + TIME + "\r\n" + MULTIMEDIA
                            
                            
                            
                            print("Prueba del WE RECEIVE: ", WERECEIVE)    
                            MUSTRECEIVE100 = ("SIP/2.0 100 Trying")
                            MUSTRECEIVE180 = ("SIP/2.0 180 Ring")
                            MUSTRECEIVE200 = ("SIP/2.0 200 OK")
                            MUSTRECEIVE = [MUSTRECEIVE100, MUSTRECEIVE180, MUSTRECEIVE200]
                            #print("WERECEIVE_CODES", WERECEIVE_CODES)
                            #print("MUSTRECEIVE", MUSTRECEIVE)

                            if WERECEIVE_CODES == MUSTRECEIVE:
                                self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n")
                                self.wfile.write(b"SIP/2.0 180 Ring\r\n\r\n")
                                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")  
                                self.wfile.write(bytes(answer, 'utf-8'))  

                            
                            
                        elif user != US_INVITE and user != US_ORIGIN:
                            self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")
                            
            elif REQUEST == 'ACK':
                LINE = text.decode('utf-8')
                LINE_ACK = LINE
                print(LINE)
                USUARIO_SIP = LINE_SIP[1]
                print('USUARIO_SIP:' , USUARIO_SIP)
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
                            my_socket.connect((dataipdata,int(dataportdata)))
                            my_socket.send(bytes(LINE_ACK, 'utf-8') + b'\r\n')
                            data = my_socket.recv(1024)
                            print(data.decode('utf-8'))
                            
            elif REQUEST == 'BYE':
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
                            my_socket.connect((dataipdata,int(dataportdata)))
                            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
                            data = my_socket.recv(1024)
                            print(data.decode('utf-8'))
                            MUSTRECEIVE200 = ("SIP/2.0 200 OK")
                            MUSTRECEIVE = [MUSTRECEIVE200]
                            WERECEIVE = data.decode('utf-8').split('\r\n\r\n')[0:-1]
            
                            if WERECEIVE == MUSTRECEIVE:
                                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                #Ahora debemos volver a entrar en el fichero y coger para el usuario sip
                # su puerto del servidor para poder enviarle un ACK 
                         
                            
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break







if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((PROXY_IP,int(PROXY_PORT)), EchoHandler)
    print("Server " + PROXY_NAME + " listening at port " + PROXY_PORT + " ..." )
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado PROXY")
