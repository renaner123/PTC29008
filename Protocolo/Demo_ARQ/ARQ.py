#!/usr/bin/python3
import serial, sys, enum
import poller
import crc
import sys
import time
import random

class Arq(poller.Layer):
    ACK0  = 0x80  #1000000   128
    ACK1  = 0x88  #1001000   136
    DATA0 = 0x00  #0000000
    DATA1 = 0x08  #0001000
    ID_Session = 50
    ID_Proto_session = 1
    ID_Proto_ARQ = 0
    

    def __init__(self, obj, timeout=5):
        self.state = 0      
        self.timeout = timeout
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
        self.cont_reenvio = 0
        self.ack_error = 0

    def get_framming(self,obj):                                #recebendo objeto do enquadramento
        self.envia_bot = obj

    def notifyLayer(self, date):                               #envia para camada de sessão quando proto for 255   
        self.To_Session_Manager.Recebe_arq(date)

    def get_Manager(self,obj):                                #recebe objeto manager     
        self.To_Session_Manager = obj


    def sendACK0(self):    
        #if(self.cont==0):
         #   print("Enviado Ack1 Errado")
          #  self.quadro = bytearray(([self.ACK1,self.ID_Session,self.ID_Proto_session]))
           # self.envia_bot.envia_byte(self.quadro)               #APenas para na primeira mensagem, simular ack errado
        #else:
        print("Enviando o ACK0")      
        self.quadro = bytearray(([self.ACK0,self.ID_Session,self.ID_Proto_session]))
        self.envia_bot.envia_byte(self.quadro)
        self.cont += 1    
    
    def sendACK1(self):
        print("Enviando o ACK1")
        self.quadro = bytearray(([self.ACK1,self.ID_Session,self.ID_Proto_session]))
        self.envia_bot.envia_byte(self.quadro)

    def send_Data0(self):
        print("estou enviando data0")
        self.quadro = bytearray(([self.DATA0,self.ID_Session,self.ID_Proto_session]))
        for see in self.recebe_app:
            self.quadro.append(ord(see))
        self.envia_bot.envia_byte(self.quadro)

        
    def send_Data1(self):
        print("estou enviando data1")
        self.quadro = bytearray(([self.DATA1,self.ID_Session,self.ID_Proto_session]))
        for see in self.recebe_app:
            self.quadro.append(ord(see))
        self.envia_bot.envia_byte(self.quadro)


    def handle(self):
        pass
  

    def Fsm_arq(self,recebe_fake):
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
        if(self.state == 1):
            if(self.cont_reenvio == 3):                                 #limita quantidade de reenvio
                print("Tempo de transmissão excedido")
                self.state = 0
                self.recebe_app = " "  
                self.cont_reenvio = 0
            else:
                self.state = 3    
        elif(self.state == 2):
            print("Estouro backoff state 2")
            self.state = 0    
        elif(self.state == 3):
            print("Estouro backoff state 3")
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
                self.cont_reenvio = self.cont_reenvio + 1          #reenvia apenas 3 vezes                     
       

    def recebe_serial(self,date):      
        #print(date[0],date[1],date[2])


                   

                if (date[0]) == (self.DATA0):
                    if self.Date_esp == 0:
                        self.Date_esp = 1      
                        self.sendACK0()
                        self.state = 0
                        print ("Mensagem 0 recebida: ",(date[3:]).decode(),"\n")
                        return
                    elif self.Date_esp == 1:
                        self.sendACK0()
                        return
                elif (date[0]) == (self.DATA1):
                    if self.Date_esp == 1:
                        self.Date_esp = 0
                        self.sendACK1()
                        self.state = 0
                        print ("Mensagem 1 recebida: ", (date)[3:].decode(),"\n")
                        return
                    elif self.Date_esp == 0:
                        if(self.state==0):
                            self.sendACK1()
                            print ("Mensagem 1 recebida: ",(date[3:]).decode(),"\n")                    
                        elif(self.state == 1):    
                            self.sendACK1() 
                        return     

                elif self.state == 1:                
                    if self.N == 0 :
                        if (date[0])== (self.ACK0):
                            print ("ACK0 Recebido \n ")
                            self.M = 1
                            self.state = 2
                            self.N = 1
                            self.backoff() 
                            #print("voltei pro handle?",self.N," ",self.state," " ,self.Date_esp)
                            return
                        elif (date[0]) ==(self.ACK1):
                            print ("Recebeu ACK1, mas deveria ser ACK0")
                            self.ack_error = 1
                            self.backoff()
                            self.state = 3
                            self.envia_date_backoff = 0
                            #self.send_Data0()      só vai enviar depois do backoff 
                            return             
                        
                    elif self.N == 1:
                        if (date[0])== (self.ACK1):
                            print ("ACK1 Recebido\n")                 
                            self.N = 0
                            self.state = 2
                            self.M = 0
                            self.backoff()
                            return
                        elif (date[0]) == (self.ACK0):
                            print ("Recebeu ACK0 mas não ACK1.")
                            self.ack_error = 1
                            self.backoff()
                            self.state = 3
                            self.envia_date_backoff = 1
                            #self.send_Data1()      #só vai enviar depois do backoff
                            return

 

    



