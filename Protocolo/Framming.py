#!/usr/bin/python3
# -*- coding: utf-8 -*- 

""" @author: Renan Rodolfo & Marina Souza
"""

from random import randint
from operator import xor
import serial 
import poller
import sys, time
import crc

class Enquadramento(poller.Layer):
    ''' Essa camada é responsável por Contruir o Enquadramento e Detecção de erros com CRC-16.
    '''
    ocioso = 1
    recp = 2
    Escape = 3
    
    def __init__(self,dev):
        ''' Para contrui-lá é necessário passar como parâmetro o timeout desejado e o objeto 
            contendo as informações da serial para ser utilizado Ex.: 
            serial.Serial('/dev/pts/5', 9600, timeout=5)

            Funcionalidade de algumas variáveis.
            buffer: Onde será armazenado os quadros transmitods 
            bit: Onde é armazenado o que é lido da serial
            quadro: Apenas informa quando ocorre o recebimento de um quadro completo
            fcs: Recebe objeto do tipo CRC16 para efetuar o cálculo.
            temp: Utilizado para fazer o estufamento dos bytes recebidos
            
        '''
        self.dev = dev
        self.enable()
        poller.Callback.__init__(self, dev, timeout=5)
        self.fd = dev
        self.state = self.ocioso  # definindo estado inicial da fsm
        self.buffer = []  # Buffer para armazenar os bytes lidos
        self.n = 0  # Contador de byte válido recebido#
        self.base_timeout = self.timeout
        self.disable_timeout()
        self.bit = self.fd
        self.fcs = crc.CRC16(" ")
        self.temp = None
        self.quadro = False  # Usado para informa que recebeu um quadro completo.


    def handle(self):  # chamado pelo poller
        ''' Evento onde o poller.py fica monitorando a serial que foi passada no construtor
            assim que lê um byte, joga para máquina de estado handle_fsm() para enquadrar.
            Caso
        '''
        self.bit = self.fd.read(1)  # Lendo um byte da serial através fd do poller.
        self.handle_fsm(self.bit)  # Jogando o byte lido para a máquina de estado analisar

    def handle_timeout(self):
        print('Timeout !')
        self.handle_fsm(" ")  # Isso é para conseguir analisar quando quadro estiver incompleto




    def notifyLayer(self, date):
        ''' Notifica o ARQ quando acaba o Enquadramento e não ocorre nenhum erro no CRC16
        '''
        self.To_Framming.recebe_serial(date)
#
    def vem_top(self,obj):
        ''' Recebe um objeto do tipo ARQ para utilizar o método recebe_serial() do mesmo.
            Responsável por enviar esse objeto é Envia.py e recebe.py ao iniciar.
        '''
        self.To_Framming = obj
    
    def Close_Conection(self):
        ''' Utilizado para fechar a conexão da serial utilizada.
        '''
        self.fd.close()
        print("Conexão foi encerrada")

    #FIXME Envia Byte
    def envia_byte(self,dado):
        ''' Recebe um quadro, faz o cálculo do CRC16 da informação contida no quadro, faz o estufamento
            e logo em seguida escreve na serial, contendo as identificações do quadro + informação com CRC. 

        '''


        if(len(dado)<=1024):                            #limitando o quadro a 1024 bytes

            self.temp = dado
            self.fcs.clear()
            self.fcs.update(self.temp)
            msg = self.fcs.gen_crc()  


            crc_value = (msg[len(self.temp ):len(msg)])
            aux_temp = bytearray()
            for see in self.temp:
                if (see == ord("~")) or (see == ord("}"))or (see == ord("}")):         
                    aux_Stuff = see ^ 32
                    aux_temp.append(int.from_bytes(b'}', 'big'))
                    aux_temp.append(aux_Stuff)
                else:
                    aux_temp.append(see)
            self.temp = bytearray()        
            self.temp = aux_temp                 

            aux_len = len(self.temp)
            aux = ((self.temp [:0] + b"~" +self.temp [0:aux_len]))
            self.temp  = bytearray(aux + crc_value + b'~')
            self.dev.write(self.temp)
            #print("Enviando",self.temp)	    
          


    def handle_fsm(self, octeto):
        ''' Essa máquina possui 3 estatos: Ocioso, Recp e Escape.

            Quando ocorre evento na serial, recebe um byte no octeto, assim que chegar um "~"
            máquina identifica que se iniciou um quadro, passa para o estado Recp e análisa os
            próximos octetos, quando receber "~" ele faz o cálculo do CRC16, se estiver sem 
            nenhum erro, notifica a camada ARQ e volta para ocioso. Escape ocorre quando se chega
            algum octero "7D"

        '''
        self.bit = octeto        
        if (self.bit == " "):
            self.state = self.ocioso  # Caso ocorra timeout, descarta o buffer e começa novamente
            self.n = 0
            self.buffer = []
            self.disable_timeout()
            return
        else:
            if (self.quadro == True):
                self.buffer = []
                self.quadro = False

            while True:
                if (self.state == self.ocioso):
                    if (self.bit == b'~' and self.n == 0):
                        self.buffer = []
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
                        for xx in self.buffer:
                            xx = chr(xx)
                            lista_aux += xx
                        self.fcs.clear()
                        #self.fcs.update(bytearray(self.buffer[:-1])) #testa com falha
                        self.fcs.update(bytearray(self.buffer[:len(self.buffer)]))                 
                        #print("Recebendo",self.buffer)
                        if(self.fcs.check_crc()==True):
                            self.notifyLayer(bytearray(self.buffer[:-2])) 
                        else:
                            print("Quadro perdeu algum byte")     

                
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
                        aux_Dec = ord(self.bit)
                        aux_Stuff = aux_Dec ^ 32
                        self.buffer.append(aux_Stuff)
                        self.n = self.n + 1
                        self.state = self.recp
                    return


                
