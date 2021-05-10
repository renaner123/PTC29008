# O protocolo desenvolvido nesse projeto se destina a estabelecer enlaces ponto-a-ponto entre computadores. As funções do protocolo são:

## Aplicação

O sistema simula um protocolo para a camada de enlace, cujo o objetivo é possibilitar a
troca de informações ponto a ponto através da rede, fazendo o uso de um transceiver RF APC
220 conectado na porta USB de cada máquina. Como requisito deve se basear no protocolo PPP
e deve oferecer uma tratativa para possíveis erros em quadros, controle de sequência, garantia
de entrega e controle de sessão.


## Características

+ Enquadramento
+ Detecção de erros com CRC-16
+ Garantia de entrega com ARQ do tipo pare-e-espere
+ Controle de acesso ao meio do tipo Aloha
+ Gerenciamento de sessão


## Utilizando o protocolo

> Para utilizar este protocolo, primeiramente deve-se acessar os arquivos Envia.py e recebe.py para alterar a porta serial a ser utilizada, assim como o endereço IP de origem e destino da Interface Tun.
 + Serial - Alterar porta serial sem serial.Serial('Alterar aqui')
 + Tun - Alterar as informações em Tun() conforme a necessidade.
 
 > A interface Tun só pode ser utilizada uma em cada placa de rede.

[Home](..) - Voltar na página principal da disciplina

Informações de métodos, diagramas, configurações ... podem ser encontradas no [relatório](./PTC___Projeto_1.pdf)


## 
