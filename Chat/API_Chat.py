import servidor
import cliente



## Não consegui concluir, não está funcionando.






class Conecta_Servidor():

    def __init__(self):
        self.host = '127.0.0.1'
        self.port = '5001'
        servidor.esperar(self.host,self.port)
        servidor.handle_client(servidor.Send.con)


class Conecta_cliente(object):

    def __init__(self,host_c,ip_c):
        self.host_c = host_c
        self.ip_c = ip_c
        cliente.esperar(self.host,self.ip)

    def enviar_Msg(self,destino,mensagem):
        self.destino = destino
        self.mensagem = mensagem
        cliente.Send()
        cliente.Send.put(self,mensagem)


 

