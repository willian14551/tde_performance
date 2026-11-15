import random
import threading
import time

NUM_FILOSOFOS = 5
PAUSA_ENTRE_GARFOS = 0.5
TEMPO_MAXIMO = 30

TEMPO_PENSAR_MIN = 0.1
TEMPO_PENSAR_MAX = 0.5
TEMPO_COMER_MIN = 0.1
TEMPO_COMER_MAX = 0.3

garfos = {numero: threading.Lock() for numero in range(1, NUM_FILOSOFOS + 1)}
estados = {numero: "pensando" for numero in range(1, NUM_FILOSOFOS + 1)}
trava_saida = threading.Lock()
inicio = time.time()

def registrar(mensagem):
    with trava_saida:
        print(f"[{time.time() - inicio:.3f}s] {mensagem}")

def mudar_estado(numero, estado):
    estados[numero] = estado
    registrar(f"Filósofo {numero} está {estado}")

def pegar_garfo(numero, garfo):
    if garfo == numero:
        lado = "direito"
    else:
        lado = "esquerdo"
    registrar(f"Filósofo {numero} tenta pegar o garfo {garfo} ({lado})")
    if garfos[garfo].acquire(False):
        registrar(f"Filósofo {numero} pegou o garfo {garfo} ({lado})")
        return True
    else:
        registrar(f"Filósofo {numero} não consegue o garfo {garfo} ({lado})")
        return False

def soltar_garfo(numero, garfo):
    if garfo == numero:
        lado = "direito"
    else:
        lado = "esquerdo"
    garfos[garfo].release()
    registrar(f"Filósofo {numero} soltou o garfo {garfo} ({lado})")

def filosofo(numero):
    direito = numero
    esquerdo = numero - 1 if numero > 1 else NUM_FILOSOFOS
    menor = min(direito, esquerdo)
    maior = max(direito, esquerdo)

    while True:
        mudar_estado(numero, "pensando")
        time.sleep(random.uniform(TEMPO_PENSAR_MIN, TEMPO_PENSAR_MAX))

        mudar_estado(numero, "com fome")
        pegar_primeiro_garfo = pegar_garfo(numero, menor)
        if pegar_primeiro_garfo:
            time.sleep(PAUSA_ENTRE_GARFOS)
            pegar_segundo_garfo = pegar_garfo(numero, maior)
            if pegar_segundo_garfo:
                mudar_estado(numero, "comendo")
                time.sleep(random.uniform(TEMPO_COMER_MIN, TEMPO_COMER_MAX))
                registrar(f"Filósofo {numero} terminou de comer.")
                soltar_garfo(numero, direito)
                soltar_garfo(numero, esquerdo)
            else:
                soltar_garfo(numero, menor)
                espera = 0.2
                registrar(f"Filósofo {numero} não consegue os 2 garfos, espera {espera}s para tentar novamente.")
                time.sleep(espera)
        else:
            espera = 0.2
            registrar(f"Filósofo {numero} espera {espera}s para tentar novamente.")
            time.sleep(espera)

def todos_com_fome():
    return all(estado == "com fome" for estado in estados.values())

def main():
    for numero in range(1, NUM_FILOSOFOS + 1):
        threading.Thread(target=filosofo, args=(numero,), daemon=True).start()

    segundos = 0
    while segundos < TEMPO_MAXIMO:
        time.sleep(1)
        segundos += 1
        if todos_com_fome():
            time.sleep(3)
            if todos_com_fome():
                print("Deadlock! Todos os filósofos continuam com fome há mais de 3 segundos e ninguém consegue comer")
                return

    print()
    print(f"Nenhum deadlock no período de {TEMPO_MAXIMO} segundos")

main()