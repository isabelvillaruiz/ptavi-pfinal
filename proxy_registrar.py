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


''' READING AND EXTRACTION OF XML DATA'''

#FIRST PARAMETER : XML FILE 
XML_DATA = sys.argv[1]
#SECOND PARAMETRER : REQUEST
#REQUEST = sys.argv[2]

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
print("Esta es la ip del proxy: ", PROXY_IP)
PROXY_PORT = data[0]['server']['puerto']
print("Este es el puerto del proxy: ", PROXY_PORT)

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
            print("Esto es mi split de lo que me manda el cliente" , Words_LINES)
            print("La peticion es: ", REQUEST)
            print("Listening...")


        
            


            if REQUEST == 'REGISTER':


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
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                lista_expirados = []
                for user in self.dicc:
                
                    if self.dicc[user]['expires'] <= now:
                        lista_expirados.append(user)
                for name in lista_expirados:
                    del self.dicc[name]
                self.register2json()
                print(self.dicc)     
                

  
            elif REQUEST == 'INVITE':
                print("Imprimiendo sabiendo que es un invite: ", Words_LINES)
                #print(self.dicc)
                USUARIO_SIP = LINE_SIP[1]
                
                US_INVITE = Words_LINES[1].split(":")[1]
                US_ORIGIN = Words_LINES[6].split("=")[1]
                

                print("Este es el usuario al que queremos invitar" , US_INVITE)
                with open('registered.json') as file:
                    data = json.load(file)
                    datos = data
                    #print("IMPRIMIENDO EL DICCIONARIO", data)
                    dataipdata = data[USUARIO_SIP]['address']
                    
                    print(dataipdata)
                    
                    for user in data:
                        print('Este es el usuario o usuarios registrados', user)
                        print("Este es el usuario al que queremos invitar: ", US_INVITE)
                        if user == US_INVITE:
                            print("PODEMOS COMUNICARNOS CON ESTE USUARIO!")
                            dataportdata = data[USUARIO_SIP]['port']
                            print("Puerto del invitado", dataportdata)
                            '''SOCKET'''
                            # Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
                            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            my_socket.connect((dataipdata,int(dataportdata)))
                            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
                            data = my_socket.recv(1024)
                            print(data.decode('utf-8'))
                            WERECEIVE = data.decode('utf-8').split('\r\n\r\n')[0:-1]
                            print("Prueba del WE RECEIVE: ", WERECEIVE)    
                            MUSTRECEIVE100 = ("SIP/2.0 100 Trying")
                            MUSTRECEIVE180 = ("SIP/2.0 180 Ring")
                            MUSTRECEIVE200 = ("SIP/2.0 200 OK")
                            MUSTRECEIVE = [MUSTRECEIVE100, MUSTRECEIVE180, MUSTRECEIVE200]


                            if WERECEIVE == MUSTRECEIVE:
                                self.wfile.write(b"SIP/2.0 100 TRYING\r\n\r\n")
                                self.wfile.write(b"SIP/2.0 180 RINGING\r\n\r\n")
                                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")  
                            
                        elif user != US_INVITE and user != US_ORIGIN:
                            self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")
                            
                            
                            
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break







if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((PROXY_IP,int(PROXY_PORT)), EchoHandler)
    print("Lanzando servidor PROXY de eco...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado PROXY")
