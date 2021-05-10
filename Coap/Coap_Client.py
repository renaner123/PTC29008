#!/usr/bin/python3
#!-*- coding: utf-8 -*-

""" @author Renan Rodolfo da Silva
"""
import socket
import random
import poller
import sys,time
import Projeto2_pb2

class COAP(poller.Callback):
    '''
         Classe responsável por construir o protocolo CoAP Client
    '''

    end = 0xFF                                      #Indica final das options
    idle = 0                                        #idle,wait e wait2 são os estados do protocolo
    wait = 1
    wait2 = 2                                       
    MAX_RETRANSMIT = 4                              # Quantidade de retransmissão
    ACK_TIMEOUT = 2                                 # Valor inicial do timeout de retransmissão       
    ACK_TIMEOUT_FACTOR = random.uniform(1,1.5)      # Fator para aumento exponencial do timeout 
    Delta1_Path = 0xB0                              # 11  Valor correspondente ao Option Number Uri-Path
    Delta2_Path = 0x00                            
    Teste_Get = None                                #Variável auxiliar para passar payload para App
    
    def __init__(self, ip,Uri):
        '''
            Construtor do CoAP:
            Recebe como parâmetro um IP(IVP6) mais a Uri que será utilizada como destino ao enviar mensagens
            para o servidor. 
            Cria um socket e vincula-o com o IP fornecido.
        '''

        global Teste_Get
        self.Poll = poller.Poller()                 #Objeto que fará o despache dos datagramas
        self.ip = ip
        self.servidor = (ip,5683)
        self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.bind((ip, 0))
        self.fd = self.sock
        self.enable()
        self.disable_timeout()
        self.base_timeout = 2 * self.ACK_TIMEOUT_FACTOR
        self.timeout = 2 * self.ACK_TIMEOUT_FACTOR
        self.First_Byte = 0x41                   # Indica Confirmavel(0), Não-Confirmável(1),Confirmação(2) ou Reset(3) 2bits                                      # tamannho do token a ser usado
        self.code_Get = 0x01                     # GET Class 000 Detail 00001        #Ack é T 10 e code 0.00
        self.code_Post =0x02
        self.code_Put = 0x03
        self.code_Delete = 0x04                  # Valores que foram definidos segundo a RFC 7252 para envio de mensagem COAP   
        self.code_Content_Format = 0x45
        self.MID1 = random.randint(0,255)        #Byte randomico para Message ID
        self.MID2 = random.randint(0,255)        #Byte randomico para Message ID
        self.payload_config = None
        self.payload_Date = None
        self.Uri = Uri    
        self.Token = random.randint(0,255)       ##Byte randomico para Message ID
        self.state = self.idle
        self.send = bytearray()
        self.ack = bytearray()
        self.Send_ack = bytearray()
        self.cont = 0
        self.Atual_Timeout_Ack = 2
        self.Periodo = 0
        
    
    
    def handle(self):
        '''
            Fica monitorando o socket criado para caso receber alguma mensagem, enviar para
            máquina de estado tratar. Recebe mensagem de até 2048 bytes.       
        '''
        msg_rcv = self.sock.recv(2048)
        self.handle_fsm(msg_rcv)
        self.Teste_Get = msg_rcv

    def handle_timeout(self):        
        '''
            handle_timeout é o responsável por fazer a retranmissão caso alguma mensagem COAP
            seja enviada e não receba nenhuma resposta do servidor. Tempo utilizado para isso
            esta descrito em Reload_Timeout_ack()
        '''   
        if(self.state==self.idle):
            self.disable_timeout()
            self.cont = 0

        elif(self.state==self.wait):
            if(self.cont == 0):
                self.Atual_Timeout_Ack = 2
                self.base_timeout = 2 * self.ACK_TIMEOUT_FACTOR
                self.timeout = 2 * self.ACK_TIMEOUT_FACTOR
                self.reload_timeout()
                self.enable_timeout()
            if(self.cont<self.MAX_RETRANSMIT):       
                self.sock.sendto(self.send,self.servidor)   
                self.Reload_Timeout_Ack(self.cont)
                #self.disable_timeout()     
            else:
                self.disable_timeout()
                self.state=self.idle
                self.cont = 0
                self.Atual_Timeout_Ack = 2
                self.Return_Base_Timeout() 
            if(self.cont == 3):
                print("Retransmissão atingiu o limite")     
            self.cont = self.cont + 1        

        elif(self.state==self.wait2):
            if(self.cont<4):
                self.sock.sendto(self.Send_Ack,self.servidor)       
            self.cont = self.cont + 1        

    def handle_fsm(self, data):
        '''
            Máquina de estado responsável por enviar as mensagens assim que a aplicação faz uma 
            requisição, assim como trata um datagrama recebido do servidor.
            Nesse protocolo desenvoldido, o estado idle é o responsável por enviar o datagrama 
            contendo as configurações da API assim que é iniciada.
            O Estado wait fica aguardando uma resposta do servidor, caso envie uma mensagem piggybacked 
            salva o valor recebido para aplicação coletar o payload.
            Wait2 seria caso o servidor enviasse apenas um Ack estando no Wait, ele fica esperando
            o recebimento da resposta.

        '''

        if(self.state == self.idle): 
            self.send = data
            self.sock.sendto(self.send,self.servidor) 
            self.enable_timeout()
            self.state = self.wait

        elif(self.state == self.wait):
            self.Ack_Response()
            if(data[0:4]==self.ack[0:4]):                # Se receber somente um ack, vai para o wait2 aguardar uma resposta
                self.state = self.wait2
                self.disable_timeout()
            elif(data[1]==self.code_Content_Format):    # se receber contente-format imprime o valor do payload
                pos = data.find(self.end)
                print('Payload recebido: ', data[pos+1:len(data)])
                self.state=self.idle
                self.disable_timeout()
                self.disable()            
            elif(data[0]==0x70):                        #se receber um reset não faz nada
                self.state = self.idle      
                self.disable_timeout() 
                self.disable()
            elif(data[1]==0x84):                        #Trara caso receba uma Not Found como resposta
                self.state = self.idle
                self.disable_timeout()
                self.disable()
                print("Not Found!")
            elif(data[0]==0x61 and data[1]!=0x00):      #recebeu um piggybacked
                pos = data.find(self.end)      
                if(pos!=-1) or (pos>5):
                    self.Teste_Get = data   
                self.state = self.idle
                self.disable_timeout()
                self.disable()
            else:   
                pos = data.find(self.end)             #caso receba alguma outra resposta, apenas imprime seu payload
                if(pos!=-1) or (pos>5):
                    print(data[pos+1:len(data)])
                                

        elif(self.state == self.wait2):
            if(data[0]==0x41):                               #caso Receba uma mensagem confirmável
                self.Push_Ack(data[2],data[3],data[4])              
                self.sock.sendto(self.Send_Ack,self.servidor)
                pos = data.find(self.end)
                #print('Payload recebido: ', data[pos+1:len(data)])   
                self.disable_timeout()
                self.disable() 
            elif(data[0]==0xa1):                             #caso Receba uma mensagem não confirmável, e somente pega payload
                #print('Payload recebido: ', data[pos+1:len(data)])   
                self.disable_timeout()
                self.disable() 

    def Reload_Timeout_Ack(self,value):  
        '''
            ** Função interna do protocolo, não deve ser chamada por uma aplicação, **

            O tempo da retransmissão é calculado como (2+4+8+16)*ACK_TIMEOUT_FACTOR, onde a primeira
            transmissão é 2*ACK_TIMEOUT_FACTOR, segunda 4*ACK_TIMEOUT_FACTOR e assim por diante. 
            Resultando em um total de 4 tentativas de retransmissão, não ultrapassando o tempo
            máximo de 45 segundos estipulado pela RFC.
            
        '''
        self.Atual_Timeout_Ack = (0x02 << value+1) * self.ACK_TIMEOUT_FACTOR 
        self.base_timeout = self.Atual_Timeout_Ack
        self.reload_timeout()
        self.enable_timeout() 
        #print("Reload_Timeout",self.Atual_Timeout_Ack,value)


    def Ack_Response(self):
        '''
            ** Função interna do protocolo, não deve ser chamada por uma aplicação, **

            Monta uma mensagem de resposta apenas para ser usado como comparação para quando receber
            algum datagrama.
        '''

        if(len(self.send)>2):
            self.ack = bytearray()
            self.ack.append(0x60)  #01100000
            self.ack.append(0x00)  #00000000
            self.ack.append(self.send[2])
            self.ack.append(self.send[3])
        return

    def Push_Ack(self,MID1,MID2,TOKEN):
        '''
            ** Função interna do protocolo, não deve ser chamada por uma aplicação, **

            Recebe como parâmetro os dois bytes contidos na Message ID e o Token de 1 byte.
            Monta uma mensagem de confirmação com payload vazio
        '''
        self.Send_Ack = bytearray()
        self.Send_Ack.append(0x60)
        self.Send_Ack.append(0x00)
        self.Send_Ack.append(MID1)
        self.Send_Ack.append(MID2)
        self.Send_Ack.append(TOKEN)




    def Set_Periodo(self,periodo):   
        '''
            Recebe uma valor em milisegundos para ser utilizado como tempo de envio de dados.
            No caso, irá ficar enviando dados coletados a cada periodo recebido.
        '''

        self.base_timeout = int(periodo/1000)
        self.reload_timeout()
        self.enable_timeout()

    def Return_Base_Timeout(self):
        '''
            Retorna o valor do timeout para o valor que foi definido como padrão. No caso
            foi 2*ACK_TIMEOUT_FACTOR
        '''
        self.base_timeout = 2 * self.ACK_TIMEOUT_FACTOR
        self.reload_timeout()
        self.disable_timeout()



    def Do_Get(self,Uri,Payload):
        '''
            Recebe uma Uri e um payload. Monta uma mensagem com Code GET e envia para o handle_fsm
            fazer a tratativa. Logo em seguida faz o despache para o poller monitorar os eventos
            futuros.
        '''    

        self.send.append(self.First_Byte)
        self.send.append(self.code_Get)                 
        self.send.append(self.MID1)
        self.send.append(self.MID2)
        self.send.append(self.Token)        
        self.Uri = self.Uri.split('/')        
        if(len(self.Uri)==2):                                              #trata uri com apenas um campo Ex. /time
            self.send.append(self.Delta1_Path | len(self.Uri[1]) << 0)
            for i in (self.Uri[1]):
                self.send.append(ord(i))
        elif(len(self.Uri)==3):                                            #trata uri com 2 camps Ex./other/separate
            self.send.append(self.Delta1_Path | len(self.Uri[1]) << 0) 
            for j in (self.Uri[1]):
                self.send.append(ord(j))            
            self.send.append(self.Delta2_Path | len(self.Uri[2]) << 0)
            for k in (self.Uri[2]):
                self.send.append(ord(k))
        self.send.append(self.end)      
        for i in range(0,len(Payload)):
            self.send.append(Payload[i]) 
        self.handle_fsm(self.send)
        self.Poll.adiciona(self)
        self.Poll.despache()

    def Do_Post(self,Uri,Payload):
        '''
            Recebe uma Uri e um payload. Monta uma mensagem com Code POST e envia para o handle_fsm
            fazer a tratativa. Logo em seguida faz o despache para o poller monitorar os eventos
            futuros.
        ''' 

        self.send.append(self.First_Byte)            
        self.send.append(self.code_Post)            
        self.send.append(random.randint(0,255))
        self.send.append(random.randint(0,255))
        self.send.append(random.randint(0,255))        
        self.Uri = Uri.split('/')

        if(len(self.Uri)==2):                                              #trata uri com apenas um campo Ex. /time
            self.send.append(self.Delta1_Path | len(self.Uri[1]) << 0)
            for i in (self.Uri[1]):
                self.send.append(ord(i))
        elif(len(self.Uri)==3):                                            #trata uri com 2 camps Ex./other/separate
            self.send.append(self.Delta1_Path | len(self.Uri[1]) << 0) 
            for j in (self.Uri[1]):
                self.send.append(ord(j))            
            self.send.append(self.Delta2_Path | len(self.Uri[2]) << 0)
            for k in (self.Uri[2]):
                self.send.append(ord(k))
        self.send.append(0x11)  #content-format octec-stream        
        self.send.append(0x2a)                         
        self.send.append(self.end)      
        #self.Protobuffer_Payload()
        for i in range(0,len(Payload)):
            self.send.append(Payload[i]) 
        self.handle_fsm(self.send)
        self.Poll.adiciona(self)
        self.Poll.despache()

        
        




