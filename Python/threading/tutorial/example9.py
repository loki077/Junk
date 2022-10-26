from multiprocessing import Process, Queue, Value, Array, Lock, Pool
from multiprocessing import Queue
import numbers
import time 
import os

#square root example
def square_numbers(numbers, queue):
    for i in numbers:
        queue.put(i*i)

#square root example
def make_negative(numbers, queue):
    for i in numbers:
        queue.put(-1*i)

start = time.perf_counter()

if __name__ == "__main__":
    numbers = range(1,6)
    q = Queue()

    p1 = Process(target=square_numbers, args=[numbers, q])
    p2 = Process(target=make_negative, args=[numbers, q])

    p1.start()
    p2.start()
    
    p1.join()
    p2.join()

    while not q.empty():
        print(q.get())

    finish = time.perf_counter()
    print(f'Finished in {round(finish-start, 2 )} second(s)')



