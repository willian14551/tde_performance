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


def imprimir(começo, final, vezes, contador):
    print(vezes + 1 , " tentativa")
    print("esperado = ", T*M , " Obtido = ", contador," tempo = ", (final - começo))
    print() 


print("==== sem semaforo====")
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
    imprimir(inicio, final, i, contador)


print("==== com semaforo====")
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
    imprimir(inicio, final, i, contador)
