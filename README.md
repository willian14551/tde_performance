# TDE Programação Concorrente: Filósofos, Semáforos e Deadlock

Vídeo da apresentação: (link do YouTube)

Grupo: TDE2 4

Integrantes:  
Willian Anderson da Rocha  
Felipe Rodrigues Milicio  
Millena Gurczakovski  
Clara Miyamoto Yajima  

Linguagem: Python 3.10 ou superior.

## Parte 1: Jantar dos filósofos

### Como o problema funciona
Cinco filósofos se sentam em volta de uma mesa redonda e entre cada par de vizinhos fica um garfo, então são cinco garfos no total. Cada filósofo repete a mesma rotina: pensa durante um tempo, fica com fome e come. Só que para comer, ele precisa dos dois garfos ao lado dele, o da esquerda e o da direita, e só devolve os dois quando termina de comer.

### PARTE 1 - Versão ingênua
Nessa versão, o protocolo é o mais direto possível. Quando fica com fome, o filósofo pega o garfo esquerdo, depois ele pega o direito, come e solta os dois.
Se o garfo que o filósofo quer está com o filósofo vizinho, a thread fica bloqueada no "acquire" até o vizinho soltar.
O programa escreve no console cada mudança de estado (pensando, com fome, comendo) junto com o tempo desde o início, assim como registra quando um filósofo tenta pegar, pegou ou soltou um garfo.

### Por que o impasse acontece
O problema acontece quando os cinco ficam com fome mais ou menos no mesmo tempo. Cada filósofo consegue pegar o garfo esquerdo, porque ninguém estava usando. Depois todos tentam pegar o direito, mas o garfo direito de cada filósofo é o esquerdo do vizinho que já foi pego. Por consequência, cada um espera um garfo que só volta para a mesa depois que o vizinho comer, e o vizinho não come porque também está esperando. Ninguém solta nada e o programa fica parado para sempre.

Nesse caso, as quatros condições de Coffman se encontram presentes. O garfo só pode estar com um filósofo por vez (exclusão mútua), cada um segura um garfo enquanto espera o outro (manter e esperar), ninguém tira o garfo da mão do vizinho (não preempção), e por fim, a espera dá a volta na mesa: o 1 espera o 2, o 2 espera o 3, e por assim vai até chegar no 5 que espera o 1 (espera circular).

O impasse não é garantido porque depende de como o escalonador intercala as threads. Para fins de reprodução, foi utilizado um "time.sleep" entre pegar o garfo esquerdo e pegar o garfo direito. Com a pausa de 0,5 segundos entre os garfos, o impasse ocorreu durante as execuções. Porém, com a pausa em 0, não foi apresentado nenhum impasse. Quando ajustado para 0,1, ocorre ocasionalmente. O erro está presente no protocolo em todos os testes, a questão é que o tempo pode ajudar a mascarar isso.

### Como o programa detecta impasse
A thread principal olha o dicionário "estados" a cada segundo. Se todos os filósofos estiverem "com fome", ele vai esperar mais 3 segundos e vai olhar de novo. Se permanecerem com fome, conclui que travou, avisa e encerra o programa. 

Obs: O "daemon" foi utilizado para conseguir finalizar o programa.

### Como executar
Abra o cmd ou terminal correspondente (No caso abaixo, utilizamos o cmd):
```
cd parte_1
python parte_1_versao_ingenua.py
```
No topo do arquivo ficam as constantes usadas no programa. Se quiser testar sem a pausa entre pegar o garfo, basta substituir o valor da constante "PAUSA_ENTRE_GARFOS" para 0

### Pseudocódigo da versão ingênua
```
N = 5
garfos 1..N, o garfo i fica entre os filósofos i e i+1 (o garfo N fica entre N e 1)

para cada filósofo p:
    direito = p
    esquerdo = p - 1, ou N se p = 1

    repetir:
        pensar()
        estado[p] <- "com fome"
        adquirir(esquerdo)
        dormir(pausa)
        adquirir(direito)
        estado[p] <- "comendo"
        comer()
        liberar(direito)
        liberar(esquerdo)
        estado[p] <- "pensando"
```
### Log de uma execução com deadlock
```
[0.001s] Filósofo 1 está pensando
[0.001s] Filósofo 2 está pensando
[0.002s] Filósofo 3 está pensando
[0.002s] Filósofo 4 está pensando
[0.002s] Filósofo 5 está pensando
[0.220s] Filósofo 2 está com fome
[0.220s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[0.220s] Filósofo 2 pegou o garfo 1 (esquerdo)
[0.242s] Filósofo 1 está com fome
[0.243s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[0.243s] Filósofo 1 pegou o garfo 5 (esquerdo)
[0.421s] Filósofo 4 está com fome
[0.422s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[0.422s] Filósofo 4 pegou o garfo 3 (esquerdo)
[0.470s] Filósofo 5 está com fome
[0.470s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[0.470s] Filósofo 5 pegou o garfo 4 (esquerdo)
[0.501s] Filósofo 3 está com fome
[0.501s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[0.501s] Filósofo 3 pegou o garfo 2 (esquerdo)
[0.720s] Filósofo 2 tenta pegar o garfo 2 (direito)
[0.743s] Filósofo 1 tenta pegar o garfo 1 (direito)
[0.922s] Filósofo 4 tenta pegar o garfo 4 (direito)
[0.970s] Filósofo 5 tenta pegar o garfo 5 (direito)
[1.002s] Filósofo 3 tenta pegar o garfo 3 (direito)
Deadlock! Todos os filósofos continuam com fome há mais de 3 segundos e ninguém consegue comer
```
Como deu para ver: Nenhum filósofo chegou a comer. Cada um pegou o seu garfo esquerdo e ficou tentando pegar o direito, e as cinco últimas linhas do log mostram isso.

## PARTE 1 - Versão corrigida
Diferente da versão ingênua, na corrigida os filósofos tentam pegar primeiro o garfo com o menor número, em vez do garfo que está a esquerda. Caso o garfo que o filósofo quer já esteja sendo usado, a thread não fica bloqueada no "acquire" até o vizinho soltar, ela espera um tempo definido e depois tenta adquiri-lo novamente. Além disso, se o filósofo já possuir um garfo, mas falhar em conseguir o segundo, o primeiro garfo é liberado.

### Condição de Coffman
A condição de Coffman negada na versão corrigida foi a Espera circular, pois os filósofos irão tentar pegar o garfo de menor número, assim sobrará um garfo (o maior) e não será formado um ciclo completo em que cada um segura um garfo e espera o vizinho liberar o próximo garfo, formando um ciclo completo.

### Como executar
Abra o cmd ou terminal correspondente (No caso abaixo, utilizamos o cmd):
```
cd parte_1
python parte_1_versao_corrigida.py
```
No topo do arquivo ficam as constantes usadas no programa. Se quiser testar sem a pausa entre pegar o garfo, basta substituir o valor da constante "PAUSA_ENTRE_GARFOS" para 0

### Pseudocódigo da versão corrigida

### Log de uma execução sem deadlock

## PARTE 2 - Threads e semáforos

### Como funciona
O programa usa um semáforo que controla os recursos adquirindo e liberando, isso resolve o problema de sobrescrita, onde muitas threads tentam modificar a mesma variável, fazendo com que alguns resultados das threads sejam perdido.
Usando o semáforo com (with) para adquirir ele deixa só 1 thread modificara por vez e liberando para a próxima, evitando o problema da sobrescrita ao custo de mais tempo pois na área critica (with) se torna sequencial.

### GIL
O python por ser uma linguagem interpretada ele executa as instrução sequencial, o GIL (Global Interpreter Lock) impede a execução paralela. Em operações rápidas como no contador do sem semáforo e com semáforo acabam sendo iguais, o sem semáforo acaba não tendo perdas. Para poder ver essa diferença adicionamos uma pausa (time.sleep) para CPU poder passar para a outra thread e pode ver essa sobrescrita.

### Como executar
Abra o cmd ou terminal correspondente (No caso abaixo, utilizamos o cmd):

```
cd parte_2
python parte_2_Threads_semaforos.py
```
### Pseudocódigo dos semáforos
```
Globais:
count = 0
sem = Semaforo(permissoes = 1, justo = true) // binário com FIFO
Funcao tarefa():
    para i de 1 ate M:
    // VERSAO 1 — sem sincronizacao (condicao de corrida):
    count = count + 1
    // VERSAO 2 — com semaforo (correta):
    sem.adquirir()
    try:
        count = count + 1
    finally:
        sem.liberar()
Programa principal:
    iniciar T threads executando tarefa()
    esperar todas terminarem
    imprimir esperado = T*M, obtido = count, tempo = ...
```
### Log da tabela

| Versão | Execução | Esperado | Obtido | Tempo(s) | 
|---|---|---|---|---|
sem semaforo  |  1  |  1600000  |  200356  |  2.2110439999960363
sem semaforo  |  2  |  1600000  |  200184  |  3.5485205000150017
sem semaforo  |  3  |  1600000  |  200380  |  3.231002399988938
com semaforo  |  1  |  1600000  |  1600000  |  16.105979299987666
com semaforo  |  2  |  1600000  |  1600000  |  15.928699699987192
com semaforo  |  3  |  1600000  |  1600000  |  15.700154099962674


podemos ver que a versão sem semáforo acabou obtendo menos do que esperado porem em um tempo mais curto, já o com semáforo o obtido é o mesmo que esperado ou seja sem perdas porem em um tempo de execução muito maior.

## PARTE 3 - Deadlock

### Como o problema funciona
O deadlock é uma situação na qual dois ou mais processos ficam bloqueados, esperando uns pelos outros. Normalmente ocorre quando uma thread precisa de um recurso que já está com outra, e ela não é capaz de prosseguir sua tarefa pois o que ela precisa esta com a thread original, assim gerando um ciclo infinito onde nada é executado.

### Pseudocódigo da versão que trava
```
LOCK_A, LOCK_B = locks distintos
Thread 1:
adquirir(LOCK_A)
dormir(50ms) // aumenta a chance do deadlock
adquirir(LOCK_B)
imprimir "T1 concluiu"
liberar(LOCK_B)
liberar(LOCK_A)
Thread 2:
adquirir(LOCK_B)
dormir(50ms)
adquirir(LOCK_A)
imprimir "T2 concluiu"
liberar(LOCK_A)
liberar(LOCK_B)
```
### Log da execução da trava
```
Thread 1 adiquiriu LOCK_A
Thread 2 adiquiriu LOCK_B
```
Nesse cenário, ocorre o deadlock e então nenhuma das threads consegue ser concluída.

### Pseudocódigo da versão corrigida
```
Regra global: sempre adquirir LOCK_A antes de LOCK_B,
em TODAS as threads.

Thread 1 e Thread 2:
adquirir(LOCK_A)
adquirir(LOCK_B)
// secao critica
liberar(LOCK_B)
liberar(LOCK_A)
```

### Log da execução corrigida
```
Thread 1 pegou A
Thread 1 concluiu
Thread 2 pegou A
Thread 2 concluiu
```
Na versão corrigida, a thread 2 espera a thread 1 ser concluída para entar começar a executar, o que evita completamente o problema do deadlock

### Condição de Coffman
Na versão corrigida a condição quebrada foi a espera circular, já que na versão corrigida o ciclo é quebrado e as threads seguem uma mesma ordem.
