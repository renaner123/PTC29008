
import poller
import sys,time
from ARQ import Arq

class Fake_app(poller.Layer):

    def __init__(self, obj, timeout=5):     
        self.timeout = timeout
        self.base_timeout = timeout
        self.fd = obj
        self.disable_timeout()
        self.recebe_app = None
    
    def handle(self):
        quadro = sys.stdin.readline()                
        self.recebe_app = quadro[:-1]     
        self.envia_fake.Fsm_arq(self.recebe_app)      

    def handle_timeout(self):
       pass
        #print('Timeout !')

    def Fake_send(self,obj):
        self.envia_fake = obj


   
        
