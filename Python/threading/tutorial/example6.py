from ast import arguments
from asyncio import as_completed
from cgi import print_exception
import time 
import multiprocessing
import concurrent.futures

start = time.perf_counter()

# functions
def do_something(seconds):
    print(f'sleeping {seconds} second')
    time.sleep(1)
    return f'Done sleeping for {seconds}'

with concurrent.futures.ProcessPoolExecutor() as executor:
    secs = [5,4,3,2,1]
    results = [executor.submit(do_something,sec) for sec in secs]

    for result in concurrent.futures.as_completed(results):
        print(result.result())

finish = time.perf_counter()
print(f'Finished in {round(finish-start, 2 )} second(s)')