import poller
from Framming import Enquadramento
import serial
from FAKE_APP import Fake_app
from ARQ import Arq
import sys

if __name__ == "__main__":

    ser = serial.Serial('/dev/pts/6', 9600, timeout=5)   #porta serial que será monitorada pelo poller
    print("Aguardando em", ser.port)
    arq = Arq(None, 5)                                   #'''Criando objetos que vão ser usados pelo poller para fazer
                                                          #  o monitoramento dos eventos  '''   
    Fake = Fake_app(sys.stdin,5)                          
    cb = Enquadramento(ser)

    arq.get_framming(cb)
   
    Fake.Fake_send(arq)                                # '''Camada utilizada para testar com captura do teclado'''                                   
    cb.vem_top(arq)    

    sched = poller.Poller()
       
    sched.adiciona(cb)                                 # '''Adicionando os eventos desejados ao poller'''
    sched.adiciona(arq)
    sched.adiciona(Fake)
    
    sched.despache()



    #print
