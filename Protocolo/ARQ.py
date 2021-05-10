#!/usr/bin/python3
# -*- coding: utf-8 -*- 
""" @author: Renan Rodolfo & Marina Souza
"""
import sys, enum
import serial
import poller
import crc
import sys
import time
import random


class Arq(poller.Layer):
    ''' ARQ e Aloha: Classe responsável por construir a camada de garantia de entrega 
        do tipo para-e-espera(ARQ) e controle de acesso ao meio(Aloha).
        
    '''
    ACK0  = 0x80  #1000000   128
    ACK1  = 0x88  #1001000   136
    DATA0 = 0x00  #0000000
    DATA1 = 0x08  #0001000
    ID_Session = 50
    ID_Proto_session = 255
    ID_Proto_ARQ = 0
    ID_Proto_Tun = 48

    

    def __init__(self, obj, timeout=5):
        '''Define a camada responsável pelo ARQ e Aloha, recebe como parâmetro o tempo de timeout e
        o objeto que será utilizado pelo "poller.py" para fazer o monitoramento dos eventos, que nesse
        caso será somente o Timeout, o objeto deverá ser None.

        As variaveis encontradas em "Data and other attributes defined here:" foram pré estabelecidos 
        para o funcionamento do protocolo exceto o ID_Session, ID_Proto_session e 
        ID_Preto_ARQ que foram definidos estaticamente por nós.   

        Funcionalidade de algumas variáveis.    
        state : Responsável pela máquina de estado
        envia_date_backoff: Caso receba Ack errado, após o backoff encaminha o Data espeficado pelo envia_date_backoff
        cont_reenvio: Limita a quantidade de tentativas de transmissão
        envia_bot: Irá receber o objeto do tipo Enquadramento para enviar quadros para camada de baixo#
        
         '''

        self.state = 0      
        self.timeout = timeout
        self.enable()
        self.base_timeout = timeout
        self.fd = obj
        self.disable_timeout()
        self.Date_esp = 0
        self.quadro = bytearray()
        self.N = 0
        self.M = 0
        self.envia_bot = None
        self.envia_date_backoff = 2
        self.cont = 0
        self.cont_reenvio = 3
        #self.ack_error = 0

    def get_framming(self,obj):                                #recebendo objeto do enquadramento
        ''' Recebe um objeto do tipo Enquadramento, responsável por enviar os quadros para camada de baixo.
            Quem envia esse objeto são Envia.py e recebe.py
        '''
        self.envia_bot = obj

    def get_Tun(self,obj):
        ''' Recebe um objeto do tipo Tun para notificar a aplicação quando 
            receber um quadro com proto diferente de 255
        '''
        self.send_To_Tun = obj

   
    def notifyLayer(self, date):                               #envia para camada de sessão quando proto for 255  
        ''' Retorna para a camada superior, que nesse caso é o session_manage, o quadro que chegar no 
        recebe_serial() e tiver o ID_Proto_Session = 255 .
        ''' 
        self.To_Session_Manager.Recebe_arq(date)
        
    def get_Manager(self,obj):      
        ''' Recebe  o objeto do tipo session_manage para ser utilizado no método notifyLayer(). 
            Responsável por enviar esse objeto é o Envia.py e recebe.py ao iniciar
        '''                          #recebe objeto manager     
        self.To_Session_Manager = obj


    def sendACK0(self):    
        ''' Envia para o Enquadramento um quadro contendo a informação do ACK0 mais as 
            informações de identificação da sessão.
            ACK0 = 0X80h = 128d
        '''     
        self.quadro = bytearray(([self.ACK0,self.ID_Session,self.ID_Proto_session]))
        self.envia_bot.envia_byte(self.quadro)  
    
    def sendACK1(self):
        ''' Envia para o Enquadramento um quadro contendo a informação do ACK1 mais as 
            informações de identificação da sessão
            ACK1 = 0X88h = 136d
        '''
        self.quadro = bytearray(([self.ACK1,self.ID_Session,self.ID_Proto_session]))
        self.envia_bot.envia_byte(self.quadro)

     
    def send_Data0(self):
        ''' Envia para o Enquadramento um quadro contendo a informação de Data0 mais as informações de identificação da sessão
            junto com a mensagem/informação a ser transmitda.
            Data0 = 0x00 = 0d
        '''
     
        self.quadro = bytearray(([self.DATA0,self.ID_Session]))
        self.quadro_Tun = bytearray(([self.DATA0,self.ID_Session]))
        if(type(self.recebe_app)==bytes):
            self.envia_bot.envia_byte(self.quadro_Tun+self.recebe_app)    
        else: 
            self.envia_bot.envia_byte(self.quadro+self.recebe_app)

        
    def send_Data1(self):
        ''' Envia para o Enquadramento um quadro contendo a informação de Data1 mais as informações de identificação da sessão
            junto com a mensagem/informação a ser transmitda.
            Data1 = 0x08 = 8d
        '''
        self.quadro = bytearray(([self.DATA1,self.ID_Session]))
        self.quadro_Tun = bytearray(([self.DATA1,self.ID_Session]))
        if(type(self.recebe_app)==bytes):
            self.envia_bot.envia_byte(self.quadro_Tun+self.recebe_app)    
        else:    
            self.envia_bot.envia_byte(self.quadro+self.recebe_app)


    def handle(self):
        '''Não está sendo utilizado
        '''
        pass
  
    def Aloha(self):
        ''' Foi definido o Aloha do tipo aleatório, onde cada Ack recebido irá fazer com que ocorra um
            Backoff() com tempo aleatório de 1 a 7, para evitar as colisões. Caso haja colisão, o quadro
            é descartado.
        '''
        if(self.state == 1):
            if(self.cont_reenvio == 0):                                 #limita quantidade de reenvio
                #print("Tempo de transmissão excedido")
                self.state = 0
                self.recebe_app = " "  
                self.cont_reenvio = 3
            else:
                self.state = 3    
        elif(self.state == 2):
            #print("Estouro backoff state 2")
            self.state = 0    
        elif(self.state == 3):
            #print("Estouro backoff state 3")
            if(self.envia_date_backoff==0):
                self.send_Data0()
                self.state = 1
                self.cont_reenvio = self.cont_reenvio + 1             
            elif(self.envia_date_backoff==1):
                self.send_Data1()
                self.state = 1   
            else:
                if self.N == 0 :
                    self.send_Data0()    
                    self.state = 1      
                elif self.N == 1 :
                    self.send_Data1()
                    self.state = 1   
                self.envia_date_backoff = 2  
                self.cont_reenvio = self.cont_reenvio - 1          #reenvia apenas 3 vezes  



    def Fsm_arq(self,recebe_fake):
        ''' Recebe uma mensagem proveniente das camadas fake/Tun e encaminha para o Enquadramento 
            com as inforamações de identificação de um quadro utilizando  os métodos send_Data0() 
            e send_Data1().
        '''
        self.recebe_app = recebe_fake
        if(self.state==0):
            if(self.N == 0):
                self.send_Data0()
                self.enable_timeout()
            elif(self.N == 1):
                self.send_Data1()
                self.enable_timeout()  
        elif(self.state>=1):
            if(self.M == 0):
                self.send_Data0()
                self.enable_timeout()
            elif(self.M==1):
                self.send_Data1()
                self.enable_timeout()     
        self.state = 1
      

    def handle_timeout(self):  
        ''' Timeout que está sendo monitorado pelo "poller.py" assim que a camada não estiver recebendo nem
            transmitindo nada.
        '''
        self.Aloha()    
                                  

    def recebe_serial(self,date):   
        ''' Recebe os quadros vindos do Enquadramento, verifica se possui informação de controle para 
            notificar a camada superior "session_manage" ou se é apenas informação da camada Fake/Tun
            date = 0 50 255 Info por exemplo 
            Caso o date[1] seja diferente do estabelecido, o quadro é descartado
            Caso o date[2] seja 255 e tenha dado de controle, será notificado para session_manage       
        '''   
        verifica = bytearray([0,1,2,3,4,5,7])              #mensagens de controle
        if(date[0] == 20):
            self.notifyLayer(date)
        if(date[1] == 50):                                 #verifica se esta na sesão
            if(date[0]== self.ACK0 or date[0]==self.ACK1): #se receber algum ack não joga para camada superior
                date.append(0)
                date[2] = 5                                #para não enviar para gerência
            if(date[2]==self.ID_Proto_Tun):
                self.send_To_Tun.NotifyLayer(date[3:])       
            elif(date[2]==self.ID_Proto_session and (date[3] in verifica)):  #se for para 255 e for dado de controle                                    
                self.notifyLayer(date[3:len(date)])                   
            if (date[0]) == (self.DATA0):               
                if self.Date_esp == 0:
                    self.Date_esp = 1      
                    self.sendACK0()
                    self.state = 0
                    if(date[2]==self.ID_Proto_Tun):
                        pass
                        #print(date[3:])
                    else:
                        if(len((date[3:]).decode())>1):   
                            print ((date[3:]).decode())
                elif self.Date_esp == 1:
                    self.sendACK0()
                    return
            elif (date[0]) == (self.DATA1):
                if self.Date_esp == 1:
                    self.Date_esp = 0
                    self.sendACK1()
                    self.state = 0
                    if(date[2]==self.ID_Proto_Tun):
                        pass
                        #print(date[3:0])
                    else: 
                        if(len((date[3:]).decode())>1):   
                            print ((date[3:]).decode())
                elif self.Date_esp == 0:
                    if(self.state==0):
                        self.sendACK1()
                        if(date[2]==self.ID_Proto_Tun):
                            #print(date[3:0])
                            pass
                        else:    
                            if(len((date[3:]).decode())>1):  
                                print((date[3:]).decode())
                    elif(self.state == 1):    
                        self.sendACK1() 
                    return     
            elif self.state == 1:                
                if self.N == 0 :
                    if (date[0])== (self.ACK0):
                        #print ("ACK0 Recebido \n ")
                        self.M = 1
                        self.state = 2
                        self.N = 1
                        self.backoff() 
                        #print("voltei pro handle?",self.N," ",self.state," " ,self.Date_esp)
                        return
                    elif (date[0]) ==(self.ACK1):
                        #print ("Recebeu ACK1, mas deveria ser ACK0")
                        #self.ack_error = 1
                        self.backoff()
                        self.state = 3
                        self.envia_date_backoff = 0
                        #self.send_Data0()      só vai enviar depois do backoff 
                        return             
                    
                elif self.N == 1:
                    if (date[0])== (self.ACK1):
                        #print ("ACK1 Recebido\n")                 
                        self.N = 0
                        self.state = 2
                        self.M = 0
                        self.backoff()
                        return
                    elif (date[0]) == (self.ACK0):
                        #print ("Recebeu ACK0 mas não ACK1.")
                        #self.ack_error = 1
                        self.backoff()
                        self.state = 3
                        self.envia_date_backoff = 1
                        #self.send_Data1()      #só vai enviar depois do backoff
                        return
        else:
           
            date = []   
            self.state = 0             

 

    
    



#
