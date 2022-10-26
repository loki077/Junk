import multiprocessing
from multiprocessing import Process, Queue
import time


class Tool(Process):
    def __init__(self, queue, components) -> None:
        super().__init__()
        Process.__init__(self)
        self.queue = queue
        self.components = components

    def process_components(self, components):
        for i in range(len(components)):
            components[i] = 1
        return components

    def run(self):
        processed_component = self.process_components(self.components)
        print("Tool is processing")
        self.queue.put(processed_component)


start = time.perf_counter()


if __name__ == "__main__":
    tools = []
    queue = Queue()
    components_to_process = 4

    for _ in range (components_to_process):
        raw_components = [0] * 10000000
        tools.append(Tool(queue, raw_components))

    for tool in tools:
        tool.start()
    
    while components_to_process > 0:
        processed_tools = queue.get()
        print("Compoent Process = ", processed_tools[59])
        components_to_process -= 1    

finish = time.perf_counter()
print(f'Finished in {round(finish-start, 2 )} second(s)')