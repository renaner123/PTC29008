#!/usr/bin/python3
#!-*- coding: utf-8 -*-

""" @author Renan Rodolfo da Silva
"""

from Coap_Client import *
#import poller
import Projeto2_pb2
import time


class CoapAPP(poller.Callback):
    '''
        Classe responsável por criar uma aplicação para utilizar o CoAP Client
    '''
    def __init__ (self,Placa,Sensores,Uris):
        '''
            Construtor do CoapAPP:
            Recebe como parâmetro o nome da placa, uma lista contento a lista de sensores e o destino da URI
            a ser enviado os dados. Nessa aplicação os valores enviados são gerados randomicamente.
        '''
        self.sched = poller.Poller()
        self.state = 0      
        self.timeout = 2
        self.base_timeout = 2
        self.fd = None
        self.disable_timeout()
        self.disable()       
        self.Placa = Placa
        self.Sensores = Sensores
        self.Uris = Uris
        self.start = "Start"
        self.Periodo = 0

    def handle(self):
        '''
            Não utilizado.
        '''
        pass

    def handle_timeout(self):
        '''
            handle_timeout nessa aplicação é responsável por receber o payload que o protocolo recebe do 
            servidor, que no caso é uma mensagem config contendo o periodo que o servidor deseja que seja
            transmitido os dados dos sensores. Essa mensagem é decodifica através do Protocol Buffers.
        '''

        #print("Timeout App",self.Periodo)
        date = self.Send.Teste_Get              #Pega o valor do payload recebido pela aplicação
        pos = date.find(0xff)      
        if(pos!=-1) or (pos>5):
            try:
                self.Decod_Protobuffer_config(date[pos+1:len(date)])
            except:
                pass
        self.start = "Aquisicao"
        Payload_App.Protobuffer_Payload()


    def Protobuffer_Payload(self):
        '''
            Gera a mensagem codificada com o Protocol Buffers e chama o método do protocolo 
            CoAP Client para enviar a mensagem, sendo esse método o Do_Post().
        '''
        self.payload_Date = None
        self.payload_config = None

        self.Send = COAP('::',self.Uris)

        Date = Projeto2_pb2.Mensagem()
        Config = Projeto2_pb2.Mensagem()
        Sensor1 = Projeto2_pb2.Sensor()
        Sensor2 = Projeto2_pb2.Sensor()	
        
        Config.config.periodo = 0
        Config.config.sensores.extend(self.Sensores)

        Sensor1.nome = self.Sensores[0]
        Sensor1.valor = random.randint(-20,50)	
        Sensor1.timestamp = int(time.time())

        Sensor2.nome = self.Sensores[1]
        Sensor2.valor = random.randint(0,100)  
        Sensor2.timestamp = int(time.time())          
        
        Date.dados.amostras.extend([Sensor1,Sensor2])

        Date.placa = self.Placa
        Config.placa = self.Placa
        
        if(self.start == "Aquisicao"):
            print("Date")
            self.payload_Date = Date.SerializeToString() 
            self.Send.Do_Post(self.Uris,self.payload_Date)

            
        elif(self.start == "Start"):
            print("Config")
            self.payload_config = Config.SerializeToString()        
            self.Send.Do_Post(self.Uris,self.payload_config)
            self.start = "Aquisicao"
            self.enable_timeout()
            self.enable()
            self.sched.adiciona(self)
            self.sched.despache()


    def Decod_Protobuffer_config(self,payload):
        '''
            Recebe como parâmetro um payload codificado pelo Protocol Buffers, nessa aplicação
            a decodificação foi necessária somente para se ter o valor do período que o servidor
            deseja que seja transmistdas os dados dos sensores.
        '''


        Config = Projeto2_pb2.Mensagem()
        try:
            Config.ParseFromString(payload)
        except:
            print(payload)
            
        if(Config.HasField('config')):
            periodo = (Config.config.periodo)
        self.Periodo = periodo
        self.Set_Periodo(periodo)   

    def Set_Periodo(self,periodo):   
        '''
            Recebe como parâmetro um valor em milisegundos e setar o timeout para envio de mensagens periódicas.
        '''

        self.base_timeout = int(periodo/1000)
        self.reload_timeout()
        self.enable_timeout()



Payload_App = CoapAPP("Renan",["Velocidade","Temperadura"],"/ptc")
Payload_App.Protobuffer_Payload()

p = poller.Poller()
p.adiciona(Payload_App)
p.despache()
