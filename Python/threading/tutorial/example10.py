from multiprocessing import  Pool
from multiprocessing import Queue
import numbers
import time 
import os


def cube(number):
    return number * number * number

start = time.perf_counter()

if __name__ == "__main__":
    pool = Pool()
    numbers = range(10)

    result = pool.map(cube, numbers)

    pool.close()
    pool.join()

    print(result)
    finish = time.perf_counter()
    print(f'Finished in {round(finish-start, 2 )} second(s)')



