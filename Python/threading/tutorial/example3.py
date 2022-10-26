from asyncio import as_completed
import time 
import concurrent.futures

start = time.perf_counter()

# functions
def do_something(seconds):
    print(f'sleeping {seconds} second(s)')
    time.sleep(seconds)
    return f'Done sleeping for {seconds} second(s)'

# setting up a future objects in threading
with concurrent.futures.ThreadPoolExecutor() as executor:
    secs = [5,4,3,2,1]

    # submit method, using list comprehensive instead of for loop
    # results = [executor.submit(do_something, sec) for sec in secs]
    # for f in concurrent.futures.as_completed(results):
    #     print(f.result())

    #map method
    results = executor.map(do_something, secs)
    for result in results:
        print(result)

finish = time.perf_counter()
print(f'Finished in {round(finish-start, 2 )} second(s)')