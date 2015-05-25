import os,sys,Queue,time
from multiprocessing import Process
from multiprocessing.managers import BaseManager

class QueueManager(BaseManager):
    pass

QueueManager.register('get_task_queue')
QueueManager.register('get_result_queue')
m = QueueManager(address=('127.0.0.1', 5000), authkey='abc')
m.connect()
task = m.get_task_queue()
result = m.get_result_queue()

for k in range(10):
    try:
        n = task.get(timeout=4)
        print "get " + str(n)
        time.sleep(2)
        result.put(n+100)
    except Queue.Empty:
        print "exception: empty queue"
print "worker quit" 
