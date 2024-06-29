Implementação de algoritmos distribúidos para Trabalho 2 de MC714.

Para o problema de exclusão mútua, foi implementado o algoritmo de Ricart-Agrawala, fazendo uso do relógio lógico de Lamport.
Para o problema de eleição, foi utilizado o algoritmo do valentão.
Ambos algoritmos foram implementados a partir de sua descrição do livro Distributed Systems de Maarten van Steen.

O projeto foi implementado utilizando ZeroMQ para a comunicação entre processos.
Foi utilizado sockets pub-sub para realizar broadcast de mensagens, e router-dealer para o envio direto entre dois processos.

Para a realização do experimento nós executamos 8 instâncias simultaneamente.
Como o algoritmo de exclusão mútua implementada não é tolerante a falhas, as eleições são começadas por processos de forma aleatória, simulando uma perda de comunicação.
