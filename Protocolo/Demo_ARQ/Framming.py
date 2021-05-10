#!/usr/bin/python3
from random import randint
from operator import xor
import serial
import poller
import sys, time
import crc

class Enquadramento(poller.Layer):
    ocioso = 1
    recp = 2
    Escape = 3
    
    def __init__(self,dev):
        #self.port = port  # Pega porta fornecida pelo usuario
        # Passando argumentos para o fileobj e o timeout para o construtor do CallBack do poller.py
        # INSERIR TAMANHO MAXIMO DE 1024
        self.dev = dev
        poller.Callback.__init__(self, dev, timeout=5)
        self.fd = dev
        self.state = self.ocioso  # definindo estado inicial da fsm
        self.buffer = []  # Buffer para armazenar os bytes lidos
        self.n = 0  # Contador de byte válido recebido
        self.base_timeout = self.timeout
        self.disable_timeout()
        self.bit = self.fd
        self.fcs = crc.CRC16(" ")
        self.temp = None
        self.quadro = False  # Usado para informa que recebeu um quadro completo.

    def notifyLayer(self, date):
        self.To_Framming.recebe_serial(date)

    def vem_top(self,obj):
        self.To_Framming = obj
    
    def Close_Conection(self):
        self.fd.close()
        print("Conexão foi encerrada")

    #FIXME Envia Byte
    def envia_byte(self,dado):
        #converter int para str
        #dado = str(dado[0])+str(dado[1])+str(dado[2])+str(dado[3])
        dados_quadro = dado[0:3]
        dados_msg = dado[3:len(dado)]   

        if(len(dado)<=1024):
            self.temp = dados_msg
           # print("entrou no envia byte",self.temp) 

            self.fcs.clear()
            self.fcs.update(self.temp)
            msg = self.fcs.gen_crc()        


            crc_value = (msg[len(self.temp ):len(msg)])

            for see in self.temp:
                if (see == ord("~")) or (see == ord("}")) or (see == ord("^")) or (see == ord("]")):         
                    aux_Dec = (see)
                    aux_Stuff = aux_Dec ^ 32
                    volta_Stuff = (aux_Stuff)
                    self.temp = self.temp .replace(chr(see).encode(), b"}" + chr(volta_Stuff).encode())
                    break                      

            aux_len = len(self.temp)
            aux = ((self.temp [:0] + b"~" +dados_quadro +self.temp [0:aux_len]))
            self.temp  = bytearray(aux + crc_value + b'~')
            
            self.dev.write(self.temp)
           # print("saindo do envia byte",self.temp)

            


    def handle(self):  # chamado pelo poller
        self.bit = self.fd.read(1)  # Lendo um byte da serial através fd do poller.
        self.handle_fsm(self.bit)  # Jogando o byte lido para a máquina de estado analisar

    def handle_timeout(self):
        print('Timeout !')
        self.handle_fsm(" ")  # Isso é para conseguir analisar quando quadro estiver incompleto

    def handle_fsm(self, octeto):
        self.bit = octeto        

        if (self.bit == " "):
            self.state = self.ocioso  # Caso ocorra timeout, descarta o buffer e começa novamente
            self.n = 0
            self.buffer = []
            self.disable_timeout()
            return
        else:
            # Se recebeu um quadro, esvazia o buffer e futuramente envia notificação para camada a cima
            if (self.quadro == True):
                self.buffer = []
                self.quadro = False

            while True:
                # Sempre inicia aqui, pois foi definido no construtor.
                if (self.state == self.ocioso):
                    if (self.bit == b'~' and self.n == 0):
                        self.state = self.recp
                        self.enable_timeout()  # Ativa o timeout somente quando estiver recebendo alguma coisa da serial
                        return
                    else:
                        self.state = self.ocioso
                        self.disable_timeout()
                        return #

                elif (self.state == self.recp):
                    if (self.bit == b'~' and self.n > 0):
                        self.quadro = True
                        lista_aux = ""
                        # Transformado o byte em string para conseguir armazenar na lista.
                        for xx in self.buffer:
                            xx = chr(xx)
                            lista_aux += xx
                       # print("recebeu um quadro completo de:", len(self.buffer), "Bytes", "-", lista_aux[:-2], "-")
                        #fail
                        self.fcs.clear()
                        #self.fcs.update(bytearray(self.buffer[:-1])) #testa com falha
                        self.fcs.update(bytearray(self.buffer[3:len(self.buffer)]))   
                       # print("Buffer que vai no check", bytearray(self.buffer))                    
               
                        if(self.fcs.check_crc()==True):
                            self.notifyLayer(bytearray(self.buffer[:-2])) 
                        else:
                            print("Quadro perdeu algum byte") 
                            self.buffer = [] 
                            self.notifyLayer(bytearray("erro".encode()))
                            self.disable_timeout()
                            return
                
                        #FIXME 
                        self.buffer = []
                        self.n = 0
                        # Informa que recebeu um quadro completo
                        self.quadro = True
                        self.state = self.ocioso
                        self.disable_timeout()
                        return
                    # Como recebeu um quadro, volta para o ocioso até receber outro byte.

                    elif (self.bit == b'~' and self.n == 0):
                        self.state = self.recp
                        return
                    elif (self.bit == b'}'):
                        self.state = self.Escape

                    elif (self.bit != b"~" and self.bit != b"}"):
                        if (self.bit != b""):
                            self.buffer += (self.bit)
                            self.n = self.n + 1
                            self.state = self.recp
                            return
                        else:
                            self.state = self.ocioso
                    else:
                        self.buffer = []
                        self.state = self.ocioso
                        self.disable_timeout()

                elif (self.state == self.Escape):
                    if (self.bit == b'~'):
                        self.buffer = []
                        print("Zerou o buffer", self.buffer)
                        self.state = self.ocioso
                        self.fim = 1
                        self.disable_timeout()
                    elif (self.bit == b'}'):
                        self.bit = self.fd.read(1)
                        # Procedimento que faz o xor 20H dos bytes para conseguir encaminhar no meio da mensagm
                        aux_Dec = ord(self.bit)
                        aux_Stuff = aux_Dec ^ 32
                        # volta_Stuff = chr(aux_Stuff)
                        self.buffer.append(aux_Stuff)
                        self.n = self.n + 1
                        self.state = self.recp
                    return


##
# port_int = input(("Digite caminho da porta serial \n"))
# while True:
