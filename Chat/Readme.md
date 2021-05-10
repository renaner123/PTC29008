# Transferência de mensagens puramente textuais entre usuários através de sockets TCP

## Especificações
 
+ Serviço: Transferência de mensagens puramente textuais entre usuários através de sockets.
+ Ambiente de execução: Servidor gera uma conexão TCP utilizando IPV4 entre usuários que
desejam ser conectados, gerenciando a transferência de mensagens entre os usuários por meio
de sockets provindos da API BSD Sockets. Sendo assim, um modelo cliente-servidor, onde possibilita o envio de mensagens privadas ou públicas.
+ Vocabulário: Possui os comandos :Mensagem pública, Nome Destino:Mensagem privada, {quit},
e os códigos de erro 01,02,03,04 e 05.
    
    Código | Significado
    :-:|-------
    01 | Esse apelido já está em uso
    02 | Destino da mensagem privada não existe
    03 | Cancelamento de conexão forçado
    04 | Servidor de destino é Inválido
    05 | Endereço IP do servidor é inválido”

+ Codificação: Puramente textual(ASCII)
+ Comportamento:
    + Comportamento lado Servidor:
    1. Recebe um endereço IP e porta válidos, onde deve ficar aguardando as conexões de clientes.
    1. Quando algum cliente se conecta, mantém a conexão até que o usuário encerre a aplicação.
    1. Solicita a aplicação do cliente uma identificãoo para poder usar o chat.
    1. Recebe tudo o que cliente digita, fazendo assim o gerenciamento das mensagens. Encaminhando para o destino correto, caso esteja disponível, ou alertando que o destino não está mais disponível.
    + Comportamento lado cliente.
    1. Recebe um endereço IP e porta válidos referente ao servidor onde deve se conectar.
    1. Deve inserir um apelido(identificação) para conseguir se conectar e usar o chat
    1. Pode enviar uma mensagem privada ou pública e sair do chat quando quiser.
  
 
 ## Manual de utilização

 ### Manual de uso do lado servidor:
1. Necessário executar primeiro o arquivo servidor.py com alguma IDLE python 
1. Em seguida ́é necessário informar um endereço IP que seja válido em sua rede para que a aplicação possa ficar aguardando conexões de clientes, assim como deve informar uma porta de escuta, caso não seja um endereço válido, irá mostrar erro 05 e deverá ser reiniciado a aplicação. Se deixar o endereço de IP em branco será atribuído o IP 127.0.0.1. 
1. Assim que algum cliente se conectar, será mostrado o endereço IP e a porta do cliente que acabou de se conectar, e irá solicitar uma identificação ao mesmo. 
1. Após aprovada a identificação, o servidor mantém a conexão ̃com o cliente e possibilitará a ele enviar mensagens privadas usando o comando Destino(apelido):Mensagem ou mandar para todos que estiverem online com :Mensagem pública. 
1. Assim que o cliente enviar uma mensagem privada, ele receberá uma mensagem ”Mensagem enviada”se o destino estiver correto e online, caso contrário informará erro 02. 
1. O cliente que receber uma mensagem privada, receberá uma mensagem de ”Mensagem recebida de: Cliente(Apelido de quem mandou). 
1. Servidor encerra a conexão com o cliente assim que ele fechar a aplicação cliente.py ou digitar quit, informando para todos os usuários conectados que esse cliente saiu

 ### Manual de uso do lado cliente: 


 1. Assim que o servidor já estiver em execução, execute o arquivo cliente.py com alguma IDLE
python
2. Será solicitado ao usuário um endereço IP e uma porta, que deve ser o endereço ao qual foi
definido na aplica¸c˜ao servidor.py para aguardar conexões de clientes, caso endereço esteja
errado, ser´a informado erro 04, ao contrário, ira informar que a conexão foi estabelecida.
3. Assim que conexão estiver estabelecida, será mostrado uma listagem com todos os usuários
que estão conectados. Caso queira mandar uma mensagem privada a alguém, o formato de envio da mensagem está descrito no item 4 do manual do servidor.
4. Caso queira sair do chat, basta digitar quit ou fechar a aplicação
 
 

 
[Home](..) - Voltar na página principal da disciplina
 
 







