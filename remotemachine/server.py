import sys,os,Queue
from multiprocessing import Process,freeze_support
from multiprocessing.managers import BaseManager

class QueueManager(BaseManager):
        pass

task_queue = Queue.Queue()
result_queue = Queue.Queue()

if __name__ == '__main__':
    freeze_support()
    QueueManager.register('get_task_queue', callable=lambda:task_queue)
    QueueManager.register('get_result_queue', callable=lambda:result_queue)
    qmm = QueueManager(address=('127.0.0.1', 5000), authkey='abc')
    qmm.get_server().serve_forever()
