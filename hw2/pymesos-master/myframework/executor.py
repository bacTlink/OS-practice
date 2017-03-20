#!/usr/bin/env python2.7
from __future__ import print_function

import sys
import time
from threading import Thread

from pymesos import MesosExecutorDriver, Executor, decode_data, encode_data
from addict import Dict


class MyExecutor(Executor):
    def launchTask(self, driver, task):
        def run_task(task):
            update = Dict()
            update.task_id.value = task.task_id.value
            update.state = 'TASK_RUNNING'
            update.timestamp = time.time()
            driver.sendStatusUpdate(update)

            tmp = decode_data(task.data).split(' ')
            left = int(tmp[0])
            right = int(tmp[1])
            res = 0
            for i in xrange(left, right):
                res = res + i
            driver.sendFrameworkMessage(encode_data(str(res)))

            update = Dict()
            update.task_id.value = task.task_id.value
            update.state = 'TASK_FINISHED'
            update.timestamp = time.time()
            driver.sendStatusUpdate(update)

        thread = Thread(target=run_task, args=(task,))
        thread.start()


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    driver = MesosExecutorDriver(MyExecutor(), use_addict=True)
    driver.run()
