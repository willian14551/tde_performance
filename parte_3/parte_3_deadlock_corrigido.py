import threading
import time
 
LOCK_A = threading.Lock()
LOCK_B = threading.Lock()
 
 
def thread1():
    LOCK_A.acquire()
    print("Thread 1 pegou A")
    time.sleep(0.05)
    LOCK_B.acquire()
    print("Thread 1 concluiu")
    LOCK_B.release()
    LOCK_A.release()
 
 
def thread2():
    LOCK_A.acquire()
    print("Thread 2 pegou A")
    time.sleep(0.05)
    LOCK_B.acquire()
    print("Thread 2 concluiu")
    LOCK_B.release()
    LOCK_A.release()
 
 
threading.Thread(target=thread1).start()
threading.Thread(target=thread2).start()