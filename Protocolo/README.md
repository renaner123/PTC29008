# O protocolo desenvolvido nesse projeto se destina a estabelecer enlaces ponto-a-ponto entre computadores. As funções do protocolo são:

+ Enquadramento
+ Detecção de erros com CRC-16
+ Garantia de entrega com ARQ do tipo pare-e-espere
+ Controle de acesso ao meio do tipo Aloha
+ Gerenciamento de sessão

O protótipo do protocolo deve se integrar ao subsistema de rede do Linux através de uma interface Tun.


## Protocolo de comunicação


## Como utilizar o protocolo

> Para utilizar este protocolo, primeiramente deve-se acessar os arquivos Envia.py e recebe.py para alterar a porta serial a ser utilizada, assim como o endereço IP de origem e destino da Interface Tun.
 + Serial - Alterar porta serial sem serial.Serial('Alterar aqui')
 + Tun - Alterar as informações em Tun() conforme a necessidade.
 
 > A interface Tun só pode ser utilizada uma em cada placa de rede.

[Home](..) - Voltar na página principal da disciplina
