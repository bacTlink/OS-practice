#!/usr/bin/env python2.7
from __future__ import print_function

import sys
import uuid
import time
import socket
import signal
import getpass
from threading import Thread
from os.path import abspath, join, dirname

from pymesos import MesosSchedulerDriver, Scheduler, encode_data, decode_data
from addict import Dict

TASK_CPU = 1
TASK_MEM = 32
EXECUTOR_CPUS = 0.5
EXECUTOR_MEM = 32


class MyScheduler(Scheduler):

	taskN = 500000

	def __init__(self, executor, fun, left, right, division):
		self.executor = executor
		self.fun = fun
		self.left = float(left)
		self.right = float(right)
		self.division = int(division)
		self.step = (self.right - self.left) / self.division
		self.sum_res = 0
		self.counts = ((self.division - 1) // self.taskN) + 1
		self.finished = 0

	def frameworkMessage(self, driver, executorId, slaveId, message):
		self.sum_res = self.sum_res + float(decode_data(message))
		self.finished = self.finished + 1
		if self.finished >= self.counts:
			print(self.sum_res)
			driver.stop()

	def resourceOffers(self, driver, offers):
		filters = {'refuse_seconds': 5}

		for offer in offers:
			if self.left >= self.right:
				break
			cpus = self.getResource(offer.resources, 'cpus')
			mem = self.getResource(offer.resources, 'mem')
			if cpus < TASK_CPU or mem < TASK_MEM:
				continue

			task = Dict()
			task_id = str(uuid.uuid4())
			task.task_id.value = task_id
			task.agent_id.value = offer.agent_id.value
			task.name = 'task {}'.format(task_id)
			task.executor = self.executor
			task.data = encode_data(self.fun + '!' \
					+ repr(self.left) + '!' \
					+ repr(min(self.right, self.left + self.step * self.taskN)) + '!' \
					+ repr(self.step))

			task.resources = [
				dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
				dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
			]

			driver.launchTasks(offer.id, [task], filters)
			self.left = self.left + self.step * self.taskN

	def getResource(self, res, name):
		for r in res:
			if r.name == name:
				return r.scalar.value
		return 0.0

	def statusUpdate(self, driver, update):
		logging.debug('Status update TID %s %s',
					  update.task_id.value,
					  update.state)

def printUsage():
	print("Usage: python scheduler.py <mesos_master> res=function start stop division")
	print("    function is an expression with variable x")
	print("        You can use temperory variable")
	print("        for example: \'y * y\\nres=y\'")
	print("    start is float")
	print("    stop is float")
	print("    division is int")

def main(master):

	executor = Dict()
	executor.executor_id.value = 'MyExecutor'
	executor.name = executor.executor_id.value
	executor.command.value = '%s %s' % (
		sys.executable,
		abspath(join(dirname(__file__), 'executor.py'))
	)
	executor.resources = [
		dict(name='mem', type='SCALAR', scalar={'value': EXECUTOR_MEM}),
		dict(name='cpus', type='SCALAR', scalar={'value': EXECUTOR_CPUS}),
	]

	framework = Dict()
	framework.user = getpass.getuser()
	framework.name = "MyFramework"
	framework.hostname = socket.gethostname()

	driver = MesosSchedulerDriver(
		MyScheduler(executor, sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]),
		framework,
		master,
		use_addict=True,
	)

	def signal_handler(signal, frame):
		driver.stop()

	def run_driver_thread():
		driver.run()

	driver_thread = Thread(target=run_driver_thread, args=())
	driver_thread.start()

	print('Scheduler running, Ctrl+C to quit.')
	signal.signal(signal.SIGINT, signal_handler)

	while driver_thread.is_alive():
		time.sleep(1)


if __name__ == '__main__':
	import logging
	logging.basicConfig(level=logging.DEBUG)
	if len(sys.argv) != 6:
		printUsage()
		sys.exit(1)
	else:
		main(sys.argv[1])
