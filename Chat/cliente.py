from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


# classe para manipular o socket
class Send:
   def __init__(self):
       self.__msg = ''
       self.new = True
       self.con = None

   def put(self, msg):
       self.__msg = msg
       if self.con != None:
           # envia um mensagem atravez de uma conexão socket
           self.con.send(str.encode(self.__msg))

   def loop(self):
       return self.new


# função esperar - Thread
def esperar(tcp, send, host='localhost', port=5050):
   destino = (host, int(port))
   # conecta a um servidor
   try:
       tcp.connect(destino)                                     #cria conexão com o servidor
       while send.loop():                                       #Fica em loop até conexão ser estabelecidade
           print('Conectado a ', host, '.')
           # atribui a conexão ao manipulador
           send.con = tcp
           try:
               while send.loop():
                   # aceita uma mensagem
                   msg = tcp.recv(1024)
                   if (msg != bytes("{quit}","utf8")):          #Quando cliente envia um {quit} para servidor, o servidor encaminha um {quit} para o cliente ser finalizado.
                       print(str(msg, 'utf-8'))
                   else:
                       tcp.close();
                   if not msg: break
           except OSError:
               print("Você foi Desconectado")
               break
   except OSError:
    print("Servidor de destino é Inválido")
    return '__main__'


def desconectar(sair):
    if (sair == 'sair'):
        tcp.close()
        tcp.shutdown();




if __name__ == '__main__':
   print('Digite IP do servidor: ')
   host = input()
   print('Digite porta do servidor: ')
   port_client = input()

   if host == '':
       host = '127.0.0.1'

   # cria um socket
   tcp = socket(AF_INET, SOCK_STREAM)
   send = Send()
   # cria um Thread e usa a função esperar com quatro argumentos
   processo = Thread(target=esperar, args=(tcp, send, host, port_client))
   processo.start()                                   #inicia a Thread

   msg = input()
   

   while True:
       send.put(msg)
       msg = input()

   processo.join()
   tcp.close()
   exit()
