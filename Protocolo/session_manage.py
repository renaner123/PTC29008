#!/usr/bin/python3
# -*- coding: utf-8 -*- 
""" @author: Renan Rodolfo & Marina Souza
"""

import sys, enum
import serial #Necessario comentar para pydoc aceitar
import poller
import time
import crc
import pydoc



class Session_Manager(poller.Layer):
    ''' Camada responsável por contruir camada de Gerenciamento de Sessão

        Algumas váriaveis globais:
        cr: conection request
        cc: conection confirm
        Kr: Keep Alive Request
        kc: Keep Alive confirm
        dr: desconection request
        dc: Desconection Confirm
        ca: Connect Acknowledge
        start: 9 Usado para iniciar enviando um cr
        ID_Session: Identifica o número da sessão estabelecida
        ID_Proto_session: Identifica que um quadro é para o Gerenciamento de Sessão
        ID_Proto_ARQ: Identifica que que é um quadro para o ARQ    
    
    '''

    cr = 0   #conection request
    cc = 1   #conection confirm
    Kr = 2   #Keep Alive Request
    kc = 3   #Keep Alive confirm
    dr = 4   #desconection request
    dc = 5   #Desconection Confirm
    ca = 7   #Connect Acknowledge#
    start = 9
    ID_Session = 50
    ID_Proto_session = 255
    ID_Proto_ARQ = 0
    Disc = 0
    Hand1 = 1
    Hand2 = 2
    Con = 3
    Check = 4 
    Half1 = 5 
    Half2 = 6
    DATA0 = 0x00  #0000000
    DATA1 = 0x08  #0001000


    def __init__(self, obj, timeout=5):
        ''' Recebe como parâmetro None como  objeto e um valor de Timeout desejado, que por padrão 
            está 5.

            Aux_con: Utilizado quando os dois lados tem a iniciativa de estabelecer uma conexão e estão no estado Hand1
            On_OFF_TOP: Utilizado para ativar e desativar a camada superior
            quadro_controle: Recebe o quadro que deverá ser enviado para o Gerenciamento de Sessão.
        '''
        self.timeout = timeout
        self.teste_event = False
        self.enable()
        self.base_timeout = timeout
        self.state = self.Disc
        self.fd = obj
        self.disable_timeout()
        self.quadro_controle = bytearray()
        self.cont_timer = 0
        self.quadro_fake = bytearray()
        self.quadro_Tun = bytearray()
        self.On_Off_TOP = None
        self.On_OFF_Tun = None
        self.Aux_con = 0
        self.N = 0

    def handle_timeout(self):
        ''' Chamada pelo poller.py quando ocorre um evento de timeout.
        '''
       # print(self.state,self.cont_timer)
        if(self.state==self.Con):                      
            if(self.cont_timer==2):
                #print("Fazendo checkinterval")
                self.Mock_Quadro()
                self.check_interval_Time()
                self.quadro_controle.append(self.Kr)
                self.state = self.Check
                self.envia_bot.Fsm_arq(self.quadro_controle)
                self.cont_timer = 0      
            
        elif(self.state == self.Check):
            print("Check - Não recebi KC, voltar para Disc")  
            self.state = self.Disc
            self.disable_timeout()
        elif(self.state == self.Hand1):
            if(self.cont_timer<=2):
                print("Enviando Cr Novamente")
                self.envia_bot.Fsm_arq(self.quadro_controle)
            else:
                print("Limite de tentativas atingido, voltando para Disc") 
                self.state = self.Disc   
        elif(self.state == self.Hand2):
            if(self.cont_timer==2):
                self.state = self.Disc   
        elif(self.state == self.Half2):
            #if(self.cont_timer==3):
            print("Hand2 - Voltando para Disc")
            self.state = self.Disc
        elif(self.state == self.Half1):
            self.Mock_Quadro()
            self.quadro_controle.append(self.dr)
            self.envia_bot.Fsm_arq(self.quadro_controle)
        elif(self.state == self.Disc):
            self.disable_timeout()    
        self.cont_timer += 1    
                         
    
    def handle(self):
        ''' Não utilizado
        '''
        pass


    def get_Arq(self,obj):                #recebendo objeto do enquadramento para enviar os quadros de controle
        ''' Recebe um objeto do tipo Enquadramento ao iniciar do sistema(Envia.py e recebe.py)
        '''
        self.envia_bot = obj        
        

    def Send_to_Arq(self, quadro):                #enviar para camada de baixo
        ''' Recebe um quadro e encaminha para o envia_byte do Enquadramento, para jogar na serial
        '''
        self.quadro_fake = bytearray(([self.ID_Proto_session]))
        self.quadro_Tun = bytearray(([48]))
        if(type(quadro)==bytes):
            for see in quadro:
                self.quadro_Tun.append((see))
            self.envia_bot.Fsm_arq(self.quadro_Tun)       
        else:    
            for see in quadro:
                self.quadro_fake.append(ord(see))
            self.envia_bot.Fsm_arq(self.quadro_fake)
      
    
    def Get_Fake(self, obj):
        ''' Recebe um objeto da camada Fake utilizada para ter interação com o teclado e pode ativar/desativar
            o gerenciamento de eventos do poller sobre ele.
        '''
        self.On_Off_TOP = obj

    def Get_Tun(self, obj):
        ''' Recebe um objeto da camada Tun utilizada para Ativar/Desativar a camada.
        '''
        self.On_OFF_Tun = obj
        


    def Start_Conection(self):
        ''' Quando um lado chamada esse método, ele joga para o Recebe_arq() um valor 9, que a máquina
            identifica como start e envia um cr para tentar iniciar uma conexão.
        '''
        self.start_conection = bytearray(bytes([9]))        #envia um start para maquina de estado
        self.Recebe_arq(self.start_conection)
        #print("enviando Cr e mudando para state hand1")
        #self.start = bytearray(bytes([0,self.ID_Session,self.ID_Proto_session,self.cr]))  #apenas pra mandar quadro com cr
        #obj.envia_byte(self.start)   

                  
    def Mock_Quadro(self):
        ''' Retorna um quadro padrão com valor de ID Proto utilizado para enviar
            mensagens de controle para o Gerenciamento de Sessão.        '''
        self.quadro_controle = bytearray()       
        self.quadro_controle.append(self.ID_Proto_session)
        #self.N = 1
        

    def Recebe_arq(self,quadro):
        ''' Recebe um quadro da camada ARQ, que contenha ID_Proto_session com valor 255 e joga para 
            a máquina de estado fazer o processamento.

            A máquina possui os seguintes estados: 
                DISC: desconectado
                HAND1: em negociação para estabelecimento de conexão, quando tomou a iniciativa de estabelecê-la
                HAND2: em negociação para estabelecimento de conexão, quando o outro lado tomou a iniciativa
                CON: conectado
                CHECK: aguardando resposta para Keep Alive
                HALF1: em estado de terminação de enlace (half-close), quando tomou a iniciativa de terminá-lo
                HALF2: em estado de terminação de enlace (half-close), quando o outro lado tomou a iniciativa 

        '''
        self.Aux_con = 0
        self.enable_timeout()
        self.reload_timeout()
	
        if(self.state==self.Disc):       #conection request
            self.On_Off_TOP.Desativa_Camada_TOP()
            self.On_OFF_Tun.Desativa_Camada_Tun()
            self.disable_timeout()
            if(quadro[0]==self.start):
                self.state = self.Hand1
                print("Disc - enviando Cr e mudando para",self.state)
                self.enable_timeout()
                self.reload_timeout()
                self.Mock_Quadro()
                self.quadro_controle.append(self.cr)
                self.envia_bot.Fsm_arq(self.quadro_controle)
            elif(quadro[0]==self.cr):
                self.state = self.Hand2
                print("Disc - Recebi Cr, enviando Cc e mudando para",self.state)                
                self.Mock_Quadro()
                self.quadro_controle.append(self.cc)
                self.envia_bot.Fsm_arq(self.quadro_controle)
                return
        elif(self.state==self.Hand1):
            if(quadro[0]==self.start):
                self.state = self.Con  
                print("Hand1 - recebi start, enviar ca e mudando para",self.state)                   
                self.On_Off_TOP.Ativa_Camada_TOP()
                self.On_OFF_Tun.Ativa_Camada_Tun()    
                self.Mock_Quadro()         
                self.quadro_controle.append(self.ca)
                self.envia_bot.Fsm_arq(self.quadro_controle)
                return              
            elif(quadro[0]==self.cc):
                self.state = self.Con
                print("Hand1 - Recebi cc, enviar ca e mudando para ", self.state)                
                self.On_Off_TOP.Ativa_Camada_TOP()
                self.On_OFF_Tun.Ativa_Camada_Tun() 
                self.Mock_Quadro()
                self.quadro_controle.append(self.ca)
                self.envia_bot.Fsm_arq(self.quadro_controle)
                self.disable_timeout()
                return 
            elif(quadro[0]==self.ca):
                self.enable_timeout()
                self.state = self.Con
                print("Hand1 - Recebi ca mudando para", self.state)
                self.Aux_con = 1
                #self.quadro_controle.append(self.dr)
                #self.envia_bot.envia_byte(self.quadro_controle)## testar dr no estado con    
                return
            elif(quadro[0]==self.cr):
                self.state = self.Hand1
                print("Hand1 - Recebi cr, enviar cc mudando ",self.state)
                self.Mock_Quadro()
                self.quadro_controle.append(self.cc)
                self.envia_bot.Fsm_arq(self.quadro_controle)
        
                return           
        elif(self.state==self.Hand2):
            if(quadro[0]==self.ca):
                self.state = self.Con
                print("Hand2 - Recebi ca, mudando para",self.state)               
                self.enable_timeout()
                self.On_Off_TOP.Ativa_Camada_TOP()
                self.On_OFF_Tun.Ativa_Camada_Tun() 
            elif(quadro[0]==self.dr):
                self.state = self.Half2
                print("Hand2 - Recebi dr, mudando para",self.state)
                self.Mock_Quadro()
                self.quadro_controle.append(self.dr)
                self.envia_bot.Fsm_arq(self.quadro_controle)             
                
                return
            elif(quadro[0]==self.dr):
                self.state=self.Half2
                print("Hand2 - Recebi dr, enviar dr mudando",self.state)
                self.Mock_Quadro()
                self.quadro_controle.append(self.dr)    
                self.envia_bot.Fsm_arq(self.quadro_controle)                              
                           
        elif(self.state==self.Con):   
            self.enable_timeout()     
            self.On_Off_TOP.Ativa_Camada_TOP()
            self.On_OFF_Tun.Ativa_Camada_Tun()    
            if(quadro[0]==self.dr):
                self.enable_timeout()
                self.state = self.Half2
                print("Con - Recebi um dr, enviar dr mudando ",self.state)
                self.Mock_Quadro()
                self.quadro_controle.append(self.dr)    
                self.envia_bot.Fsm_arq(self.quadro_controle)
                    
            elif(quadro[0]==8):
                print("Con - Ocorreu um close, enviar dr mudando",self.Half1)
                self.state = self.Half1
                self.enable_timeout()
                self.Mock_Quadro()
                self.quadro_controle.append(self.dc)
                self.envia_bot.Fsm_arq(self.quadro_controle)                              
            elif(quadro[0]==self.dc):
                self.state = self.Disc    
                print("Outro lado fechou o terminal, voltando ",self.state)
                self.disable_timeout()
            elif(quadro[0]==self.Kr):
                #print("Con - Recebi um Kr, enviar Kc mudando",self.state)
                self.state = self.Con
                self.Mock_Quadro()
                self.quadro_controle.append(self.kc)   
                self.envia_bot.Fsm_arq(self.quadro_controle) 
            elif(quadro[0]==self.ca):             
                self.On_Off_TOP.Ativa_Camada_TOP()
                self.On_OFF_Tun.Ativa_Camada_Tun() 
            elif(quadro[0]==20):
                self.enable_timeout()
                self.state = self.Half1      
                print("Close, enviar Dr mudando para",self.state)                                                                     #Erro de CRC
                self.Mock_Quadro()               
                self.quadro_controle.append(self.dr)
                self.envia_bot.Fsm_arq(self.quadro_controle)
            elif(quadro[0]==6):
                self.disable_timeout()      

        elif(self.state==self.Check):
            self.enable_timeout()
            self.check_interval_Time()
            self.On_Off_TOP.Ativa_Camada_TOP()
            self.On_OFF_Tun.Ativa_Camada_Tun() 
            if(quadro[0]==self.kc): 
                self.state = self.Con          
                #print("Check - Recebi um KC, mudando para",self.state)                      
            else:
                self.state = self.Disc
                #print("Check - Não recebeu Kc, voltando ",self.state)
                #self.envia_bot.Close_Conection()
                
        elif(self.state== self.Half2):
            self.enable_timeout()
            self.On_Off_TOP.Desativa_Camada_TOP()
            self.On_OFF_Tun.Desativa_Camada_Tun()
            if(quadro[0]==self.dr):
                self.state = self.Half2
                print("Half2 - Chegou um dr, enviando dr",self.state)
                self.Mock_Quadro()
                self.quadro_controle.append(self.dr)
                self.envia_bot.Fsm_arq(self.quadro_controle)    
                     
            elif(quadro[0]==self.dc):
                print("Recebi dc, vou para Disc")
                self.state = self.Disc                  
                
        elif(self.state==self.Half1):   
            self.enable_timeout()
            if(quadro[0]==self.dr):         
                print("Half1 - Recebi Dr, enviando dc")
                self.state = self.Disc
                self.enable_timeout()
                self.Mock_Quadro()
                self.quadro_controle.append(self.dc)
                self.envia_bot.Fsm_arq(self.quadro_controle)
            else:
                print("que acontece")
           
                

    
   

