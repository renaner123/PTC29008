mtype = {flag, esc, comum}
chan serial = [1] of {mtype}        // canal que suporta uma mensagem do tipo (flag,esc ou comum)
bool Quadro							// Quando true, corresponde a um quadro que foi recebido

// Processo responsável por fazer a transmissão dos quadros
active proctype TX() {
  int bytes	  
 
// Estado no qual é enviado um quadro completo, no caso, contém flag no inicio e no fim. 
envia1:
  printf("Inicio envia1 \n")
  bytes = 0  						// Bytes é usado para delimitar quantidade de bytes a ser enviada
  serial!flag						// Inicia um quadro com flag
  do
  :: bytes < 4 ->					// Enquanto bytes for menor que 4, fica enviando byte comum ou byte especial
     if
     :: serial!comum
     :: serial!esc -> serial!comum
     fi
     bytes++
  :: else -> break
  od 
  serial!flag   					// Finaliza o quadro e muda para envia2
  goto envia2
  
// Estado no qual é enviado um quadro incompleto, no caso, contém apenas a flag inicial 	  
envia2:
  printf("Inicio envia2 \n")		// Mesmo funcionamento do envia1, a diferença é que não é enviado a flag delimitadora de quadro
  bytes = 0  
  serial!flag
  do
    :: bytes < 4 ->
     if
     :: serial!comum
     :: serial!esc -> serial!comum
     fi
     bytes++
  :: else -> break
  od  
  goto envia1

	  	  
}

// Processo responsável pela recepção dos quadros
active proctype RX(){
   int cont							// Variável que verifica a quantidade de bytes já recebidos
   bool Buffer	  					// True para quando recebe um quadro completo    
   goto Ocioso

// Estado de inicio da recepção
Ocioso:
   Quadro = false
   do
   ::serial?flag ->					// Caso receba uma flag, zera o cont e muda para o estado recepcao
     cont = 0
     printf("Oci - Recebeu: %d FLAG \n", _pid)
     goto Recepcao
   ::serial?comum ->				// Caso receba um byte comum, permanece no ocioso até receber uma flag
     printf("Oci - Recebeu: %d Comum \n", _pid)
     goto Ocioso
   ::serial?esc ->					// Caso receba um byte especial, permanece no ocioso até receber uma flag
     printf(" Oci - Recebeu: %d Esc \n", _pid)
     goto Ocioso
   :: timeout ->
	 goto Ocioso
   od
   
// Estado responsável pela recepção dos quadros   
Recepcao:
   do
   :: serial?comum -> 				// Caso receba um byte comum, incrementa o cont e permanace em Recepcao
      printf("Rec -recebeu %d comum \n",_pid)
      cont ++
      goto Recepcao
   :: serial?esc ->					// Caso receba um byte de escape 
      printf("Rec - recebeu %d esc \n", _pid)
      goto Escape 
   :: serial?flag ->   				// Se receber uma flag com n>0 indica que recebeu um quadro completo
       Quadro = true				
	   if
	   :: cont > 0 ->
	      printf(" Rec - Recebeu Flag - Copia Buffer %d bytes \n", cont ) 
		  Buffer = 1
		  goto Ocioso

	   :: cont == 0 ->				// Se n for igual 0 informa que recebeu um quadro vazio ou apenas duas flag
		  printf(" Rec - Recebeu Flag  mas quadro esta vazio %d \n", cont) 
		  goto Recepcao  
	   fi
   :: timeout ->  
      goto Ocioso

   od

// Estado que faz o processo contrário do estufamento
Escape:

   do
   :: serial?comum ->				// Caso receba uma flag ou outro escape, retornar para ocioso, pois deveria ser um byte comum
      cont ++
	  printf("Esc - Recebeu byte comum \n") 
      goto Recepcao
   :: serial?esc ->
	  printf("Esc - Recebeu esc \n") 
      goto Ocioso
   :: serial?flag ->
	  printf("Esc - Recebeu flag comum \n")  
	   goto Ocioso
   :: timeout ->
	  goto Ocioso

   od

}

ltl Enquadramento { []<>(Quadro == true) }

// Perdas de sincronismo sao recuperadas em algum momento
//Essa fórmula representa que Indefinidamente frequente o processo RX recebe um quadro completo.
// pois sempre que o estado Recepcao recebe uma flag, joga o Quadro para true.
