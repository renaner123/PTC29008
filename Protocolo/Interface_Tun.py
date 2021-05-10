#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 10:24:35 2018

@author: msobral
"""

import poller
import sys,time
from tun import Tun
import struct

class Tun_Tun(poller.Callback):

    Proto_Tun = 2048#
    
    def __init__(self, tun):
        poller.Callback.__init__(self, tun.fd, 1000)
        self.tun_rcv = tun
        self.disable()
        self.value_icmp = bytearray()

    def handle(self):
        prto,l = self.tun_rcv.get_frame()
        if(prto==2048)and(len(l)>2):
            print("Proto (Tx)",prto)
            self.envia_fake.Send_to_Arq(l)

    def handle_timeout(self):
        pass


    def Desativa_Camada_Tun(self):
        ''' Desativa o monitoramento de teclado
        '''
        self.disable()

    def Ativa_Camada_Tun(self):
        ''' Ativa o monitoramento de teclado
        '''
        self.enable()        

    def Tun_send(self,obj):
        ''' Recebe objeto do Arq para chamar o Fsm_arq.
        '''
        self.envia_fake = obj
    
    
    def NotifyLayer(self,get_ping):      
        print("Proto (Rx)",self.Proto_Tun)
        self.tun_rcv.send_frame(get_ping,self.Proto_Tun)
        #print(self.value_icmp)

        #get
        
        
