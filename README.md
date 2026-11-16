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
Diferente da versão ingênua, na corrigida os filósofos tentam pegar primeiro o garfo com o menor número (Hierarquia de recursos), em vez do garfo que está a esquerda, assim não fecha o ciclo de um esperando o ouro liberar, causando o deadlock. Quando o filoso fica com fome, ele é inserido em uma fila, e quando ambos os garfos que ele precisa estiverem livres e ele for o primeiro da fila, ele consiguirá comer e depois ira liberar os garfos e notificar os demais filósofos que estão aguardando, isso garante a justiça e faz com que todos entre na lista de espera e tenham a chance de comer.

### Condição de Coffman
A condição de Coffman negada na versão corrigida foi a Espera circular, pois os filósofos irão tentar pegar o garfo de menor número, assim sobrará um garfo (o maior) e não será formado um ciclo completo em que cada um segura um garfo e espera o vizinho liberar o próximo garfo.

### Como executar
Abra o cmd ou terminal correspondente (No caso abaixo, utilizamos o cmd):
```
cd parte_1
python parte_1_versao_corrigida.py
```
No topo do arquivo ficam as constantes usadas no programa. Se quiser testar sem a pausa entre pegar o garfo, basta substituir o valor da constante "PAUSA_ENTRE_GARFOS" para 0

### Pseudocódigo da versão corrigida
```
N = 5
garfos 1..N, o garfo i fica entre os filósofos i e i+1 (o garfo N fica entre N e 1)

para cada filósofo p:
    direito = p
    esquerdo = p - 1, ou N se p = 1
    menor = min(direito, esquerdo)
    maior = max(direito, esquerdo)

    repetir:
        pensar()
        estado[p] <- "com fome"
        fila.append(numero) //entrar na fila
        while fila[0] != numero or garfos[menor].locked() or garfos[maior].locked():
            garfos_condition.wait()  //espera notificação de liberação
        adquirir(menor)
        adquirir(maior)
        estado[p] <- "comendo"
        fila.popleft() //sair da fila
        comer()
        liberar(direito)
        liberar(esquerdo)
        garfos_condition.notify_all() //notifica liberação para quem está na fila esperando
        estado[p] <- "pensando"
```

### Log de uma execução sem deadlock
<details>
  <summary>Clique para expandir o log </summary>

```
[0.001s] Filósofo 1 está pensando
[0.002s] Filósofo 2 está pensando
[0.002s] Filósofo 3 está pensando
[0.003s] Filósofo 4 está pensando
[0.003s] Filósofo 5 está pensando
[0.163s] Filósofo 2 está com fome
[0.165s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[0.166s] Filósofo 2 pegou o garfo 1 (esquerdo)
[0.166s] Filósofo 2 tenta pegar o garfo 2 (direito)
[0.166s] Filósofo 2 pegou o garfo 2 (direito)
[0.166s] Filósofo 2 está comendo
[0.204s] Filósofo 4 está com fome
[0.204s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[0.205s] Filósofo 4 pegou o garfo 3 (esquerdo)
[0.205s] Filósofo 4 tenta pegar o garfo 4 (direito)
[0.205s] Filósofo 4 pegou o garfo 4 (direito)
[0.206s] Filósofo 4 está comendo
[0.281s] Filósofo 1 está com fome
[0.321s] Filósofo 3 está com fome
[0.322s] Filósofo 5 está com fome
[0.369s] Filósofo 4 terminou de comer.
[0.369s] Filósofo 4 soltou o garfo 4 (direito)
[0.369s] Filósofo 4 soltou o garfo 3 (esquerdo)
[0.370s] Filósofo 4 está pensando
[0.424s] Filósofo 2 terminou de comer.
[0.424s] Filósofo 2 soltou o garfo 2 (direito)
[0.424s] Filósofo 2 soltou o garfo 1 (esquerdo)
[0.424s] Filósofo 2 está pensando
[0.425s] Filósofo 1 tenta pegar o garfo 1 (direito)
[0.426s] Filósofo 1 pegou o garfo 1 (direito)
[0.426s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[0.426s] Filósofo 1 pegou o garfo 5 (esquerdo)
[0.426s] Filósofo 1 está comendo
[0.634s] Filósofo 2 está com fome
[0.654s] Filósofo 1 terminou de comer.
[0.656s] Filósofo 1 soltou o garfo 1 (direito)
[0.656s] Filósofo 1 soltou o garfo 5 (esquerdo)
[0.657s] Filósofo 1 está pensando
[0.657s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[0.657s] Filósofo 3 pegou o garfo 2 (esquerdo)
[0.657s] Filósofo 3 tenta pegar o garfo 3 (direito)
[0.657s] Filósofo 3 pegou o garfo 3 (direito)
[0.657s] Filósofo 3 está comendo
[0.717s] Filósofo 4 está com fome
[0.774s] Filósofo 3 terminou de comer.
[0.774s] Filósofo 3 soltou o garfo 3 (direito)
[0.774s] Filósofo 3 soltou o garfo 2 (esquerdo)
[0.774s] Filósofo 3 está pensando
[0.775s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[0.775s] Filósofo 5 pegou o garfo 4 (esquerdo)
[0.775s] Filósofo 5 tenta pegar o garfo 5 (direito)
[0.775s] Filósofo 5 pegou o garfo 5 (direito)
[0.775s] Filósofo 5 está comendo
[0.825s] Filósofo 1 está com fome
[0.968s] Filósofo 3 está com fome
[1.041s] Filósofo 5 terminou de comer.
[1.041s] Filósofo 5 soltou o garfo 5 (direito)
[1.041s] Filósofo 5 soltou o garfo 4 (esquerdo)
[1.042s] Filósofo 5 está pensando
[1.042s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[1.042s] Filósofo 2 pegou o garfo 1 (esquerdo)
[1.042s] Filósofo 2 tenta pegar o garfo 2 (direito)
[1.042s] Filósofo 2 pegou o garfo 2 (direito)
[1.043s] Filósofo 2 está comendo
[1.149s] Filósofo 2 terminou de comer.
[1.149s] Filósofo 2 soltou o garfo 2 (direito)
[1.150s] Filósofo 2 soltou o garfo 1 (esquerdo)
[1.150s] Filósofo 2 está pensando
[1.151s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[1.151s] Filósofo 4 pegou o garfo 3 (esquerdo)
[1.151s] Filósofo 4 tenta pegar o garfo 4 (direito)
[1.151s] Filósofo 4 pegou o garfo 4 (direito)
[1.152s] Filósofo 4 está comendo
[1.227s] Filósofo 5 está com fome
[1.443s] Filósofo 2 está com fome
[1.446s] Filósofo 4 terminou de comer.
[1.447s] Filósofo 4 soltou o garfo 4 (direito)
[1.447s] Filósofo 4 soltou o garfo 3 (esquerdo)
[1.447s] Filósofo 4 está pensando
[1.447s] Filósofo 1 tenta pegar o garfo 1 (direito)
[1.447s] Filósofo 1 pegou o garfo 1 (direito)
[1.447s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[1.447s] Filósofo 1 pegou o garfo 5 (esquerdo)
[1.447s] Filósofo 1 está comendo
[1.611s] Filósofo 1 terminou de comer.
[1.613s] Filósofo 1 soltou o garfo 1 (direito)
[1.614s] Filósofo 1 soltou o garfo 5 (esquerdo)
[1.614s] Filósofo 1 está pensando
[1.614s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[1.614s] Filósofo 3 pegou o garfo 2 (esquerdo)
[1.614s] Filósofo 3 tenta pegar o garfo 3 (direito)
[1.614s] Filósofo 3 pegou o garfo 3 (direito)
[1.614s] Filósofo 3 está comendo
[1.842s] Filósofo 3 terminou de comer.
[1.842s] Filósofo 3 soltou o garfo 3 (direito)
[1.842s] Filósofo 3 soltou o garfo 2 (esquerdo)
[1.842s] Filósofo 3 está pensando
[1.842s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[1.842s] Filósofo 5 pegou o garfo 4 (esquerdo)
[1.843s] Filósofo 5 tenta pegar o garfo 5 (direito)
[1.843s] Filósofo 5 pegou o garfo 5 (direito)
[1.843s] Filósofo 5 está comendo
[1.854s] Filósofo 4 está com fome
[2.022s] Filósofo 5 terminou de comer.
[2.022s] Filósofo 5 soltou o garfo 5 (direito)
[2.022s] Filósofo 5 soltou o garfo 4 (esquerdo)
[2.022s] Filósofo 5 está pensando
[2.022s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[2.023s] Filósofo 2 pegou o garfo 1 (esquerdo)
[2.023s] Filósofo 2 tenta pegar o garfo 2 (direito)
[2.023s] Filósofo 2 pegou o garfo 2 (direito)
[2.023s] Filósofo 2 está comendo
[2.024s] Filósofo 1 está com fome
[2.206s] Filósofo 3 está com fome
[2.257s] Filósofo 2 terminou de comer.
[2.257s] Filósofo 2 soltou o garfo 2 (direito)
[2.257s] Filósofo 2 soltou o garfo 1 (esquerdo)
[2.257s] Filósofo 2 está pensando
[2.258s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[2.258s] Filósofo 4 pegou o garfo 3 (esquerdo)
[2.258s] Filósofo 4 tenta pegar o garfo 4 (direito)
[2.258s] Filósofo 4 pegou o garfo 4 (direito)
[2.258s] Filósofo 4 está comendo
[2.409s] Filósofo 4 terminou de comer.
[2.410s] Filósofo 4 soltou o garfo 4 (direito)
[2.410s] Filósofo 4 soltou o garfo 3 (esquerdo)
[2.410s] Filósofo 4 está pensando
[2.410s] Filósofo 1 tenta pegar o garfo 1 (direito)
[2.410s] Filósofo 1 pegou o garfo 1 (direito)
[2.410s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[2.411s] Filósofo 1 pegou o garfo 5 (esquerdo)
[2.412s] Filósofo 1 está comendo
[2.439s] Filósofo 5 está com fome
[2.597s] Filósofo 2 está com fome
[2.695s] Filósofo 1 terminou de comer.
[2.695s] Filósofo 1 soltou o garfo 1 (direito)
[2.695s] Filósofo 1 soltou o garfo 5 (esquerdo)
[2.696s] Filósofo 1 está pensando
[2.697s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[2.697s] Filósofo 3 pegou o garfo 2 (esquerdo)
[2.697s] Filósofo 3 tenta pegar o garfo 3 (direito)
[2.697s] Filósofo 3 pegou o garfo 3 (direito)
[2.698s] Filósofo 3 está comendo
[2.874s] Filósofo 4 está com fome
[2.887s] Filósofo 3 terminou de comer.
[2.887s] Filósofo 3 soltou o garfo 3 (direito)
[2.887s] Filósofo 3 soltou o garfo 2 (esquerdo)
[2.889s] Filósofo 3 está pensando
[2.889s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[2.889s] Filósofo 5 pegou o garfo 4 (esquerdo)
[2.889s] Filósofo 5 tenta pegar o garfo 5 (direito)
[2.889s] Filósofo 5 pegou o garfo 5 (direito)
[2.889s] Filósofo 5 está comendo
[3.081s] Filósofo 1 está com fome
[3.181s] Filósofo 5 terminou de comer.
[3.181s] Filósofo 5 soltou o garfo 5 (direito)
[3.181s] Filósofo 5 soltou o garfo 4 (esquerdo)
[3.182s] Filósofo 5 está pensando
[3.182s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[3.182s] Filósofo 2 pegou o garfo 1 (esquerdo)
[3.182s] Filósofo 2 tenta pegar o garfo 2 (direito)
[3.182s] Filósofo 2 pegou o garfo 2 (direito)
[3.183s] Filósofo 2 está comendo
[3.198s] Filósofo 3 está com fome
[3.426s] Filósofo 5 está com fome
[3.452s] Filósofo 2 terminou de comer.
[3.452s] Filósofo 2 soltou o garfo 2 (direito)
[3.453s] Filósofo 2 soltou o garfo 1 (esquerdo)
[3.454s] Filósofo 2 está pensando
[3.454s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[3.454s] Filósofo 4 pegou o garfo 3 (esquerdo)
[3.454s] Filósofo 4 tenta pegar o garfo 4 (direito)
[3.454s] Filósofo 4 pegou o garfo 4 (direito)
[3.454s] Filósofo 4 está comendo
[3.580s] Filósofo 2 está com fome
[3.701s] Filósofo 4 terminou de comer.
[3.701s] Filósofo 4 soltou o garfo 4 (direito)
[3.701s] Filósofo 4 soltou o garfo 3 (esquerdo)
[3.701s] Filósofo 4 está pensando
[3.702s] Filósofo 1 tenta pegar o garfo 1 (direito)
[3.702s] Filósofo 1 pegou o garfo 1 (direito)
[3.702s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[3.702s] Filósofo 1 pegou o garfo 5 (esquerdo)
[3.702s] Filósofo 1 está comendo
[3.897s] Filósofo 1 terminou de comer.
[3.899s] Filósofo 1 soltou o garfo 1 (direito)
[3.899s] Filósofo 1 soltou o garfo 5 (esquerdo)
[3.900s] Filósofo 1 está pensando
[3.900s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[3.900s] Filósofo 3 pegou o garfo 2 (esquerdo)
[3.900s] Filósofo 3 tenta pegar o garfo 3 (direito)
[3.900s] Filósofo 3 pegou o garfo 3 (direito)
[3.900s] Filósofo 3 está comendo
[4.005s] Filósofo 3 terminou de comer.
[4.006s] Filósofo 3 soltou o garfo 3 (direito)
[4.006s] Filósofo 3 soltou o garfo 2 (esquerdo)
[4.006s] Filósofo 3 está pensando
[4.007s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[4.007s] Filósofo 5 pegou o garfo 4 (esquerdo)
[4.007s] Filósofo 5 tenta pegar o garfo 5 (direito)
[4.007s] Filósofo 5 pegou o garfo 5 (direito)
[4.007s] Filósofo 5 está comendo
[4.110s] Filósofo 4 está com fome
[4.208s] Filósofo 3 está com fome
[4.217s] Filósofo 1 está com fome
[4.303s] Filósofo 5 terminou de comer.
[4.303s] Filósofo 5 soltou o garfo 5 (direito)
[4.303s] Filósofo 5 soltou o garfo 4 (esquerdo)
[4.303s] Filósofo 5 está pensando
[4.304s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[4.304s] Filósofo 2 pegou o garfo 1 (esquerdo)
[4.304s] Filósofo 2 tenta pegar o garfo 2 (direito)
[4.304s] Filósofo 2 pegou o garfo 2 (direito)
[4.304s] Filósofo 2 está comendo
[4.569s] Filósofo 2 terminou de comer.
[4.569s] Filósofo 2 soltou o garfo 2 (direito)
[4.569s] Filósofo 2 soltou o garfo 1 (esquerdo)
[4.570s] Filósofo 2 está pensando
[4.571s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[4.571s] Filósofo 4 pegou o garfo 3 (esquerdo)
[4.571s] Filósofo 4 tenta pegar o garfo 4 (direito)
[4.571s] Filósofo 4 pegou o garfo 4 (direito)
[4.571s] Filósofo 4 está comendo
[4.689s] Filósofo 4 terminou de comer.
[4.689s] Filósofo 4 soltou o garfo 4 (direito)
[4.690s] Filósofo 4 soltou o garfo 3 (esquerdo)
[4.690s] Filósofo 4 está pensando
[4.690s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[4.690s] Filósofo 3 pegou o garfo 2 (esquerdo)
[4.691s] Filósofo 3 tenta pegar o garfo 3 (direito)
[4.691s] Filósofo 3 pegou o garfo 3 (direito)
[4.691s] Filósofo 3 está comendo
[4.791s] Filósofo 5 está com fome
[4.940s] Filósofo 3 terminou de comer.
[4.940s] Filósofo 3 soltou o garfo 3 (direito)
[4.941s] Filósofo 3 soltou o garfo 2 (esquerdo)
[4.941s] Filósofo 3 está pensando
[4.942s] Filósofo 1 tenta pegar o garfo 1 (direito)
[4.942s] Filósofo 1 pegou o garfo 1 (direito)
[4.942s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[4.942s] Filósofo 1 pegou o garfo 5 (esquerdo)
[4.942s] Filósofo 1 está comendo
[4.943s] Filósofo 4 está com fome
[5.011s] Filósofo 2 está com fome
[5.185s] Filósofo 1 terminou de comer.
[5.185s] Filósofo 1 soltou o garfo 1 (direito)
[5.185s] Filósofo 1 soltou o garfo 5 (esquerdo)
[5.186s] Filósofo 1 está pensando
[5.186s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[5.187s] Filósofo 5 pegou o garfo 4 (esquerdo)
[5.187s] Filósofo 5 tenta pegar o garfo 5 (direito)
[5.187s] Filósofo 5 pegou o garfo 5 (direito)
[5.187s] Filósofo 5 está comendo
[5.295s] Filósofo 5 terminou de comer.
[5.295s] Filósofo 5 soltou o garfo 5 (direito)
[5.295s] Filósofo 5 soltou o garfo 4 (esquerdo)
[5.296s] Filósofo 5 está pensando
[5.296s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[5.296s] Filósofo 4 pegou o garfo 3 (esquerdo)
[5.296s] Filósofo 4 tenta pegar o garfo 4 (direito)
[5.296s] Filósofo 4 pegou o garfo 4 (direito)
[5.297s] Filósofo 4 está comendo
[5.425s] Filósofo 4 terminou de comer.
[5.425s] Filósofo 4 soltou o garfo 4 (direito)
[5.426s] Filósofo 4 soltou o garfo 3 (esquerdo)
[5.426s] Filósofo 4 está pensando
[5.426s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[5.426s] Filósofo 2 pegou o garfo 1 (esquerdo)
[5.426s] Filósofo 2 tenta pegar o garfo 2 (direito)
[5.426s] Filósofo 2 pegou o garfo 2 (direito)
[5.427s] Filósofo 2 está comendo
[5.435s] Filósofo 3 está com fome
[5.552s] Filósofo 1 está com fome
[5.726s] Filósofo 2 terminou de comer.
[5.727s] Filósofo 2 soltou o garfo 2 (direito)
[5.728s] Filósofo 2 soltou o garfo 1 (esquerdo)
[5.728s] Filósofo 2 está pensando
[5.729s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[5.729s] Filósofo 3 pegou o garfo 2 (esquerdo)
[5.729s] Filósofo 3 tenta pegar o garfo 3 (direito)
[5.730s] Filósofo 3 pegou o garfo 3 (direito)
[5.730s] Filósofo 3 está comendo
[5.731s] Filósofo 5 está com fome
[5.771s] Filósofo 4 está com fome
[6.023s] Filósofo 3 terminou de comer.
[6.024s] Filósofo 3 soltou o garfo 3 (direito)
[6.024s] Filósofo 3 soltou o garfo 2 (esquerdo)
[6.024s] Filósofo 3 está pensando
[6.024s] Filósofo 1 tenta pegar o garfo 1 (direito)
[6.024s] Filósofo 1 pegou o garfo 1 (direito)
[6.025s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[6.025s] Filósofo 1 pegou o garfo 5 (esquerdo)
[6.025s] Filósofo 1 está comendo
[6.183s] Filósofo 2 está com fome
[6.284s] Filósofo 1 terminou de comer.
[6.284s] Filósofo 1 soltou o garfo 1 (direito)
[6.285s] Filósofo 1 soltou o garfo 5 (esquerdo)
[6.285s] Filósofo 1 está pensando
[6.286s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[6.286s] Filósofo 5 pegou o garfo 4 (esquerdo)
[6.286s] Filósofo 5 tenta pegar o garfo 5 (direito)
[6.286s] Filósofo 5 pegou o garfo 5 (direito)
[6.286s] Filósofo 5 está comendo
[6.416s] Filósofo 5 terminou de comer.
[6.418s] Filósofo 5 soltou o garfo 5 (direito)
[6.418s] Filósofo 5 soltou o garfo 4 (esquerdo)
[6.418s] Filósofo 5 está pensando
[6.419s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[6.419s] Filósofo 4 pegou o garfo 3 (esquerdo)
[6.420s] Filósofo 4 tenta pegar o garfo 4 (direito)
[6.420s] Filósofo 4 pegou o garfo 4 (direito)
[6.421s] Filósofo 4 está comendo
[6.484s] Filósofo 3 está com fome
[6.537s] Filósofo 4 terminou de comer.
[6.537s] Filósofo 4 soltou o garfo 4 (direito)
[6.538s] Filósofo 4 soltou o garfo 3 (esquerdo)
[6.538s] Filósofo 4 está pensando
[6.538s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[6.538s] Filósofo 2 pegou o garfo 1 (esquerdo)
[6.538s] Filósofo 2 tenta pegar o garfo 2 (direito)
[6.539s] Filósofo 2 pegou o garfo 2 (direito)
[6.539s] Filósofo 2 está comendo
[6.573s] Filósofo 1 está com fome
[6.794s] Filósofo 4 está com fome
[6.814s] Filósofo 2 terminou de comer.
[6.814s] Filósofo 2 soltou o garfo 2 (direito)
[6.814s] Filósofo 2 soltou o garfo 1 (esquerdo)
[6.814s] Filósofo 2 está pensando
[6.815s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[6.815s] Filósofo 3 pegou o garfo 2 (esquerdo)
[6.815s] Filósofo 3 tenta pegar o garfo 3 (direito)
[6.815s] Filósofo 3 pegou o garfo 3 (direito)
[6.816s] Filósofo 3 está comendo
[6.878s] Filósofo 5 está com fome
[6.959s] Filósofo 3 terminou de comer.
[6.959s] Filósofo 3 soltou o garfo 3 (direito)
[6.960s] Filósofo 3 soltou o garfo 2 (esquerdo)
[6.960s] Filósofo 3 está pensando
[6.961s] Filósofo 1 tenta pegar o garfo 1 (direito)
[6.961s] Filósofo 1 pegou o garfo 1 (direito)
[6.961s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[6.961s] Filósofo 1 pegou o garfo 5 (esquerdo)
[6.962s] Filósofo 1 está comendo
[7.086s] Filósofo 1 terminou de comer.
[7.086s] Filósofo 1 soltou o garfo 1 (direito)
[7.086s] Filósofo 1 soltou o garfo 5 (esquerdo)
[7.087s] Filósofo 1 está pensando
[7.087s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[7.088s] Filósofo 4 pegou o garfo 3 (esquerdo)
[7.088s] Filósofo 4 tenta pegar o garfo 4 (direito)
[7.088s] Filósofo 4 pegou o garfo 4 (direito)
[7.089s] Filósofo 4 está comendo
[7.207s] Filósofo 2 está com fome
[7.291s] Filósofo 4 terminou de comer.
[7.292s] Filósofo 4 soltou o garfo 4 (direito)
[7.292s] Filósofo 4 soltou o garfo 3 (esquerdo)
[7.292s] Filósofo 4 está pensando
[7.292s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[7.293s] Filósofo 5 pegou o garfo 4 (esquerdo)
[7.293s] Filósofo 5 tenta pegar o garfo 5 (direito)
[7.293s] Filósofo 5 pegou o garfo 5 (direito)
[7.293s] Filósofo 5 está comendo
[7.331s] Filósofo 3 está com fome
[7.465s] Filósofo 1 está com fome
[7.513s] Filósofo 5 terminou de comer.
[7.514s] Filósofo 5 soltou o garfo 5 (direito)
[7.514s] Filósofo 5 soltou o garfo 4 (esquerdo)
[7.514s] Filósofo 5 está pensando
[7.514s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[7.514s] Filósofo 2 pegou o garfo 1 (esquerdo)
[7.514s] Filósofo 2 tenta pegar o garfo 2 (direito)
[7.515s] Filósofo 2 pegou o garfo 2 (direito)
[7.515s] Filósofo 2 está comendo
[7.723s] Filósofo 5 está com fome
[7.760s] Filósofo 2 terminou de comer.
[7.760s] Filósofo 2 soltou o garfo 2 (direito)
[7.761s] Filósofo 2 soltou o garfo 1 (esquerdo)
[7.761s] Filósofo 2 está pensando
[7.761s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[7.761s] Filósofo 3 pegou o garfo 2 (esquerdo)
[7.762s] Filósofo 3 tenta pegar o garfo 3 (direito)
[7.762s] Filósofo 3 pegou o garfo 3 (direito)
[7.762s] Filósofo 3 está comendo
[7.781s] Filósofo 4 está com fome
[7.974s] Filósofo 3 terminou de comer.
[7.975s] Filósofo 3 soltou o garfo 3 (direito)
[7.975s] Filósofo 3 soltou o garfo 2 (esquerdo)
[7.975s] Filósofo 3 está pensando
[7.976s] Filósofo 1 tenta pegar o garfo 1 (direito)
[7.976s] Filósofo 1 pegou o garfo 1 (direito)
[7.976s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[7.976s] Filósofo 1 pegou o garfo 5 (esquerdo)
[7.977s] Filósofo 1 está comendo
[8.155s] Filósofo 2 está com fome
[8.204s] Filósofo 3 está com fome
[8.267s] Filósofo 1 terminou de comer.
[8.268s] Filósofo 1 soltou o garfo 1 (direito)
[8.268s] Filósofo 1 soltou o garfo 5 (esquerdo)
[8.268s] Filósofo 1 está pensando
[8.269s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[8.269s] Filósofo 5 pegou o garfo 4 (esquerdo)
[8.270s] Filósofo 5 tenta pegar o garfo 5 (direito)
[8.270s] Filósofo 5 pegou o garfo 5 (direito)
[8.270s] Filósofo 5 está comendo
[8.378s] Filósofo 5 terminou de comer.
[8.379s] Filósofo 5 soltou o garfo 5 (direito)
[8.379s] Filósofo 5 soltou o garfo 4 (esquerdo)
[8.379s] Filósofo 5 está pensando
[8.379s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[8.380s] Filósofo 4 pegou o garfo 3 (esquerdo)
[8.380s] Filósofo 4 tenta pegar o garfo 4 (direito)
[8.380s] Filósofo 4 pegou o garfo 4 (direito)
[8.380s] Filósofo 4 está comendo
[8.613s] Filósofo 4 terminou de comer.
[8.614s] Filósofo 4 soltou o garfo 4 (direito)
[8.614s] Filósofo 4 soltou o garfo 3 (esquerdo)
[8.614s] Filósofo 4 está pensando
[8.615s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[8.615s] Filósofo 2 pegou o garfo 1 (esquerdo)
[8.615s] Filósofo 2 tenta pegar o garfo 2 (direito)
[8.616s] Filósofo 2 pegou o garfo 2 (direito)
[8.616s] Filósofo 2 está comendo
[8.621s] Filósofo 1 está com fome
[8.730s] Filósofo 5 está com fome
[8.733s] Filósofo 2 terminou de comer.
[8.733s] Filósofo 2 soltou o garfo 2 (direito)
[8.733s] Filósofo 2 soltou o garfo 1 (esquerdo)
[8.734s] Filósofo 2 está pensando
[8.734s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[8.734s] Filósofo 3 pegou o garfo 2 (esquerdo)
[8.735s] Filósofo 3 tenta pegar o garfo 3 (direito)
[8.735s] Filósofo 3 pegou o garfo 3 (direito)
[8.735s] Filósofo 3 está comendo
[8.838s] Filósofo 3 terminou de comer.
[8.839s] Filósofo 3 soltou o garfo 3 (direito)
[8.839s] Filósofo 3 soltou o garfo 2 (esquerdo)
[8.839s] Filósofo 3 está pensando
[8.840s] Filósofo 1 tenta pegar o garfo 1 (direito)
[8.840s] Filósofo 1 pegou o garfo 1 (direito)
[8.840s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[8.840s] Filósofo 1 pegou o garfo 5 (esquerdo)
[8.841s] Filósofo 1 está comendo
[8.841s] Filósofo 2 está com fome
[8.945s] Filósofo 3 está com fome
[9.071s] Filósofo 4 está com fome
[9.128s] Filósofo 1 terminou de comer.
[9.129s] Filósofo 1 soltou o garfo 1 (direito)
[9.129s] Filósofo 1 soltou o garfo 5 (esquerdo)
[9.129s] Filósofo 1 está pensando
[9.130s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[9.130s] Filósofo 5 pegou o garfo 4 (esquerdo)
[9.132s] Filósofo 5 tenta pegar o garfo 5 (direito)
[9.132s] Filósofo 5 pegou o garfo 5 (direito)
[9.132s] Filósofo 5 está comendo
[9.290s] Filósofo 1 está com fome
[9.421s] Filósofo 5 terminou de comer.
[9.423s] Filósofo 5 soltou o garfo 5 (direito)
[9.425s] Filósofo 5 soltou o garfo 4 (esquerdo)
[9.427s] Filósofo 5 está pensando
[9.427s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[9.428s] Filósofo 2 pegou o garfo 1 (esquerdo)
[9.428s] Filósofo 2 tenta pegar o garfo 2 (direito)
[9.428s] Filósofo 2 pegou o garfo 2 (direito)
[9.428s] Filósofo 2 está comendo
[9.557s] Filósofo 2 terminou de comer.
[9.557s] Filósofo 2 soltou o garfo 2 (direito)
[9.558s] Filósofo 2 soltou o garfo 1 (esquerdo)
[9.558s] Filósofo 2 está pensando
[9.560s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[9.562s] Filósofo 5 está com fome
[9.564s] Filósofo 3 pegou o garfo 2 (esquerdo)
[9.566s] Filósofo 3 tenta pegar o garfo 3 (direito)
[9.568s] Filósofo 3 pegou o garfo 3 (direito)
[9.570s] Filósofo 3 está comendo
[9.680s] Filósofo 3 terminou de comer.
[9.681s] Filósofo 3 soltou o garfo 3 (direito)
[9.681s] Filósofo 3 soltou o garfo 2 (esquerdo)
[9.681s] Filósofo 3 está pensando
[9.682s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[9.682s] Filósofo 4 pegou o garfo 3 (esquerdo)
[9.682s] Filósofo 4 tenta pegar o garfo 4 (direito)
[9.682s] Filósofo 4 pegou o garfo 4 (direito)
[9.682s] Filósofo 4 está comendo
[9.804s] Filósofo 2 está com fome
[9.885s] Filósofo 4 terminou de comer.
[9.886s] Filósofo 4 soltou o garfo 4 (direito)
[9.886s] Filósofo 4 soltou o garfo 3 (esquerdo)
[9.887s] Filósofo 4 está pensando
[9.888s] Filósofo 1 tenta pegar o garfo 1 (direito)
[9.888s] Filósofo 1 pegou o garfo 1 (direito)
[9.888s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[9.889s] Filósofo 1 pegou o garfo 5 (esquerdo)
[9.889s] Filósofo 1 está comendo
[10.034s] Filósofo 1 terminou de comer.
[10.036s] Filósofo 1 soltou o garfo 1 (direito)
[10.037s] Filósofo 1 soltou o garfo 5 (esquerdo)
[10.038s] Filósofo 1 está pensando
[10.038s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[10.038s] Filósofo 5 pegou o garfo 4 (esquerdo)
[10.038s] Filósofo 5 tenta pegar o garfo 5 (direito)
[10.039s] Filósofo 5 pegou o garfo 5 (direito)
[10.039s] Filósofo 5 está comendo
[10.174s] Filósofo 3 está com fome
[10.273s] Filósofo 4 está com fome
[10.308s] Filósofo 5 terminou de comer.
[10.308s] Filósofo 5 soltou o garfo 5 (direito)
[10.308s] Filósofo 5 soltou o garfo 4 (esquerdo)
[10.309s] Filósofo 5 está pensando
[10.309s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[10.309s] Filósofo 2 pegou o garfo 1 (esquerdo)
[10.309s] Filósofo 2 tenta pegar o garfo 2 (direito)
[10.309s] Filósofo 2 pegou o garfo 2 (direito)
[10.310s] Filósofo 2 está comendo
[10.327s] Filósofo 1 está com fome
[10.476s] Filósofo 2 terminou de comer.
[10.476s] Filósofo 2 soltou o garfo 2 (direito)
[10.476s] Filósofo 2 soltou o garfo 1 (esquerdo)
[10.476s] Filósofo 2 está pensando
[10.476s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[10.477s] Filósofo 3 pegou o garfo 2 (esquerdo)
[10.477s] Filósofo 3 tenta pegar o garfo 3 (direito)
[10.477s] Filósofo 3 pegou o garfo 3 (direito)
[10.477s] Filósofo 3 está comendo
[10.578s] Filósofo 3 terminou de comer.
[10.578s] Filósofo 3 soltou o garfo 3 (direito)
[10.579s] Filósofo 3 soltou o garfo 2 (esquerdo)
[10.579s] Filósofo 3 está pensando
[10.579s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[10.579s] Filósofo 4 pegou o garfo 3 (esquerdo)
[10.579s] Filósofo 4 tenta pegar o garfo 4 (direito)
[10.579s] Filósofo 4 pegou o garfo 4 (direito)
[10.579s] Filósofo 4 está comendo
[10.611s] Filósofo 2 está com fome
[10.668s] Filósofo 5 está com fome
[10.738s] Filósofo 4 terminou de comer.
[10.739s] Filósofo 4 soltou o garfo 4 (direito)
[10.739s] Filósofo 4 soltou o garfo 3 (esquerdo)
[10.739s] Filósofo 4 está pensando
[10.739s] Filósofo 1 tenta pegar o garfo 1 (direito)
[10.740s] Filósofo 1 pegou o garfo 1 (direito)
[10.740s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[10.740s] Filósofo 1 pegou o garfo 5 (esquerdo)
[10.740s] Filósofo 1 está comendo
[10.886s] Filósofo 3 está com fome
[10.927s] Filósofo 4 está com fome
[10.993s] Filósofo 1 terminou de comer.
[10.993s] Filósofo 1 soltou o garfo 1 (direito)
[10.994s] Filósofo 1 soltou o garfo 5 (esquerdo)
[10.994s] Filósofo 1 está pensando
[10.994s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[10.995s] Filósofo 2 pegou o garfo 1 (esquerdo)
[10.995s] Filósofo 2 tenta pegar o garfo 2 (direito)
[10.995s] Filósofo 2 pegou o garfo 2 (direito)
[10.995s] Filósofo 2 está comendo
[11.112s] Filósofo 1 está com fome
[11.171s] Filósofo 2 terminou de comer.
[11.172s] Filósofo 2 soltou o garfo 2 (direito)
[11.172s] Filósofo 2 soltou o garfo 1 (esquerdo)
[11.172s] Filósofo 2 está pensando
[11.172s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[11.173s] Filósofo 5 pegou o garfo 4 (esquerdo)
[11.173s] Filósofo 5 tenta pegar o garfo 5 (direito)
[11.173s] Filósofo 5 pegou o garfo 5 (direito)
[11.173s] Filósofo 5 está comendo
[11.318s] Filósofo 5 terminou de comer.
[11.319s] Filósofo 5 soltou o garfo 5 (direito)
[11.319s] Filósofo 5 soltou o garfo 4 (esquerdo)
[11.319s] Filósofo 5 está pensando
[11.320s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[11.320s] Filósofo 3 pegou o garfo 2 (esquerdo)
[11.320s] Filósofo 3 tenta pegar o garfo 3 (direito)
[11.320s] Filósofo 3 pegou o garfo 3 (direito)
[11.321s] Filósofo 3 está comendo
[11.391s] Filósofo 2 está com fome
[11.598s] Filósofo 3 terminou de comer.
[11.599s] Filósofo 3 soltou o garfo 3 (direito)
[11.599s] Filósofo 3 soltou o garfo 2 (esquerdo)
[11.600s] Filósofo 3 está pensando
[11.600s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[11.600s] Filósofo 4 pegou o garfo 3 (esquerdo)
[11.601s] Filósofo 4 tenta pegar o garfo 4 (direito)
[11.601s] Filósofo 4 pegou o garfo 4 (direito)
[11.601s] Filósofo 4 está comendo
[11.605s] Filósofo 5 está com fome
[11.782s] Filósofo 3 está com fome
[11.892s] Filósofo 4 terminou de comer.
[11.893s] Filósofo 4 soltou o garfo 4 (direito)
[11.894s] Filósofo 4 soltou o garfo 3 (esquerdo)
[11.894s] Filósofo 4 está pensando
[11.895s] Filósofo 1 tenta pegar o garfo 1 (direito)
[11.896s] Filósofo 1 pegou o garfo 1 (direito)
[11.896s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[11.896s] Filósofo 1 pegou o garfo 5 (esquerdo)
[11.896s] Filósofo 1 está comendo
[12.151s] Filósofo 4 está com fome
[12.157s] Filósofo 1 terminou de comer.
[12.158s] Filósofo 1 soltou o garfo 1 (direito)
[12.158s] Filósofo 1 soltou o garfo 5 (esquerdo)
[12.158s] Filósofo 1 está pensando
[12.159s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[12.160s] Filósofo 2 pegou o garfo 1 (esquerdo)
[12.160s] Filósofo 2 tenta pegar o garfo 2 (direito)
[12.160s] Filósofo 2 pegou o garfo 2 (direito)
[12.160s] Filósofo 2 está comendo
[12.335s] Filósofo 1 está com fome
[12.422s] Filósofo 2 terminou de comer.
[12.423s] Filósofo 2 soltou o garfo 2 (direito)
[12.423s] Filósofo 2 soltou o garfo 1 (esquerdo)
[12.424s] Filósofo 2 está pensando
[12.424s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[12.424s] Filósofo 5 pegou o garfo 4 (esquerdo)
[12.425s] Filósofo 5 tenta pegar o garfo 5 (direito)
[12.425s] Filósofo 5 pegou o garfo 5 (direito)
[12.425s] Filósofo 5 está comendo
[12.574s] Filósofo 2 está com fome
[12.644s] Filósofo 5 terminou de comer.
[12.645s] Filósofo 5 soltou o garfo 5 (direito)
[12.647s] Filósofo 5 soltou o garfo 4 (esquerdo)
[12.649s] Filósofo 5 está pensando
[12.651s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[12.651s] Filósofo 3 pegou o garfo 2 (esquerdo)
[12.653s] Filósofo 3 tenta pegar o garfo 3 (direito)
[12.653s] Filósofo 3 pegou o garfo 3 (direito)
[12.653s] Filósofo 3 está comendo
[12.807s] Filósofo 3 terminou de comer.
[12.807s] Filósofo 3 soltou o garfo 3 (direito)
[12.808s] Filósofo 3 soltou o garfo 2 (esquerdo)
[12.808s] Filósofo 3 está pensando
[12.808s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[12.809s] Filósofo 4 pegou o garfo 3 (esquerdo)
[12.809s] Filósofo 4 tenta pegar o garfo 4 (direito)
[12.809s] Filósofo 4 pegou o garfo 4 (direito)
[12.810s] Filósofo 4 está comendo
[12.925s] Filósofo 4 terminou de comer.
[12.925s] Filósofo 4 soltou o garfo 4 (direito)
[12.925s] Filósofo 4 soltou o garfo 3 (esquerdo)
[12.926s] Filósofo 4 está pensando
[12.926s] Filósofo 1 tenta pegar o garfo 1 (direito)
[12.926s] Filósofo 1 pegou o garfo 1 (direito)
[12.926s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[12.926s] Filósofo 1 pegou o garfo 5 (esquerdo)
[12.926s] Filósofo 1 está comendo
[13.042s] Filósofo 1 terminou de comer.
[13.042s] Filósofo 1 soltou o garfo 1 (direito)
[13.043s] Filósofo 1 soltou o garfo 5 (esquerdo)
[13.043s] Filósofo 1 está pensando
[13.043s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[13.044s] Filósofo 2 pegou o garfo 1 (esquerdo)
[13.044s] Filósofo 2 tenta pegar o garfo 2 (direito)
[13.044s] Filósofo 2 pegou o garfo 2 (direito)
[13.044s] Filósofo 2 está comendo
[13.099s] Filósofo 5 está com fome
[13.099s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[13.099s] Filósofo 5 pegou o garfo 4 (esquerdo)
[13.100s] Filósofo 5 tenta pegar o garfo 5 (direito)
[13.100s] Filósofo 5 pegou o garfo 5 (direito)
[13.100s] Filósofo 5 está comendo
[13.142s] Filósofo 3 está com fome
[13.216s] Filósofo 5 terminou de comer.
[13.216s] Filósofo 5 soltou o garfo 5 (direito)
[13.216s] Filósofo 5 soltou o garfo 4 (esquerdo)
[13.216s] Filósofo 5 está pensando
[13.234s] Filósofo 2 terminou de comer.
[13.235s] Filósofo 2 soltou o garfo 2 (direito)
[13.235s] Filósofo 2 soltou o garfo 1 (esquerdo)
[13.235s] Filósofo 2 está pensando
[13.235s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[13.235s] Filósofo 3 pegou o garfo 2 (esquerdo)
[13.235s] Filósofo 3 tenta pegar o garfo 3 (direito)
[13.235s] Filósofo 3 pegou o garfo 3 (direito)
[13.235s] Filósofo 3 está comendo
[13.360s] Filósofo 4 está com fome
[13.368s] Filósofo 3 terminou de comer.
[13.368s] Filósofo 3 soltou o garfo 3 (direito)
[13.368s] Filósofo 3 soltou o garfo 2 (esquerdo)
[13.369s] Filósofo 3 está pensando
[13.369s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[13.369s] Filósofo 4 pegou o garfo 3 (esquerdo)
[13.369s] Filósofo 4 tenta pegar o garfo 4 (direito)
[13.369s] Filósofo 4 pegou o garfo 4 (direito)
[13.369s] Filósofo 4 está comendo
[13.387s] Filósofo 1 está com fome
[13.387s] Filósofo 1 tenta pegar o garfo 1 (direito)
[13.387s] Filósofo 1 pegou o garfo 1 (direito)
[13.387s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[13.387s] Filósofo 1 pegou o garfo 5 (esquerdo)
[13.387s] Filósofo 1 está comendo
[13.395s] Filósofo 5 está com fome
[13.443s] Filósofo 2 está com fome
[13.521s] Filósofo 1 terminou de comer.
[13.521s] Filósofo 1 soltou o garfo 1 (direito)
[13.522s] Filósofo 1 soltou o garfo 5 (esquerdo)
[13.522s] Filósofo 1 está pensando
[13.551s] Filósofo 4 terminou de comer.
[13.552s] Filósofo 4 soltou o garfo 4 (direito)
[13.552s] Filósofo 4 soltou o garfo 3 (esquerdo)
[13.552s] Filósofo 4 está pensando
[13.553s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[13.553s] Filósofo 5 pegou o garfo 4 (esquerdo)
[13.554s] Filósofo 5 tenta pegar o garfo 5 (direito)
[13.554s] Filósofo 5 pegou o garfo 5 (direito)
[13.554s] Filósofo 5 está comendo
[13.797s] Filósofo 4 está com fome
[13.842s] Filósofo 5 terminou de comer.
[13.843s] Filósofo 5 soltou o garfo 5 (direito)
[13.843s] Filósofo 5 soltou o garfo 4 (esquerdo)
[13.843s] Filósofo 5 está pensando
[13.843s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[13.843s] Filósofo 2 pegou o garfo 1 (esquerdo)
[13.844s] Filósofo 2 tenta pegar o garfo 2 (direito)
[13.844s] Filósofo 2 pegou o garfo 2 (direito)
[13.844s] Filósofo 2 está comendo
[13.845s] Filósofo 3 está com fome
[13.863s] Filósofo 1 está com fome
[14.005s] Filósofo 2 terminou de comer.
[14.005s] Filósofo 2 soltou o garfo 2 (direito)
[14.006s] Filósofo 2 soltou o garfo 1 (esquerdo)
[14.006s] Filósofo 2 está pensando
[14.006s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[14.006s] Filósofo 4 pegou o garfo 3 (esquerdo)
[14.006s] Filósofo 4 tenta pegar o garfo 4 (direito)
[14.007s] Filósofo 4 pegou o garfo 4 (direito)
[14.007s] Filósofo 4 está comendo
[14.126s] Filósofo 4 terminou de comer.
[14.126s] Filósofo 4 soltou o garfo 4 (direito)
[14.126s] Filósofo 4 soltou o garfo 3 (esquerdo)
[14.126s] Filósofo 4 está pensando
[14.127s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[14.127s] Filósofo 3 pegou o garfo 2 (esquerdo)
[14.127s] Filósofo 3 tenta pegar o garfo 3 (direito)
[14.127s] Filósofo 3 pegou o garfo 3 (direito)
[14.127s] Filósofo 3 está comendo
[14.312s] Filósofo 5 está com fome
[14.386s] Filósofo 2 está com fome
[14.386s] Filósofo 4 está com fome
[14.418s] Filósofo 3 terminou de comer.
[14.419s] Filósofo 3 soltou o garfo 3 (direito)
[14.419s] Filósofo 3 soltou o garfo 2 (esquerdo)
[14.419s] Filósofo 3 está pensando
[14.419s] Filósofo 1 tenta pegar o garfo 1 (direito)
[14.419s] Filósofo 1 pegou o garfo 1 (direito)
[14.419s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[14.420s] Filósofo 1 pegou o garfo 5 (esquerdo)
[14.420s] Filósofo 1 está comendo
[14.563s] Filósofo 1 terminou de comer.
[14.563s] Filósofo 1 soltou o garfo 1 (direito)
[14.563s] Filósofo 1 soltou o garfo 5 (esquerdo)
[14.563s] Filósofo 1 está pensando
[14.563s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[14.564s] Filósofo 5 pegou o garfo 4 (esquerdo)
[14.564s] Filósofo 5 tenta pegar o garfo 5 (direito)
[14.564s] Filósofo 5 pegou o garfo 5 (direito)
[14.564s] Filósofo 5 está comendo
[14.798s] Filósofo 5 terminou de comer.
[14.799s] Filósofo 5 soltou o garfo 5 (direito)
[14.799s] Filósofo 5 soltou o garfo 4 (esquerdo)
[14.799s] Filósofo 5 está pensando
[14.799s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[14.799s] Filósofo 2 pegou o garfo 1 (esquerdo)
[14.799s] Filósofo 2 tenta pegar o garfo 2 (direito)
[14.800s] Filósofo 2 pegou o garfo 2 (direito)
[14.800s] Filósofo 2 está comendo
[14.866s] Filósofo 3 está com fome
[14.992s] Filósofo 1 está com fome
[15.048s] Filósofo 2 terminou de comer.
[15.049s] Filósofo 2 soltou o garfo 2 (direito)
[15.049s] Filósofo 2 soltou o garfo 1 (esquerdo)
[15.049s] Filósofo 2 está pensando
[15.049s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[15.049s] Filósofo 4 pegou o garfo 3 (esquerdo)
[15.050s] Filósofo 4 tenta pegar o garfo 4 (direito)
[15.050s] Filósofo 4 pegou o garfo 4 (direito)
[15.050s] Filósofo 4 está comendo
[15.175s] Filósofo 5 está com fome
[15.336s] Filósofo 4 terminou de comer.
[15.336s] Filósofo 4 soltou o garfo 4 (direito)
[15.336s] Filósofo 4 soltou o garfo 3 (esquerdo)
[15.336s] Filósofo 4 está pensando
[15.337s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[15.337s] Filósofo 3 pegou o garfo 2 (esquerdo)
[15.337s] Filósofo 3 tenta pegar o garfo 3 (direito)
[15.337s] Filósofo 3 pegou o garfo 3 (direito)
[15.337s] Filósofo 3 está comendo
[15.441s] Filósofo 2 está com fome
[15.583s] Filósofo 3 terminou de comer.
[15.584s] Filósofo 3 soltou o garfo 3 (direito)
[15.584s] Filósofo 3 soltou o garfo 2 (esquerdo)
[15.584s] Filósofo 3 está pensando
[15.584s] Filósofo 1 tenta pegar o garfo 1 (direito)
[15.584s] Filósofo 1 pegou o garfo 1 (direito)
[15.584s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[15.585s] Filósofo 1 pegou o garfo 5 (esquerdo)
[15.585s] Filósofo 1 está comendo
[15.625s] Filósofo 4 está com fome
[15.713s] Filósofo 1 terminou de comer.
[15.713s] Filósofo 1 soltou o garfo 1 (direito)
[15.713s] Filósofo 1 soltou o garfo 5 (esquerdo)
[15.713s] Filósofo 1 está pensando
[15.714s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[15.714s] Filósofo 5 pegou o garfo 4 (esquerdo)
[15.714s] Filósofo 5 tenta pegar o garfo 5 (direito)
[15.714s] Filósofo 5 pegou o garfo 5 (direito)
[15.714s] Filósofo 5 está comendo
[15.746s] Filósofo 3 está com fome
[15.956s] Filósofo 5 terminou de comer.
[15.958s] Filósofo 5 soltou o garfo 5 (direito)
[15.958s] Filósofo 5 soltou o garfo 4 (esquerdo)
[15.958s] Filósofo 5 está pensando
[15.958s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[15.958s] Filósofo 2 pegou o garfo 1 (esquerdo)
[15.959s] Filósofo 2 tenta pegar o garfo 2 (direito)
[15.959s] Filósofo 2 pegou o garfo 2 (direito)
[15.959s] Filósofo 2 está comendo
[16.109s] Filósofo 1 está com fome
[16.235s] Filósofo 2 terminou de comer.
[16.235s] Filósofo 2 soltou o garfo 2 (direito)
[16.235s] Filósofo 2 soltou o garfo 1 (esquerdo)
[16.235s] Filósofo 2 está pensando
[16.235s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[16.235s] Filósofo 4 pegou o garfo 3 (esquerdo)
[16.235s] Filósofo 4 tenta pegar o garfo 4 (direito)
[16.236s] Filósofo 4 pegou o garfo 4 (direito)
[16.236s] Filósofo 4 está comendo
[16.362s] Filósofo 5 está com fome
[16.416s] Filósofo 4 terminou de comer.
[16.417s] Filósofo 4 soltou o garfo 4 (direito)
[16.417s] Filósofo 4 soltou o garfo 3 (esquerdo)
[16.417s] Filósofo 4 está pensando
[16.417s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[16.417s] Filósofo 3 pegou o garfo 2 (esquerdo)
[16.417s] Filósofo 3 tenta pegar o garfo 3 (direito)
[16.417s] Filósofo 3 pegou o garfo 3 (direito)
[16.418s] Filósofo 3 está comendo
[16.584s] Filósofo 2 está com fome
[16.587s] Filósofo 3 terminou de comer.
[16.587s] Filósofo 3 soltou o garfo 3 (direito)
[16.587s] Filósofo 3 soltou o garfo 2 (esquerdo)
[16.587s] Filósofo 3 está pensando
[16.587s] Filósofo 1 tenta pegar o garfo 1 (direito)
[16.587s] Filósofo 1 pegou o garfo 1 (direito)
[16.587s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[16.588s] Filósofo 1 pegou o garfo 5 (esquerdo)
[16.588s] Filósofo 1 está comendo
[16.711s] Filósofo 4 está com fome
[16.770s] Filósofo 1 terminou de comer.
[16.770s] Filósofo 1 soltou o garfo 1 (direito)
[16.770s] Filósofo 1 soltou o garfo 5 (esquerdo)
[16.771s] Filósofo 1 está pensando
[16.771s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[16.771s] Filósofo 5 pegou o garfo 4 (esquerdo)
[16.771s] Filósofo 5 tenta pegar o garfo 5 (direito)
[16.771s] Filósofo 5 pegou o garfo 5 (direito)
[16.772s] Filósofo 5 está comendo
[16.931s] Filósofo 3 está com fome
[17.001s] Filósofo 5 terminou de comer.
[17.002s] Filósofo 5 soltou o garfo 5 (direito)
[17.002s] Filósofo 5 soltou o garfo 4 (esquerdo)
[17.003s] Filósofo 5 está pensando
[17.003s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[17.003s] Filósofo 2 pegou o garfo 1 (esquerdo)
[17.004s] Filósofo 2 tenta pegar o garfo 2 (direito)
[17.004s] Filósofo 2 pegou o garfo 2 (direito)
[17.004s] Filósofo 2 está comendo
[17.160s] Filósofo 5 está com fome
[17.256s] Filósofo 1 está com fome
[17.295s] Filósofo 2 terminou de comer.
[17.296s] Filósofo 2 soltou o garfo 2 (direito)
[17.296s] Filósofo 2 soltou o garfo 1 (esquerdo)
[17.296s] Filósofo 2 está pensando
[17.297s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[17.297s] Filósofo 4 pegou o garfo 3 (esquerdo)
[17.297s] Filósofo 4 tenta pegar o garfo 4 (direito)
[17.297s] Filósofo 4 pegou o garfo 4 (direito)
[17.297s] Filósofo 4 está comendo
[17.518s] Filósofo 2 está com fome
[17.521s] Filósofo 4 terminou de comer.
[17.521s] Filósofo 4 soltou o garfo 4 (direito)
[17.521s] Filósofo 4 soltou o garfo 3 (esquerdo)
[17.521s] Filósofo 4 está pensando
[17.522s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[17.522s] Filósofo 3 pegou o garfo 2 (esquerdo)
[17.522s] Filósofo 3 tenta pegar o garfo 3 (direito)
[17.522s] Filósofo 3 pegou o garfo 3 (direito)
[17.522s] Filósofo 3 está comendo
[17.623s] Filósofo 3 terminou de comer.
[17.624s] Filósofo 3 soltou o garfo 3 (direito)
[17.624s] Filósofo 3 soltou o garfo 2 (esquerdo)
[17.624s] Filósofo 3 está pensando
[17.624s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[17.624s] Filósofo 5 pegou o garfo 4 (esquerdo)
[17.624s] Filósofo 5 tenta pegar o garfo 5 (direito)
[17.624s] Filósofo 5 pegou o garfo 5 (direito)
[17.624s] Filósofo 5 está comendo
[17.751s] Filósofo 4 está com fome
[17.757s] Filósofo 5 terminou de comer.
[17.757s] Filósofo 5 soltou o garfo 5 (direito)
[17.757s] Filósofo 5 soltou o garfo 4 (esquerdo)
[17.757s] Filósofo 5 está pensando
[17.757s] Filósofo 1 tenta pegar o garfo 1 (direito)
[17.758s] Filósofo 1 pegou o garfo 1 (direito)
[17.758s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[17.758s] Filósofo 1 pegou o garfo 5 (esquerdo)
[17.758s] Filósofo 1 está comendo
[17.782s] Filósofo 3 está com fome
[18.033s] Filósofo 5 está com fome
[18.039s] Filósofo 1 terminou de comer.
[18.040s] Filósofo 1 soltou o garfo 1 (direito)
[18.040s] Filósofo 1 soltou o garfo 5 (esquerdo)
[18.040s] Filósofo 1 está pensando
[18.040s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[18.040s] Filósofo 2 pegou o garfo 1 (esquerdo)
[18.041s] Filósofo 2 tenta pegar o garfo 2 (direito)
[18.041s] Filósofo 2 pegou o garfo 2 (direito)
[18.041s] Filósofo 2 está comendo
[18.255s] Filósofo 1 está com fome
[18.287s] Filósofo 2 terminou de comer.
[18.288s] Filósofo 2 soltou o garfo 2 (direito)
[18.288s] Filósofo 2 soltou o garfo 1 (esquerdo)
[18.288s] Filósofo 2 está pensando
[18.288s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[18.288s] Filósofo 4 pegou o garfo 3 (esquerdo)
[18.288s] Filósofo 4 tenta pegar o garfo 4 (direito)
[18.288s] Filósofo 4 pegou o garfo 4 (direito)
[18.288s] Filósofo 4 está comendo
[18.418s] Filósofo 4 terminou de comer.
[18.419s] Filósofo 4 soltou o garfo 4 (direito)
[18.419s] Filósofo 4 soltou o garfo 3 (esquerdo)
[18.419s] Filósofo 4 está pensando
[18.420s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[18.420s] Filósofo 3 pegou o garfo 2 (esquerdo)
[18.420s] Filósofo 3 tenta pegar o garfo 3 (direito)
[18.420s] Filósofo 3 pegou o garfo 3 (direito)
[18.420s] Filósofo 3 está comendo
[18.545s] Filósofo 3 terminou de comer.
[18.547s] Filósofo 3 soltou o garfo 3 (direito)
[18.547s] Filósofo 3 soltou o garfo 2 (esquerdo)
[18.547s] Filósofo 3 está pensando
[18.547s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[18.547s] Filósofo 5 pegou o garfo 4 (esquerdo)
[18.547s] Filósofo 5 tenta pegar o garfo 5 (direito)
[18.547s] Filósofo 5 pegou o garfo 5 (direito)
[18.547s] Filósofo 5 está comendo
[18.593s] Filósofo 4 está com fome
[18.594s] Filósofo 2 está com fome
[18.704s] Filósofo 5 terminou de comer.
[18.704s] Filósofo 5 soltou o garfo 5 (direito)
[18.704s] Filósofo 5 soltou o garfo 4 (esquerdo)
[18.705s] Filósofo 5 está pensando
[18.706s] Filósofo 1 tenta pegar o garfo 1 (direito)
[18.706s] Filósofo 1 pegou o garfo 1 (direito)
[18.706s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[18.706s] Filósofo 1 pegou o garfo 5 (esquerdo)
[18.706s] Filósofo 1 está comendo
[18.770s] Filósofo 3 está com fome
[18.892s] Filósofo 1 terminou de comer.
[18.894s] Filósofo 1 soltou o garfo 1 (direito)
[18.898s] Filósofo 1 soltou o garfo 5 (esquerdo)
[18.900s] Filósofo 1 está pensando
[18.901s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[18.901s] Filósofo 4 pegou o garfo 3 (esquerdo)
[18.904s] Filósofo 4 tenta pegar o garfo 4 (direito)
[18.905s] Filósofo 4 pegou o garfo 4 (direito)
[18.906s] Filósofo 4 está comendo
[19.051s] Filósofo 4 terminou de comer.
[19.051s] Filósofo 4 soltou o garfo 4 (direito)
[19.051s] Filósofo 4 soltou o garfo 3 (esquerdo)
[19.052s] Filósofo 4 está pensando
[19.052s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[19.052s] Filósofo 2 pegou o garfo 1 (esquerdo)
[19.052s] Filósofo 2 tenta pegar o garfo 2 (direito)
[19.052s] Filósofo 2 pegou o garfo 2 (direito)
[19.052s] Filósofo 2 está comendo
[19.173s] Filósofo 5 está com fome
[19.199s] Filósofo 2 terminou de comer.
[19.200s] Filósofo 2 soltou o garfo 2 (direito)
[19.200s] Filósofo 2 soltou o garfo 1 (esquerdo)
[19.200s] Filósofo 1 está com fome
[19.200s] Filósofo 2 está pensando
[19.200s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[19.200s] Filósofo 3 pegou o garfo 2 (esquerdo)
[19.200s] Filósofo 3 tenta pegar o garfo 3 (direito)
[19.201s] Filósofo 3 pegou o garfo 3 (direito)
[19.201s] Filósofo 3 está comendo
[19.406s] Filósofo 3 terminou de comer.
[19.407s] Filósofo 3 soltou o garfo 3 (direito)
[19.407s] Filósofo 3 soltou o garfo 2 (esquerdo)
[19.408s] Filósofo 3 está pensando
[19.408s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[19.408s] Filósofo 5 pegou o garfo 4 (esquerdo)
[19.408s] Filósofo 5 tenta pegar o garfo 5 (direito)
[19.408s] Filósofo 5 pegou o garfo 5 (direito)
[19.408s] Filósofo 5 está comendo
[19.420s] Filósofo 2 está com fome
[19.429s] Filósofo 4 está com fome
[19.617s] Filósofo 5 terminou de comer.
[19.617s] Filósofo 5 soltou o garfo 5 (direito)
[19.618s] Filósofo 5 soltou o garfo 4 (esquerdo)
[19.618s] Filósofo 5 está pensando
[19.619s] Filósofo 1 tenta pegar o garfo 1 (direito)
[19.619s] Filósofo 1 pegou o garfo 1 (direito)
[19.619s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[19.619s] Filósofo 1 pegou o garfo 5 (esquerdo)
[19.619s] Filósofo 1 está comendo
[19.756s] Filósofo 3 está com fome
[19.894s] Filósofo 1 terminou de comer.
[19.894s] Filósofo 1 soltou o garfo 1 (direito)
[19.894s] Filósofo 1 soltou o garfo 5 (esquerdo)
[19.894s] Filósofo 1 está pensando
[19.894s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[19.895s] Filósofo 2 pegou o garfo 1 (esquerdo)
[19.895s] Filósofo 2 tenta pegar o garfo 2 (direito)
[19.895s] Filósofo 2 pegou o garfo 2 (direito)
[19.895s] Filósofo 2 está comendo
[19.895s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[19.896s] Filósofo 4 pegou o garfo 3 (esquerdo)
[19.896s] Filósofo 4 tenta pegar o garfo 4 (direito)
[19.897s] Filósofo 4 pegou o garfo 4 (direito)
[19.897s] Filósofo 4 está comendo
[19.972s] Filósofo 5 está com fome
[20.053s] Filósofo 2 terminou de comer.
[20.053s] Filósofo 2 soltou o garfo 2 (direito)
[20.054s] Filósofo 2 soltou o garfo 1 (esquerdo)
[20.054s] Filósofo 2 está pensando
[20.091s] Filósofo 4 terminou de comer.
[20.091s] Filósofo 4 soltou o garfo 4 (direito)
[20.091s] Filósofo 4 soltou o garfo 3 (esquerdo)
[20.091s] Filósofo 4 está pensando
[20.091s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[20.092s] Filósofo 3 pegou o garfo 2 (esquerdo)
[20.092s] Filósofo 3 tenta pegar o garfo 3 (direito)
[20.092s] Filósofo 3 pegou o garfo 3 (direito)
[20.092s] Filósofo 3 está comendo
[20.200s] Filósofo 3 terminou de comer.
[20.200s] Filósofo 3 soltou o garfo 3 (direito)
[20.200s] Filósofo 3 soltou o garfo 2 (esquerdo)
[20.201s] Filósofo 3 está pensando
[20.202s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[20.202s] Filósofo 5 pegou o garfo 4 (esquerdo)
[20.202s] Filósofo 5 tenta pegar o garfo 5 (direito)
[20.202s] Filósofo 5 pegou o garfo 5 (direito)
[20.202s] Filósofo 5 está comendo
[20.280s] Filósofo 1 está com fome
[20.328s] Filósofo 5 terminou de comer.
[20.328s] Filósofo 5 soltou o garfo 5 (direito)
[20.329s] Filósofo 5 soltou o garfo 4 (esquerdo)
[20.329s] Filósofo 5 está pensando
[20.329s] Filósofo 1 tenta pegar o garfo 1 (direito)
[20.329s] Filósofo 1 pegou o garfo 1 (direito)
[20.329s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[20.329s] Filósofo 1 pegou o garfo 5 (esquerdo)
[20.329s] Filósofo 1 está comendo
[20.421s] Filósofo 2 está com fome
[20.450s] Filósofo 4 está com fome
[20.510s] Filósofo 3 está com fome
[20.527s] Filósofo 1 terminou de comer.
[20.527s] Filósofo 1 soltou o garfo 1 (direito)
[20.527s] Filósofo 1 soltou o garfo 5 (esquerdo)
[20.527s] Filósofo 1 está pensando
[20.528s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[20.528s] Filósofo 2 pegou o garfo 1 (esquerdo)
[20.528s] Filósofo 2 tenta pegar o garfo 2 (direito)
[20.528s] Filósofo 2 pegou o garfo 2 (direito)
[20.528s] Filósofo 2 está comendo
[20.648s] Filósofo 2 terminou de comer.
[20.649s] Filósofo 2 soltou o garfo 2 (direito)
[20.649s] Filósofo 2 soltou o garfo 1 (esquerdo)
[20.649s] Filósofo 2 está pensando
[20.649s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[20.649s] Filósofo 4 pegou o garfo 3 (esquerdo)
[20.649s] Filósofo 4 tenta pegar o garfo 4 (direito)
[20.650s] Filósofo 4 pegou o garfo 4 (direito)
[20.650s] Filósofo 4 está comendo
[20.683s] Filósofo 5 está com fome
[20.784s] Filósofo 4 terminou de comer.
[20.785s] Filósofo 4 soltou o garfo 4 (direito)
[20.785s] Filósofo 4 soltou o garfo 3 (esquerdo)
[20.785s] Filósofo 4 está pensando
[20.785s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[20.785s] Filósofo 3 pegou o garfo 2 (esquerdo)
[20.785s] Filósofo 3 tenta pegar o garfo 3 (direito)
[20.785s] Filósofo 3 pegou o garfo 3 (direito)
[20.785s] Filósofo 3 está comendo
[20.921s] Filósofo 4 está com fome
[20.934s] Filósofo 3 terminou de comer.
[20.935s] Filósofo 3 soltou o garfo 3 (direito)
[20.935s] Filósofo 3 soltou o garfo 2 (esquerdo)
[20.935s] Filósofo 3 está pensando
[20.935s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[20.935s] Filósofo 5 pegou o garfo 4 (esquerdo)
[20.935s] Filósofo 5 tenta pegar o garfo 5 (direito)
[20.935s] Filósofo 5 pegou o garfo 5 (direito)
[20.935s] Filósofo 5 está comendo
[20.938s] Filósofo 2 está com fome
[21.005s] Filósofo 1 está com fome
[21.103s] Filósofo 5 terminou de comer.
[21.104s] Filósofo 5 soltou o garfo 5 (direito)
[21.104s] Filósofo 5 soltou o garfo 4 (esquerdo)
[21.104s] Filósofo 5 está pensando
[21.104s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[21.104s] Filósofo 4 pegou o garfo 3 (esquerdo)
[21.104s] Filósofo 4 tenta pegar o garfo 4 (direito)
[21.104s] Filósofo 4 pegou o garfo 4 (direito)
[21.104s] Filósofo 4 está comendo
[21.201s] Filósofo 3 está com fome
[21.213s] Filósofo 4 terminou de comer.
[21.214s] Filósofo 4 soltou o garfo 4 (direito)
[21.214s] Filósofo 4 soltou o garfo 3 (esquerdo)
[21.214s] Filósofo 4 está pensando
[21.214s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[21.215s] Filósofo 2 pegou o garfo 1 (esquerdo)
[21.215s] Filósofo 2 tenta pegar o garfo 2 (direito)
[21.215s] Filósofo 2 pegou o garfo 2 (direito)
[21.215s] Filósofo 2 está comendo
[21.271s] Filósofo 5 está com fome
[21.392s] Filósofo 2 terminou de comer.
[21.392s] Filósofo 2 soltou o garfo 2 (direito)
[21.393s] Filósofo 2 soltou o garfo 1 (esquerdo)
[21.393s] Filósofo 2 está pensando
[21.393s] Filósofo 1 tenta pegar o garfo 1 (direito)
[21.393s] Filósofo 1 pegou o garfo 1 (direito)
[21.394s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[21.394s] Filósofo 1 pegou o garfo 5 (esquerdo)
[21.394s] Filósofo 1 está comendo
[21.400s] Filósofo 4 está com fome
[21.541s] Filósofo 1 terminou de comer.
[21.541s] Filósofo 1 soltou o garfo 1 (direito)
[21.542s] Filósofo 1 soltou o garfo 5 (esquerdo)
[21.542s] Filósofo 1 está pensando
[21.542s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[21.542s] Filósofo 3 pegou o garfo 2 (esquerdo)
[21.542s] Filósofo 3 tenta pegar o garfo 3 (direito)
[21.542s] Filósofo 3 pegou o garfo 3 (direito)
[21.542s] Filósofo 3 está comendo
[21.839s] Filósofo 3 terminou de comer.
[21.839s] Filósofo 3 soltou o garfo 3 (direito)
[21.840s] Filósofo 3 soltou o garfo 2 (esquerdo)
[21.840s] Filósofo 3 está pensando
[21.840s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[21.840s] Filósofo 5 pegou o garfo 4 (esquerdo)
[21.840s] Filósofo 5 tenta pegar o garfo 5 (direito)
[21.840s] Filósofo 5 pegou o garfo 5 (direito)
[21.840s] Filósofo 5 está comendo
[21.843s] Filósofo 1 está com fome
[21.885s] Filósofo 2 está com fome
[22.056s] Filósofo 5 terminou de comer.
[22.057s] Filósofo 5 soltou o garfo 5 (direito)
[22.057s] Filósofo 5 soltou o garfo 4 (esquerdo)
[22.057s] Filósofo 5 está pensando
[22.057s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[22.057s] Filósofo 4 pegou o garfo 3 (esquerdo)
[22.057s] Filósofo 4 tenta pegar o garfo 4 (direito)
[22.057s] Filósofo 4 pegou o garfo 4 (direito)
[22.058s] Filósofo 4 está comendo
[22.058s] Filósofo 1 tenta pegar o garfo 1 (direito)
[22.058s] Filósofo 1 pegou o garfo 1 (direito)
[22.058s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[22.058s] Filósofo 1 pegou o garfo 5 (esquerdo)
[22.058s] Filósofo 1 está comendo
[22.214s] Filósofo 4 terminou de comer.
[22.214s] Filósofo 4 soltou o garfo 4 (direito)
[22.215s] Filósofo 4 soltou o garfo 3 (esquerdo)
[22.215s] Filósofo 4 está pensando
[22.216s] Filósofo 3 está com fome
[22.322s] Filósofo 1 terminou de comer.
[22.323s] Filósofo 1 soltou o garfo 1 (direito)
[22.323s] Filósofo 1 soltou o garfo 5 (esquerdo)
[22.323s] Filósofo 1 está pensando
[22.323s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[22.323s] Filósofo 2 pegou o garfo 1 (esquerdo)
[22.323s] Filósofo 2 tenta pegar o garfo 2 (direito)
[22.323s] Filósofo 2 pegou o garfo 2 (direito)
[22.323s] Filósofo 2 está comendo
[22.412s] Filósofo 5 está com fome
[22.430s] Filósofo 4 está com fome
[22.498s] Filósofo 2 terminou de comer.
[22.498s] Filósofo 2 soltou o garfo 2 (direito)
[22.498s] Filósofo 2 soltou o garfo 1 (esquerdo)
[22.498s] Filósofo 2 está pensando
[22.499s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[22.500s] Filósofo 3 pegou o garfo 2 (esquerdo)
[22.500s] Filósofo 3 tenta pegar o garfo 3 (direito)
[22.500s] Filósofo 3 pegou o garfo 3 (direito)
[22.500s] Filósofo 3 está comendo
[22.549s] Filósofo 1 está com fome
[22.635s] Filósofo 3 terminou de comer.
[22.637s] Filósofo 3 soltou o garfo 3 (direito)
[22.639s] Filósofo 3 soltou o garfo 2 (esquerdo)
[22.639s] Filósofo 3 está pensando
[22.643s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[22.644s] Filósofo 5 pegou o garfo 4 (esquerdo)
[22.644s] Filósofo 5 tenta pegar o garfo 5 (direito)
[22.644s] Filósofo 5 pegou o garfo 5 (direito)
[22.644s] Filósofo 5 está comendo
[22.717s] Filósofo 2 está com fome
[22.768s] Filósofo 5 terminou de comer.
[22.769s] Filósofo 5 soltou o garfo 5 (direito)
[22.770s] Filósofo 5 soltou o garfo 4 (esquerdo)
[22.770s] Filósofo 5 está pensando
[22.770s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[22.771s] Filósofo 4 pegou o garfo 3 (esquerdo)
[22.771s] Filósofo 4 tenta pegar o garfo 4 (direito)
[22.771s] Filósofo 4 pegou o garfo 4 (direito)
[22.771s] Filósofo 4 está comendo
[22.964s] Filósofo 4 terminou de comer.
[22.968s] Filósofo 4 soltou o garfo 4 (direito)
[22.971s] Filósofo 4 soltou o garfo 3 (esquerdo)
[22.972s] Filósofo 4 está pensando
[22.975s] Filósofo 1 tenta pegar o garfo 1 (direito)
[22.975s] Filósofo 1 pegou o garfo 1 (direito)
[22.976s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[22.976s] Filósofo 1 pegou o garfo 5 (esquerdo)
[22.976s] Filósofo 1 está comendo
[23.009s] Filósofo 3 está com fome
[23.108s] Filósofo 5 está com fome
[23.120s] Filósofo 1 terminou de comer.
[23.123s] Filósofo 1 soltou o garfo 1 (direito)
[23.126s] Filósofo 1 soltou o garfo 5 (esquerdo)
[23.127s] Filósofo 1 está pensando
[23.130s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[23.130s] Filósofo 2 pegou o garfo 1 (esquerdo)
[23.131s] Filósofo 2 tenta pegar o garfo 2 (direito)
[23.131s] Filósofo 2 pegou o garfo 2 (direito)
[23.131s] Filósofo 2 está comendo
[23.151s] Filósofo 4 está com fome
[23.273s] Filósofo 1 está com fome
[23.363s] Filósofo 2 terminou de comer.
[23.364s] Filósofo 2 soltou o garfo 2 (direito)
[23.364s] Filósofo 2 soltou o garfo 1 (esquerdo)
[23.364s] Filósofo 2 está pensando
[23.365s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[23.365s] Filósofo 3 pegou o garfo 2 (esquerdo)
[23.365s] Filósofo 3 tenta pegar o garfo 3 (direito)
[23.372s] Filósofo 3 pegou o garfo 3 (direito)
[23.373s] Filósofo 3 está comendo
[23.572s] Filósofo 2 está com fome
[23.633s] Filósofo 3 terminou de comer.
[23.640s] Filósofo 3 soltou o garfo 3 (direito)
[23.643s] Filósofo 3 soltou o garfo 2 (esquerdo)
[23.644s] Filósofo 3 está pensando
[23.646s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[23.647s] Filósofo 5 pegou o garfo 4 (esquerdo)
[23.647s] Filósofo 5 tenta pegar o garfo 5 (direito)
[23.648s] Filósofo 5 pegou o garfo 5 (direito)
[23.648s] Filósofo 5 está comendo
[23.775s] Filósofo 3 está com fome
[23.885s] Filósofo 5 terminou de comer.
[23.886s] Filósofo 5 soltou o garfo 5 (direito)
[23.889s] Filósofo 5 soltou o garfo 4 (esquerdo)
[23.889s] Filósofo 5 está pensando
[23.889s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[23.890s] Filósofo 4 pegou o garfo 3 (esquerdo)
[23.890s] Filósofo 4 tenta pegar o garfo 4 (direito)
[23.890s] Filósofo 4 pegou o garfo 4 (direito)
[23.890s] Filósofo 4 está comendo
[24.109s] Filósofo 4 terminou de comer.
[24.109s] Filósofo 4 soltou o garfo 4 (direito)
[24.110s] Filósofo 4 soltou o garfo 3 (esquerdo)
[24.110s] Filósofo 4 está pensando
[24.110s] Filósofo 1 tenta pegar o garfo 1 (direito)
[24.110s] Filósofo 1 pegou o garfo 1 (direito)
[24.110s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[24.110s] Filósofo 1 pegou o garfo 5 (esquerdo)
[24.110s] Filósofo 1 está comendo
[24.292s] Filósofo 1 terminou de comer.
[24.293s] Filósofo 1 soltou o garfo 1 (direito)
[24.293s] Filósofo 1 soltou o garfo 5 (esquerdo)
[24.293s] Filósofo 1 está pensando
[24.294s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[24.294s] Filósofo 2 pegou o garfo 1 (esquerdo)
[24.294s] Filósofo 2 tenta pegar o garfo 2 (direito)
[24.294s] Filósofo 2 pegou o garfo 2 (direito)
[24.294s] Filósofo 2 está comendo
[24.337s] Filósofo 5 está com fome
[24.388s] Filósofo 4 está com fome
[24.454s] Filósofo 1 está com fome
[24.506s] Filósofo 2 terminou de comer.
[24.520s] Filósofo 2 soltou o garfo 2 (direito)
[24.523s] Filósofo 2 soltou o garfo 1 (esquerdo)
[24.526s] Filósofo 2 está pensando
[24.528s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[24.528s] Filósofo 3 pegou o garfo 2 (esquerdo)
[24.529s] Filósofo 3 tenta pegar o garfo 3 (direito)
[24.529s] Filósofo 3 pegou o garfo 3 (direito)
[24.532s] Filósofo 3 está comendo
[24.647s] Filósofo 3 terminou de comer.
[24.647s] Filósofo 3 soltou o garfo 3 (direito)
[24.647s] Filósofo 3 soltou o garfo 2 (esquerdo)
[24.648s] Filósofo 3 está pensando
[24.648s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[24.648s] Filósofo 5 pegou o garfo 4 (esquerdo)
[24.648s] Filósofo 5 tenta pegar o garfo 5 (direito)
[24.649s] Filósofo 5 pegou o garfo 5 (direito)
[24.649s] Filósofo 5 está comendo
[24.848s] Filósofo 5 terminou de comer.
[24.848s] Filósofo 5 soltou o garfo 5 (direito)
[24.848s] Filósofo 5 soltou o garfo 4 (esquerdo)
[24.848s] Filósofo 5 está pensando
[24.848s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[24.848s] Filósofo 4 pegou o garfo 3 (esquerdo)
[24.848s] Filósofo 4 tenta pegar o garfo 4 (direito)
[24.849s] Filósofo 4 pegou o garfo 4 (direito)
[24.849s] Filósofo 4 está comendo
[24.971s] Filósofo 2 está com fome
[24.991s] Filósofo 3 está com fome
[25.063s] Filósofo 5 está com fome
[25.146s] Filósofo 4 terminou de comer.
[25.146s] Filósofo 4 soltou o garfo 4 (direito)
[25.146s] Filósofo 4 soltou o garfo 3 (esquerdo)
[25.147s] Filósofo 4 está pensando
[25.147s] Filósofo 1 tenta pegar o garfo 1 (direito)
[25.147s] Filósofo 1 pegou o garfo 1 (direito)
[25.147s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[25.147s] Filósofo 1 pegou o garfo 5 (esquerdo)
[25.147s] Filósofo 1 está comendo
[25.391s] Filósofo 1 terminou de comer.
[25.391s] Filósofo 1 soltou o garfo 1 (direito)
[25.391s] Filósofo 1 soltou o garfo 5 (esquerdo)
[25.392s] Filósofo 1 está pensando
[25.392s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[25.392s] Filósofo 2 pegou o garfo 1 (esquerdo)
[25.392s] Filósofo 2 tenta pegar o garfo 2 (direito)
[25.392s] Filósofo 2 pegou o garfo 2 (direito)
[25.392s] Filósofo 2 está comendo
[25.409s] Filósofo 4 está com fome
[25.527s] Filósofo 2 terminou de comer.
[25.528s] Filósofo 2 soltou o garfo 2 (direito)
[25.528s] Filósofo 2 soltou o garfo 1 (esquerdo)
[25.528s] Filósofo 2 está pensando
[25.529s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[25.529s] Filósofo 3 pegou o garfo 2 (esquerdo)
[25.529s] Filósofo 3 tenta pegar o garfo 3 (direito)
[25.529s] Filósofo 3 pegou o garfo 3 (direito)
[25.529s] Filósofo 3 está comendo
[25.629s] Filósofo 1 está com fome
[25.705s] Filósofo 2 está com fome
[25.719s] Filósofo 3 terminou de comer.
[25.719s] Filósofo 3 soltou o garfo 3 (direito)
[25.720s] Filósofo 3 soltou o garfo 2 (esquerdo)
[25.720s] Filósofo 3 está pensando
[25.720s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[25.720s] Filósofo 5 pegou o garfo 4 (esquerdo)
[25.720s] Filósofo 5 tenta pegar o garfo 5 (direito)
[25.720s] Filósofo 5 pegou o garfo 5 (direito)
[25.721s] Filósofo 5 está comendo
[25.834s] Filósofo 3 está com fome
[25.935s] Filósofo 5 terminou de comer.
[25.936s] Filósofo 5 soltou o garfo 5 (direito)
[25.937s] Filósofo 5 soltou o garfo 4 (esquerdo)
[25.937s] Filósofo 5 está pensando
[25.937s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[25.937s] Filósofo 4 pegou o garfo 3 (esquerdo)
[25.937s] Filósofo 4 tenta pegar o garfo 4 (direito)
[25.937s] Filósofo 4 pegou o garfo 4 (direito)
[25.937s] Filósofo 4 está comendo
[26.136s] Filósofo 4 terminou de comer.
[26.136s] Filósofo 4 soltou o garfo 4 (direito)
[26.136s] Filósofo 4 soltou o garfo 3 (esquerdo)
[26.137s] Filósofo 4 está pensando
[26.138s] Filósofo 1 tenta pegar o garfo 1 (direito)
[26.138s] Filósofo 1 pegou o garfo 1 (direito)
[26.138s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[26.138s] Filósofo 1 pegou o garfo 5 (esquerdo)
[26.138s] Filósofo 1 está comendo
[26.208s] Filósofo 5 está com fome
[26.341s] Filósofo 1 terminou de comer.
[26.341s] Filósofo 1 soltou o garfo 1 (direito)
[26.342s] Filósofo 1 soltou o garfo 5 (esquerdo)
[26.343s] Filósofo 1 está pensando
[26.343s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[26.344s] Filósofo 2 pegou o garfo 1 (esquerdo)
[26.344s] Filósofo 2 tenta pegar o garfo 2 (direito)
[26.344s] Filósofo 2 pegou o garfo 2 (direito)
[26.344s] Filósofo 2 está comendo
[26.507s] Filósofo 2 terminou de comer.
[26.507s] Filósofo 2 soltou o garfo 2 (direito)
[26.508s] Filósofo 2 soltou o garfo 1 (esquerdo)
[26.508s] Filósofo 2 está pensando
[26.508s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[26.508s] Filósofo 3 pegou o garfo 2 (esquerdo)
[26.508s] Filósofo 3 tenta pegar o garfo 3 (direito)
[26.508s] Filósofo 3 pegou o garfo 3 (direito)
[26.508s] Filósofo 3 está comendo
[26.546s] Filósofo 4 está com fome
[26.550s] Filósofo 1 está com fome
[26.611s] Filósofo 3 terminou de comer.
[26.611s] Filósofo 3 soltou o garfo 3 (direito)
[26.611s] Filósofo 3 soltou o garfo 2 (esquerdo)
[26.611s] Filósofo 3 está pensando
[26.612s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[26.612s] Filósofo 5 pegou o garfo 4 (esquerdo)
[26.612s] Filósofo 5 tenta pegar o garfo 5 (direito)
[26.612s] Filósofo 5 pegou o garfo 5 (direito)
[26.612s] Filósofo 5 está comendo
[26.621s] Filósofo 2 está com fome
[26.840s] Filósofo 5 terminou de comer.
[26.841s] Filósofo 5 soltou o garfo 5 (direito)
[26.841s] Filósofo 5 soltou o garfo 4 (esquerdo)
[26.841s] Filósofo 5 está pensando
[26.841s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[26.841s] Filósofo 4 pegou o garfo 3 (esquerdo)
[26.841s] Filósofo 4 tenta pegar o garfo 4 (direito)
[26.841s] Filósofo 4 pegou o garfo 4 (direito)
[26.842s] Filósofo 4 está comendo
[27.001s] Filósofo 3 está com fome
[27.035s] Filósofo 5 está com fome
[27.121s] Filósofo 4 terminou de comer.
[27.122s] Filósofo 4 soltou o garfo 4 (direito)
[27.122s] Filósofo 4 soltou o garfo 3 (esquerdo)
[27.122s] Filósofo 4 está pensando
[27.122s] Filósofo 1 tenta pegar o garfo 1 (direito)
[27.122s] Filósofo 1 pegou o garfo 1 (direito)
[27.123s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[27.123s] Filósofo 1 pegou o garfo 5 (esquerdo)
[27.123s] Filósofo 1 está comendo
[27.318s] Filósofo 1 terminou de comer.
[27.319s] Filósofo 1 soltou o garfo 1 (direito)
[27.319s] Filósofo 1 soltou o garfo 5 (esquerdo)
[27.319s] Filósofo 1 está pensando
[27.319s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[27.319s] Filósofo 2 pegou o garfo 1 (esquerdo)
[27.320s] Filósofo 2 tenta pegar o garfo 2 (direito)
[27.320s] Filósofo 2 pegou o garfo 2 (direito)
[27.320s] Filósofo 2 está comendo
[27.466s] Filósofo 2 terminou de comer.
[27.467s] Filósofo 2 soltou o garfo 2 (direito)
[27.467s] Filósofo 2 soltou o garfo 1 (esquerdo)
[27.467s] Filósofo 2 está pensando
[27.467s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[27.467s] Filósofo 3 pegou o garfo 2 (esquerdo)
[27.468s] Filósofo 3 tenta pegar o garfo 3 (direito)
[27.468s] Filósofo 3 pegou o garfo 3 (direito)
[27.468s] Filósofo 3 está comendo
[27.483s] Filósofo 4 está com fome
[27.494s] Filósofo 1 está com fome
[27.601s] Filósofo 2 está com fome
[27.701s] Filósofo 3 terminou de comer.
[27.701s] Filósofo 3 soltou o garfo 3 (direito)
[27.701s] Filósofo 3 soltou o garfo 2 (esquerdo)
[27.702s] Filósofo 3 está pensando
[27.702s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[27.703s] Filósofo 5 pegou o garfo 4 (esquerdo)
[27.704s] Filósofo 5 tenta pegar o garfo 5 (direito)
[27.704s] Filósofo 5 pegou o garfo 5 (direito)
[27.704s] Filósofo 5 está comendo
[27.983s] Filósofo 3 está com fome
[27.985s] Filósofo 5 terminou de comer.
[27.985s] Filósofo 5 soltou o garfo 5 (direito)
[27.986s] Filósofo 5 soltou o garfo 4 (esquerdo)
[27.986s] Filósofo 5 está pensando
[27.986s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[27.987s] Filósofo 4 pegou o garfo 3 (esquerdo)
[27.987s] Filósofo 4 tenta pegar o garfo 4 (direito)
[27.987s] Filósofo 4 pegou o garfo 4 (direito)
[27.988s] Filósofo 4 está comendo
[28.194s] Filósofo 4 terminou de comer.
[28.195s] Filósofo 4 soltou o garfo 4 (direito)
[28.195s] Filósofo 4 soltou o garfo 3 (esquerdo)
[28.195s] Filósofo 4 está pensando
[28.195s] Filósofo 1 tenta pegar o garfo 1 (direito)
[28.195s] Filósofo 1 pegou o garfo 1 (direito)
[28.195s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[28.196s] Filósofo 1 pegou o garfo 5 (esquerdo)
[28.196s] Filósofo 1 está comendo
[28.364s] Filósofo 5 está com fome
[28.496s] Filósofo 1 terminou de comer.
[28.496s] Filósofo 1 soltou o garfo 1 (direito)
[28.496s] Filósofo 1 soltou o garfo 5 (esquerdo)
[28.497s] Filósofo 1 está pensando
[28.497s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[28.497s] Filósofo 2 pegou o garfo 1 (esquerdo)
[28.497s] Filósofo 2 tenta pegar o garfo 2 (direito)
[28.497s] Filósofo 2 pegou o garfo 2 (direito)
[28.498s] Filósofo 2 está comendo
[28.530s] Filósofo 4 está com fome
[28.660s] Filósofo 2 terminou de comer.
[28.660s] Filósofo 2 soltou o garfo 2 (direito)
[28.660s] Filósofo 2 soltou o garfo 1 (esquerdo)
[28.661s] Filósofo 2 está pensando
[28.661s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[28.661s] Filósofo 3 pegou o garfo 2 (esquerdo)
[28.661s] Filósofo 3 tenta pegar o garfo 3 (direito)
[28.662s] Filósofo 3 pegou o garfo 3 (direito)
[28.662s] Filósofo 3 está comendo
[28.850s] Filósofo 1 está com fome
[28.852s] Filósofo 3 terminou de comer.
[28.853s] Filósofo 3 soltou o garfo 3 (direito)
[28.853s] Filósofo 3 soltou o garfo 2 (esquerdo)
[28.853s] Filósofo 3 está pensando
[28.854s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[28.854s] Filósofo 5 pegou o garfo 4 (esquerdo)
[28.855s] Filósofo 5 tenta pegar o garfo 5 (direito)
[28.855s] Filósofo 5 pegou o garfo 5 (direito)
[28.856s] Filósofo 5 está comendo
[29.001s] Filósofo 3 está com fome
[29.083s] Filósofo 5 terminou de comer.
[29.084s] Filósofo 5 soltou o garfo 5 (direito)
[29.084s] Filósofo 5 soltou o garfo 4 (esquerdo)
[29.084s] Filósofo 5 está pensando
[29.085s] Filósofo 4 tenta pegar o garfo 3 (esquerdo)
[29.085s] Filósofo 4 pegou o garfo 3 (esquerdo)
[29.085s] Filósofo 4 tenta pegar o garfo 4 (direito)
[29.086s] Filósofo 4 pegou o garfo 4 (direito)
[29.086s] Filósofo 4 está comendo
[29.112s] Filósofo 2 está com fome
[29.332s] Filósofo 4 terminou de comer.
[29.333s] Filósofo 4 soltou o garfo 4 (direito)
[29.333s] Filósofo 4 soltou o garfo 3 (esquerdo)
[29.333s] Filósofo 4 está pensando
[29.333s] Filósofo 1 tenta pegar o garfo 1 (direito)
[29.334s] Filósofo 1 pegou o garfo 1 (direito)
[29.334s] Filósofo 1 tenta pegar o garfo 5 (esquerdo)
[29.334s] Filósofo 1 pegou o garfo 5 (esquerdo)
[29.334s] Filósofo 1 está comendo
[29.456s] Filósofo 5 está com fome
[29.534s] Filósofo 4 está com fome
[29.542s] Filósofo 1 terminou de comer.
[29.542s] Filósofo 1 soltou o garfo 1 (direito)
[29.543s] Filósofo 1 soltou o garfo 5 (esquerdo)
[29.543s] Filósofo 1 está pensando
[29.543s] Filósofo 3 tenta pegar o garfo 2 (esquerdo)
[29.543s] Filósofo 3 pegou o garfo 2 (esquerdo)
[29.544s] Filósofo 3 tenta pegar o garfo 3 (direito)
[29.544s] Filósofo 3 pegou o garfo 3 (direito)
[29.544s] Filósofo 3 está comendo
[29.684s] Filósofo 3 terminou de comer.
[29.684s] Filósofo 3 soltou o garfo 3 (direito)
[29.684s] Filósofo 3 soltou o garfo 2 (esquerdo)
[29.685s] Filósofo 3 está pensando
[29.686s] Filósofo 2 tenta pegar o garfo 1 (esquerdo)
[29.686s] Filósofo 2 pegou o garfo 1 (esquerdo)
[29.686s] Filósofo 2 tenta pegar o garfo 2 (direito)
[29.687s] Filósofo 2 pegou o garfo 2 (direito)
[29.687s] Filósofo 2 está comendo
[29.799s] Filósofo 1 está com fome
[29.952s] Filósofo 2 terminou de comer.
[29.952s] Filósofo 2 soltou o garfo 2 (direito)
[29.952s] Filósofo 2 soltou o garfo 1 (esquerdo)
[29.953s] Filósofo 2 está pensando
[29.953s] Filósofo 5 tenta pegar o garfo 4 (esquerdo)
[29.953s] Filósofo 5 pegou o garfo 4 (esquerdo)
[29.953s] Filósofo 5 tenta pegar o garfo 5 (direito)
[29.954s] Filósofo 5 pegou o garfo 5 (direito)
[29.954s] Filósofo 5 está comendo

Nenhum deadlock no período de 30 segundos
```
</details>

## PARTE 2 - Threads e semáforos

### Como funciona
O programa usa um semáforo que controla os recursos adquirindo e liberando, isso resolve o problema de sobrescrita, onde muitas threads tentam modificar a mesma variável, fazendo com que alguns resultados das threads sejam perdidos.
Usando o semáforo com (with) para adquirir ele deixa só 1 thread modificara por vez e liberando para a próxima, evitando o problema da sobrescrita ao custo de mais tempo pois na área crítica (with) se torna sequencial.

### GIL
O python por ser uma linguagem interpretada ele executa as instruções sequenciais, o GIL (Global Interpreter Lock) impede a execução paralela. Em operações rápidas como no contador do sem semáforo e com semáforo acabam sendo iguais, o sem semáforo acaba não tendo perdas. Para poder ver essa diferença adicionamos uma pausa (time.sleep) para CPU poder passar para a outra thread e poder ver essa sobrescrita.

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
sem = Semaforo(1)
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


Como podemos ver que a versão sem semáforo acabou obtendo menos do que esperado porem em um tempo mais curto, já o com semáforo o obtido é o mesmo que esperado ou seja sem perdas porem em um tempo de execução muito maior.

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
