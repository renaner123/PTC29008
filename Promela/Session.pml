mtype = {cr,cc,kr,kc,dr,dc,ca,start,vinte,seis}   // Mensagens a serem transmitidas
chan Ent = [1] of {mtype}                         // Canal de tamanho 1 usado pela entidade 1 para envio de mensagem
chan Ent2 = [1] of {mtype}						  // Canal de tamanho 1 usado pela entidade 2 para envio de mensagem
int aux											  // aux é incrementado quando ocorre uma desconexão para entidade 1					
int aux1										  // aux1 é incrementado quando ocorre uma desconexão para entidade 2				
int Conectou									  // Usado para verificar se ambas entidades se conectam


// Processo responsável por simular o um "Transmissor"
active proctype T1() {
	int cont									  // Variável utilziada para controlar retransmissão do CR quando no estado Hand1
    int cont_check								  // Variável utilizada para controlar o período de cada Check_Interval
	
Ent!start										  // Inicia o processo enviando um start, que por sinal é o único a ser enviado.

// Essa entidade tem o mesmo funcionamento da máquina de estado do projeto1, onde: 
  //      DISC: desconectado
  //      HAND1: em negociação para estabelecimento de conexão, quando tomou a iniciativa de estabelecê-la
  //      HAND2: em negociação para estabelecimento de conexão, quando o outro lado tomou a iniciativa
  //      CON: conectado
  //      CHECK: aguardando resposta para Keep Alive
  //      HALF1: em estado de terminação de enlace (half-close), quando tomou a iniciativa de terminá-lo
  //      HALF2: em estado de terminação de enlace (half-close), quando o outro lado tomou a iniciativa 

Disc:
	cont = 0
	aux = 0
	printf("Disc 1 %d \n",aux)		
	do
	
	:: Ent2?start ->
	   Ent!cr	
	   printf("Disc - Recebeu Start e Enviou cr \n")
	   goto Hand1    
	:: Ent2?cr ->
	   Ent!cc
	   printf("Disc - Recebeu cr e Enviou cc \n")
	   goto Hand2	
	:: timeout ->
	   goto Disc
    od

	
Hand1:
	printf("Hand1 1 \n")	
	do
	:: Ent2?start ->
	   Ent!ca	
	   printf("Hand1 - Recebeu Start e Enviou ca \n")		
	   goto Con		
	:: Ent2?cc ->
	   Ent!ca 
	   printf("Hand1 - Recebeu cc e Enviou ca \n")	
	   goto Con				
	:: Ent2?ca ->
	   printf("Hand1 - Recebu ca \n")				
	   goto Con	
	:: Ent2?cr ->
	   Ent!cc	
	   printf("Hand1 - Recebeu cr e Enviou cc \n")		
	   goto Hand1 		
	:: timeout ->
	   if    
	   ::cont<=2 ->						// Retransmissão da mensagem cr caso ocorra timeout
         Ent!cr
	     cont ++	
	   :: else ->
	      cont = 0
	      goto Disc
       fi
	od
	
Hand2:
	
	printf("Hand2 1 \n")		
	do
	:: Ent2?ca ->
	   printf("Hand2 - Recebeu ca \n")
	   goto Con
	:: Ent2?dr ->
	   Ent!dr	
	   printf("Hand2 - Recebeu dr e Enviou dr \n")		
       goto Half2
	:: timeout -> 
	   goto Disc
	od
		
Con:

    Conectou ++
	printf("Con 1 \n")	
	do
	
	:: Conectou == 15 ->         // Isso não consta no projeto1, foi feito para forçar uma desconexão.
	   Ent!dr
	   Conectou = 0
	   goto Half1
	:: Ent2?dr ->
       Ent!dr
	   printf("Con - Recebeu dr e Enviou dr  \n")
	   goto Half2
	:: Ent2?dc ->
	   printf("Con - Recebeu dc  \n")
	   aux ++
	   goto Disc
	:: Ent2?kr ->
	   Ent!kc	
	   printf("Con - Recebeu kr e Enviou kc  \n")		
	   goto Con	
	:: Ent2?ca ->
	   printf("Con - Recebeu ca  \n")
	   goto Con	
	:: Ent2?vinte
	   Ent!dr	
	   printf("Con - Recebeu close e Enviou dr  \n")
	   aux ++
	   goto Disc
	:: timeout->
	   cont_check ++
	   printf("Con1 cont = %d \n",cont_check)
	   if 
	   :: cont_check == 3 ->	// Não é o mesmo valor do projeto1, quando cont_check chegar em 3, inicia o Check_Interval
		  Ent!kr
		  cont_check = 0
		  goto Check
	   :: else ->
	      goto Con
	   fi
    od
		
Half1:
	
	printf("Half1 1 \n")	
	do
	:: Ent2?dr ->
	   printf("Half1 - Recebeu dr  \n")
	   Ent!dc
	   aux ++
	   goto Disc	
	:: timeout ->
	   Ent!dr	
	   printf("Half1 Timeout - Enviando Dr  \n")	
	od
		
Half2:
	
	printf("Half2 1 \n")	
	do
	:: Ent2?dr ->
	   Ent!dr
	   printf("Half2 - Recebeu dr e Enviar  \n")	
	   goto Half2
	:: Ent2?dc ->
       printf("Half2 - Recebeu dc  \n")
	   aux ++
	   goto Disc	
    :: timeout ->
	   printf("Half2 Timeout \n")
	   aux ++
	   goto Disc	
    od		
		
Check:
	
	printf("Check 1 \n")	
	do
	:: Ent2?kc ->
	   printf("Check - Recebeu kc  \n")
	   goto Con	
	:: timeout ->
	   printf("Timeout Check\n")
	   aux ++
	   goto Disc
	od
	  	  
}



// A entidade2 se comporta da mesma maneira que a entidade1, diferença que nessa não possui
// a parte de forçar uma desconexão.



active proctype T2() {
	int cont
    int cont_check2
	
Ent2!start
	
Disc:
	cont = 0
	printf("Disc 2 %d\n",aux1)	
	
	do
	:: Ent?start ->
       Ent2!cr	
	   printf("Disc2 - Recebeu Start e Enviou cr \n")
	   goto Hand1    
	:: Ent?cr ->
	   Ent2!cc
	   printf("Disc2 - Recebeu cr e Enviou cc \n")
	   goto Hand2
	:: timeout ->
	   goto Disc		
    od
	
		
Hand1:
	printf("Hand1 2 \n")	
	do
	:: Ent?start ->
	   Ent2!ca	
	   printf("Hand12 - Recebeu Start e Enviou ca \n")		
	   goto Con		
	:: Ent?cc ->
	   Ent2!ca 
	   printf("Hand12 - Recebeu cc e Enviou ca \n")	
	   goto Con				
	:: Ent?ca ->
	   printf("Hand12 - Recebu ca \n")				
	   goto Con	
	:: Ent?cr ->
	   Ent2!cc	
	   printf("Hand12 - Recebeu cr e Enviou cc \n")			
	   goto Hand1 			
	:: timeout ->
	   if    
	   ::cont<=2 ->
end1:    Ent2!cr
	     cont ++	
	   :: else ->
	      cont = 0
	      goto Disc
       fi
	od
		
Hand2:
	
	printf("Hand2 2 \n")		
	do
	:: Ent?ca ->
	   printf("Hand22 - Recebeu ca \n")
	   goto Con
	:: Ent?dr ->
	   Ent2!dr	
	   printf("Hand22 - Recebeu dr e Enviou dr \n")		
       goto Half2
	:: timeout -> 
	   goto Disc
	od

Con:
 
    Conectou ++	
	printf("Con 2 \n")	
	do
	:: Ent?dr ->
       Ent2!dr
	   printf("Con2 - Recebeu dr e Enviou dr  \n")
	   goto Half2
	:: Ent?dc ->
	   printf("Con2 - Recebeu dc  \n")
	   aux1 ++
	   goto Disc
	:: Ent?kr ->
	   Ent2!kc	
	   printf("Con2 - Recebeu kr e Enviou kc  \n")		
	   goto Con	
	:: Ent?ca ->
	   printf("Con2 - Recebeu ca  \n")
	   goto Con	
	:: Ent?vinte
	   Ent2!dr	
	   printf("Con2 - Recebeu close e Enviou dr  \n")
	   aux1 ++
	   goto Disc	
	:: timeout->
	   cont_check2 ++
	   printf("Con2 cont = %d \n", cont_check2)
	   if 
	   :: cont_check2 == 3 ->
		  Ent2!kr
		  cont_check2 = 0
		  goto Check
	   :: else ->
	      goto Con
	   fi
    od
	
Half1:
	
	printf("Half1 2 \n")	
	do
	:: Ent?dr ->
	   printf("Half12 - Recebeu dr  \n")
	   Ent2!dc
	   aux1 ++
	   goto Disc	
	:: timeout ->
	   Ent2!dr	
	   printf("Half12 Timeout - Enviando Dr  \n")	
	od
		
Half2:
	
	printf("Half2 2 \n")	
	do
	:: Ent?dr ->
	   Ent2!dr
	   printf("Half22 - Recebeu dr e Enviar  \n")	
	   goto Half2
	:: Ent?dc ->
       printf("Half22 - Recebeu dc  \n")
	   aux1 ++
	   goto Disc	
    :: timeout ->
	   printf("Half22 Timeout \n")
	   aux1 ++
	   goto Disc	
    od		
		
Check:
		
	printf("Check 2 \n")	
	do
	:: Ent?kc ->
	   printf("Check2 - Recebeu kc  \n")
	   goto Con	
	:: timeout ->
	   printf("Timeout Check \n")
	   goto Disc
	   
	od
	  	  
}

ltl Desconecta1 { <> (aux == 1) &&  <>(aux1==1)} // 
ltl Desconecta2 { (((<>(T1@Con U T1@Half2)) && (<>(T2@Con U T2@Half1))) ||((<>(T1@Con U T1@Half1)) && (<>(T2@Con U T2@Half2))))    }

ltl Estabelece1 { <> (Conectou == 2)}
ltl Estabelece2 {  (((<>(T1@Hand1 U T1@Con)) && (<>(T2@Hand2 U T2@Con))) ||  ((<>(T1@Hand2 U T1@Con)) && (<>(T2@Hand1 U T2@Con))))}


//Desconecta1 - Variável aux e aux1 é incrementa quando as entidadee estiverem no estado Con e receber um dc ou um vinte(erro ARQ), ou quando 
// estiverem nos estados Half1/Half2 prestes a irem para o estado Disc. Assume assim, que eventualmente aux e aux1 vão ser igual a 1. Representando assim
// que em algum momento as entidades vão ser desconectadas.
//Uma falha que é possível observer, é que as entidades após serem desconectas permanecem sempre desconectadas, pois só ocorre um start no inicio do processo.
//Isso pode ser verificado no promela, onde após o estado 9 não acontece mais nada.

//Desconecta2 - Como o ciclo só ocorre uma vez(um start), usa-se uma formula ltl que diz que eventualmente se a entidade1 estiver no estado Con 
//e a entidade2 tomar a iniciativa de desconexão, a entidade1 irá para Half2 e a entidade2 passará de Con para Half1, que nesse caso, Half1 e Half2 
//sempre vão gerar desconexão. Vice versa para quando a entidade1 toma a iniciativa.
 
 
 
//Estabelece1 - A variável é incrementa assim que uma entidade chega no estado Con, se as duas entidades chegarem no Con, entede-se que eventualmente
// foi estabelecida uma conexão, onde o lado que inicia é idependente, pois ambos os processos estão sendo iniciados enviando um start.
 
//Estabelece2 - Foi usado a mesma lógica do Desconecta2, em que diz que eventualmente se a entidade1 estiver no estado Hand1 
//e a entidade2 tomar a iniciativa de conexão, a entidade1 irá para Con e a entidade2 passará de Hand2 para Con, que nesse caso, Hand1 e Hand2 
//sempre vão gerar Conexão,já que só vão receber start e cc/cr/ca. Vice versa para quando a entidade1 toma a iniciativa.


//termino de sessao eventualmente sera concluido para ambas as partes
//duas entidades sao capazes de estabelecerem uma sessao independente
//de qual delas iniciar a sessao
