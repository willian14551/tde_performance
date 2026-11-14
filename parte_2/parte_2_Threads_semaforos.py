import threading
import time

T = 8     
M = 200000
contador = 0

sem = semaforo = threading.Semaphore(1)

def tarefa_com_semaforo():
    global contador
    
    for i in range(M):
        with sem:
            temp = contador
            time.sleep(0)
            contador = temp + 1

       
def tarefa_sem_semaforo():
    global contador

    for i in range(M):
        temp = contador
        time.sleep(0)
        contador = temp + 1


def imprimir(tipo,começo, final, vezes, contador):

    if tipo == "sem":
        tipo = "sem semaforo"
    else:
        tipo = "com semaforo"
    print(tipo, " | " , vezes + 1 , " | ",  T*M , " | ", contador," | ", (final - começo))



print("| Versão | Execução | Esperado | Obtido | Tempo(s) | ")
print("|---|---|---|---|---|")
for i in range(3):
    inicio = time.perf_counter()

    contador = 0
    threads = []

    for t in range(T):
        t = threading.Thread(target=tarefa_sem_semaforo)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    final = time.perf_counter()
    imprimir("sem", inicio, final, i, contador)



for i in range(3):
    inicio = time.perf_counter() 

    contador = 0
    threads = []

    for t in range(T):
        t = threading.Thread(target=tarefa_com_semaforo)
        threads.append(t) 
        t.start() 
    
    for t in threads:
        t.join()

    final = time.perf_counter() 
    imprimir("com" , inicio, final, i, contador)
