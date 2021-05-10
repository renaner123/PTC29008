from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

#Código base se encontra em: https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170


# classe para manipular o socket
class Send:
    def __init__(self):  # construtor da mensagem
        self.__msg = ''
        self.new = True
        self.con = None

    def desconectar(sair):
        if (sair == 'sair'):
            tcp.close()
            tcp.shutdown();

# função esperar - Thread.
def esperar(tcp, send, host='host', port='port'):
    try:
        origem = (host, int(port))                                       # recebe host e ip fornecido pelo usuário
        # cria um vinculo
        tcp.bind(origem)
        # deixa em espera, nesse caso permite até 3 conexões
        tcp.listen(3)

        while True:
            # aceita um conexão, cria objeto 'con' com as informações da conexão
            con, cliente = tcp.accept()
            print('Cliente ', cliente, ' conectado!')
            # atribui a conexão ao manipulador
            con.send(bytes("Digite seu apelido", "utf8"))
            addresses[con] = cliente                                     # guarda ip e a porta do cliente
            list_addr.append(con)                                        # lista auxiliar com os endereços obtido dos sockets
            Thread(target=handle_client, args=(con,)).start()            # joga s argumentos do con para o handle_client
            send.con = con

    except OSError:
        print("Erro 05: Endereço IP do servidor é inválido")

def handle_client(con):

    name = con.recv(1024).decode("utf8")                                 #recebe apelido fornecido pelo usuário

    welcome = 'Bem Vindo %s! Caso queira sair digite {quit}. \nDigite a mensagem no formato Origem:mensagem ou :Mensagem para enviar a todos' % name

    if (name in list_names) and (name != bytes("{quit}", "utf8")):       #Verifica se o nome informa já está em uso
        con.send(bytes("Erro 01: Esse apelido já está em uso", "utf8"))
        con.send(bytes("Digite seu apelido", "utf8"))
        handle_client(con)                                               #Retorna ao inicio da função para informar um novo apelido.
    else:
        list_names.append(name.replace(" ", ""))                         # replace para tirar os espaços existente nos nomes Ex. "  Renan"
        con.send(bytes(welcome, "utf8"))
        rpt = len(list_names)                                            #Auxiliar para imprimir os usuários online
        # mostra quem está online

        for x in range(0, rpt - 1):
            con.send(bytes(list_names[x] + ' Está online \n', "utf8"))   #Laço apenas para informar a quem entra quem está online

        x = 0
        msg = "%s Entrou no chat!" % name
        broadcast(bytes(msg, "utf8"))
        clients[con] = name

    while True:
        try:
            msg = con.recv(1024)                                        #fica aguardando novas mensagens
        except OSError:
            if (msg != "{quit}"):                                       # Verifica se quando ocorrer uma exceção não é o usuário digitando {quit}
                print("Erro 03: Cancelamento de conexão forçado")
                con.close()
                del list_addr[list_names.index(clients[con])]
                list_names.remove(clients[con])

                # list_addr.remove(addresses[con])
                del clients[con]
                del addresses[con]
                break
            else:
                print("Erro 03: Cancelamento de conexão forçado")
                con.close()
                del list_addr[list_names.index(clients[con])]
                list_names.remove(clients[con])
                break
        msg_rcv = str(msg)
        try:
            #  if(msg_rcv.find(":")>=0)or(msg_rcv==("{quit}")):
            if msg != bytes("{quit}", "utf8"):                          #Enquanto mensagem for diferente de {quit} verifica o destino da mensagem e o conteúdo da mensagem
                destino, mensagem = (msg_rcv[2:(len(msg_rcv))].split(':'))
                destino = destino.replace(" ", "")
                if (destino == ''):
                    broadcast(msg, name + ": ")
                else:
                    if (destino in list_names):
                        list_addr[list_names.index(destino)].send(
                            bytes('Mensagem recebida de ' + clients[con] + ': ' + mensagem, "utf8"))
                        con.send(bytes('Mensagem Enviada', "utf8"))
                    else:
                        con.send(bytes("Erro 02: Destino de mensagem privada não existe", "utf8"))
            else:
                con.send(bytes("{quit}", "utf8"))                       #Se a mensagem for {quit} servidor encerra a conexão e limpa os dados existente do usuário
                print('Cliente ', addresses[con], clients[con], ' deconectado!')
                con.close()
                del list_addr[list_names.index(clients[con])]           #limpa o endereço de acordo com a posição que o apelido está, pois ambos estão na mesma ordem
                list_names.remove(clients[con])
                # list_addr.remove(addresses[con])
                del clients[con]
                del addresses[con]
                broadcast(bytes("%s Saiu do chat." % name, "utf8"))
                break
        except:
            con.send(bytes('Por favor, digite Destino: Mensagem', "utf8"))


def desconectar(sair):
    if (sair == 'sair'):
        tcp.close()
        tcp.shutdown();


def broadcast(msg: object, prefix: object = "") -> object:  # prefix is for name identification.
    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)


clients = {}                                                        #guarda os apelidos dos clientes
addresses = {}                                                      #guarda a tupla (host, ip)
list_names = []                                                     #lista auxiliar para ajudar ver quem está online
list_addr = []                                                      #lista auxiliar para ajudar a ver os endereços de quem está online
port_client = 0
host_servidor = 0

if __name__ == '__main__':

    print('Digite um IP válido da rede para criar o servidor: ')
    host_servidor = input()
    print('Digite porta do servidor: ')
    port_client = input()

    # cria um socket
    tcp = socket(AF_INET, SOCK_STREAM)
    send = Send()
    # cria um Thread e usa a função esperar com quatro argumentos
    processo = Thread(target=esperar, args=(tcp, send, host_servidor, port_client))
    processo.start()

    print('Iniciando o servidor de chat!')
    print('Aguarde alguém conectar!')
    msg = input()
    while True:
        send.put(msg)
        msg = input()

    processo.join()
    tcp.close()
    list_names.clear()
    list_addr.clear()
exit()
