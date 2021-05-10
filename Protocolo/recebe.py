import poller
from Framming import Enquadramento
import serial
from FAKE_APP import Fake_app
from session_manage import Session_Manager
from Interface_Tun import Tun_Tun
from ARQ import Arq
import sys
from tun import Tun


if __name__ == "__main__":

    ser = serial.Serial('/dev/pts/3', 9600, timeout=5)   #porta serial que será monitorada pelo poller
    tun = Tun("tun0","10.0.0.2","10.0.0.1",mask="255.255.255.252",mtu=1500,qlen=4)


    print("Aguardando em", ser.port)
    arq = Arq(None, 1)                                 #'''Criando objetos que vão ser usados pelo poller para fazer 
    Int_tun = Tun_Tun(tun)                                                    #  o monitoramento dos eventos  '''   
    Fake = Fake_app(sys.stdin,1)                          
    cb = Enquadramento(ser)
    Manager = Session_Manager(None, 5)  
    Fake.Fake_send(Manager)
    arq.get_framming(cb)
    arq.get_Tun(Int_tun) 

    Manager.Get_Tun(Int_tun)
    Manager.get_Arq(arq)                   #objeto para enviar primeiro quadro para conection request
    Manager.Get_Fake(Fake)
    Manager.Start_Conection()

    arq.get_Manager(Manager)    
  
    Int_tun.Tun_send(Manager)                                # '''Camada utilizada para testar com captura do teclado'''                                   
    cb.vem_top(arq)    
#s
    sched = poller.Poller()

    sched.adiciona(Manager)   
    sched.adiciona(cb)                                 # '''Adicionando os eventos desejados ao poller'''
    sched.adiciona(arq)
    sched.adiciona(Fake)
  
    sched.despache()



#print