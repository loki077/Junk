from multiprocessing import Process, Queue, Value, Array, Lock
from multiprocessing import Queue
import time 
import os

#square root example
def square_numbers():
    for i in range(1000):
        i*i
    return i

#add data with share value and array with lock
def add_100(number,array, lock):
    for i in range(100):
        time.sleep(0.01)
        with lock:
            number.value +=1
            for i in range (len(array)):
                array[i] +=1
        # lock.acquire()
        # number.value +=1
        # lock.release()


start = time.perf_counter()

if __name__ == "__main__":
    lock = Lock()
    share_number = Value('i', 0)
    share_array = Array('d', [0.0, 100.0, 200.0, 300.0])
    print("Share Number is ", share_number.value)
    print("Array Number is ", share_array[:])

    processes = []
    num_processor = os.cpu_count()
    print(num_processor)

    for i in range(num_processor):
        process = Process(target= add_100, args=(share_number,share_array, lock))
        processes.append(process)
    
    for process in processes:
        process.start()

    for process in processes:
        process.join()
    
    print("Share Number is ", share_number.value)
    print("Array Number is ", share_array[:])

    finish = time.perf_counter()
    print(f'Finished in {round(finish-start, 2 )} second(s)')



