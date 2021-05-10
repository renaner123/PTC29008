#!/usr/bin/python3
# -*- coding: utf-8 -*- 

""" @author: Renan Rodolfo & Marina Souza
"""

import poller
import sys,time
from ARQ import Arq
from session_manage import Session_Manager

class Fake_app(poller.Layer):
    ''' Camada utilizada para o poller.py monitorar o evento do teclado 
    '''

    def __init__(self, obj, timeout=5):     
        self.timeout = timeout
        self.base_timeout = timeout
        self.fd = obj
        self.disable()
        self.disable_timeout()
        self.recebe_app = None
 
    def handle(self):
        ''' Recebe algo do teclado e encaminha para Fsm_arq encapsular informações de um quadro
        '''
        quadro = sys.stdin.readline()                
        self.recebe_app = quadro[:-1]     
        self.envia_fake.Send_to_Arq(self.recebe_app)

    def handle_timeout(self):
       pass
        #print('Timeout !')
    def Desativa_Camada_TOP(self):
        ''' Desativa o monitoramento de teclado
        '''
        self.disable()

    def Ativa_Camada_TOP(self):
        ''' Ativa o monitoramento de teclado
        '''
        self.enable()        

    def Fake_send(self,obj):
        ''' Recebe objeto do Arq para chamar o Fsm_arq.
        '''
        self.envia_fake = obj#


   

        
