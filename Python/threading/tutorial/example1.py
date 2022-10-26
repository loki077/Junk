import time 
import threading

start = time.perf_counter()

# functions
def do_something():
    print('sleeping 1 second')
    time.sleep(1)
    print('Done sleeping')

#init thread
thr_1 = threading.Thread(target=do_something)
thr_2 = threading.Thread(target=do_something)

# start thread
thr_1.start()
thr_2.start()

# wait for the threads to end
thr_1.join()
thr_2.join()


finish = time.perf_counter()
print(f'Finished in {round(finish-start, 2 )} second(s)')