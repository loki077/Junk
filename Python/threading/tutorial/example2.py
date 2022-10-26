import time 
import threading

start = time.perf_counter()

# functions
def do_something(seconds):
    print(f'sleeping {seconds} second(s)')
    time.sleep(seconds)
    print('Done sleeping')


#init thread list
threads = []

for _ in range(10):
    t = threading.Thread(target=do_something, args=[1.5])
    t.start()
    threads.append(t)

for thread in threads:
    thread.join()

finish = time.perf_counter()
print(f'Finished in {round(finish-start, 2 )} second(s)')