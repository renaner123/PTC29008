

########################################
Demonstração do funcionamento do Arq
#######################################

Arquivos a serem executados:
Envia.py  -> 
recebe.py -> 
Obs.: setar as portas seriais em ambos os arquivos no contrutor.




Para testar o funcionamento do ARQ pode se utilizar o arquivo Envia.py alterando sua porta serial para a desejada, e executando o arquivo recebe.py alterando também sua porta 
serial.
Nessa demonstração vocẽ pode observar a sequência de mensagens utilizada, que no caso é 0 e 1, assim como o recebimento do ACK0 e ACK1 para suas respectivas mensagens.
Outro teste que pode ser verificado, é que em cada recebimento de ack ocorre um backoff onde o tempo é aleatório entre 1 a 7, fazendo com que se garanta a entrega dos dados e não haja colisão.
Também é possível verificar que caso um lado envie uma mensagem, mas o outro esteja desconectado, o protocolo tentará enviar 3 vezes a mensagem, caso não obtenha sucesso, mensagem é descartada. Nessa demonstração também é possivél verificar que a transmissão é bidirecinal, qualquer lado pode transmitir a qualquer momento.
