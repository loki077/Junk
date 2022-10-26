from ast import arguments
import time 
import multiprocessing

start = time.perf_counter()

# functions
def do_something(seconds):
    print(f'sleeping {seconds} second')
    time.sleep(1)
    print(f'Done sleeping for {seconds}')

#setup multiprocess
p1 = multiprocessing.Process(target=do_something, args= [1.5])
p2 = multiprocessing.Process(target=do_something, args= [1.5])

#start process
p1.start()
p2.start()

#wait for process to end
p1.join()
p2.join()

finish = time.perf_counter()
print(f'Finished in {round(finish-start, 2 )} second(s)')