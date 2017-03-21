#!/usr/bin/env python2.7
from __future__ import print_function

import sys
import time
import math
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

			tmp = decode_data(task.data).split('!')
			fun = tmp[0];
			left = float(tmp[1])
			right = float(tmp[2])
			step = float(tmp[3])
			res_tot = 0
			x = left
			while x<right-1e-16:
				exec(fun) in globals(), locals()
				res_tot = res_tot + res
				x = x + step
			driver.sendFrameworkMessage(encode_data(repr(step * res_tot)))

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
