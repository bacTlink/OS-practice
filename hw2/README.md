1.用自己的语言描述Mesos的组成结构，指出它们在源码中的具体位置，简单描述一下它们的工作流程
----

### 架构

![architecture](https://raw.githubusercontent.com/bacTlink/OS-practice/master/hw2/architecture.png)

如上图所示，Mesos的架构有ZooKeeper、Mesos Master、Standby Master、Mesos slaves以及Framework。
其中ZooKeeper与Standby Master不是必须的。
MPI和Hadoop是两个Framework的例子。Task通过Framework来运行。
Master调配资源，Slave运行Master分配给它的Task，如上图所示一个Slave也可以运行两个Tasks。

- Master负责管理Slave在每个节点上的运行，
根据指定的策略决定提供多少的资源给Framework。

- Slave(Agent)定期向Master汇报拥有的资源，然后根据Master的调配执行对应的命令，
以及管理分配给自己的任务。

- Framework包括scheduler和executor两部分。
scheduler注册到Master以获取集群资源，并在获取资源后，选择其中提供的一些资源，然后将tasks发送到slave上进行运行。
executor运行在slave上，负责执行framework的tasks。

- Standby Master是备用的Master。Master的设计是soft state的，可以通过从slave和framework获得的消息完全恢复状态并工作。当原有的Master发生错误时，为了保证运行在其上的framework可以继续工作，需要一个新的Master。

- ZooKeeper在重新选举一个Master起作用。另外，当Agent检测Master时，如果指定了ZooKeeper，则会使用ZooKeeper做Master的检测，不然则使用StandaloneMasterDetector。

### 代码位置

- Master：mesos-1.1.0/src/master
- Slave(Agent)：mesos-1.1.0/src/slave
- ZooKeeper：mesos-1.1.0/src/zookeeper

### 工作流程

![resource](https://raw.githubusercontent.com/bacTlink/OS-practice/master/hw2/Resource.png)

上图是运行的一个示例。
上图的事件流程:[(参考资料)](https://mesos-cn.gitbooks.io/mesos-cn/content/OverView/Mesos-Architecture.html)

- Slave1 向 Master 报告，有4个CPU和4 GB内存可用

- Master 发送一个 Resource Offer 给 Framework1 来描述 Slave1 有多少可用资源

- FrameWork1 中的 FW Scheduler会答复 Master，我有两个 Task 需要运行在 Slave1，一个 Task 需要<2个cpu，1 gb内存="">，另外一个Task需要<1个cpu，2 gb内存="">

- 最后，Master 发送这些 Tasks 给 Slave1。然后，Slave1还有1个CPU和1 GB内存没有使用，所以分配模块可以把这些资源提供给 Framework2

抽象一下，就是

- Slave定期向Master报告自身可用的资源。

- Master发送可用资源给Framework，让Framework进行调配。

- Framework答复Master具体在哪个Slave上运行什么Task，Task需要多少资源。

- Master将Tasks发送给Slaves，然后Slaves运行Task，报告可用资源给Master。

#### 更详细的工作流程：[(参考资料)](http://www.cnblogs.com/popsuper1982/p/5930827.html)

![pig](http://images2015.cnblogs.com/blog/635909/201610/635909-20161004174842567-1059543870.png)


2.用自己的语言描述框架（如Spark On Mesos）在Mesos上的运行过程，并与在传统操作系统上运行程序进行对比
---

### 以Spark为例。

![SparkWroks](http://spark.apache.org/docs/latest/img/cluster-overview.png)

上图为Spark运行时的框架。
mesos作为Spark的Cluster Manager，运行流程为：
- Spark启动，作为Framework向Master注册
- 用户向Driver Program提交Tasks
- Mesos调度Worker Node(Slave)运行Tasks
- Slave从Spark处获取SparkContext以运行Tasks

### 与传统操作系统进行对比
- 开始运行申请资源时，传统操作系统中，程序是申请资源，然后操作系统返回结果。而在Mesos上时，则是Mesos提供可用资源，程序再进行申请，Mesos再返回结果。
- 运行时，都对程序提供了资源的抽象，包括CPU、内存、GPU等等。
- 最大的不同是一个运行在单机，另一个运行在集群上。运行在传统操作系统上的程序不需要进行通信。

3.叙述master和slave的初始化过程
---

### Master

Master的入口是mesos-1.1.0/src/master/main.cpp
```
开一个master::Flags记录flags。
flags用到了stout库，主要是其中的option和flag。
flags涉及到了LIBPROCESS_IP等环境变量。
进行libprocess库的process的初始化。
进行日志logging的初始化。
将warning写入日志中。
新建一个VersionProcess线程用于返回http请求的版本号。
初始化防火墙。
初始化模块。
初始化hooks（暂时不知道有什么作用）。
新建一个分配器的实例。
新建用于state的空间。
创建State实例。
创建Registrar实例。
创建MasterContender实例。
创建MasterDetector实例。
初始化Authorizer相关内容。
初始化SlaveRemovalLimiter相关内容。
创建master实例，创建master线程以监听请求。
等待master结束。
垃圾回收。
```
这里创建master线程，应该是进入了Master::initialize()。
然后就等待事件的发生，以进行相应。
这里的事件包括Slave注册，Framework注册，Framework执行任务等等。

### Slave
Slave的入口是mesos-1.1.0/src/slave/main.cpp

```
开一个slave::Flags进行flags的chuli。
向Master提供资源，每隔"disk_watch_interval"的时间就调用一次Slave::checkDiskUsage。
输出版本号。
利用libprocess生成一个slave的ID。
进行libprocess库的process的初始化。
进行日志logging的初始化。
将warning写入日志中。
新建一个VersionProcess线程用于返回http请求的版本号。
初始化防火墙。
初始化模块。
创建containerizer。
创建detector。
Authorizer管理。
创建gc、StatusUpdateManager、ResourceEstimator。
创建slave实例，创建slave线程。
等待slave结束。
垃圾回收。
```

创建slave线程后应该也是进入Slave::initialize()进行slave的初始化。

Master和Slave的initialize过程基本都是对flag进行处理，进行http请求的初始化工作。


4.查找资料，简述Mesos的资源调度算法，指出在源代码中的具体位置并阅读，说说你对它的看法
---
Mesos使用的是Dominant Resource Fairness算法(DRF)：[论文](https://github.com/bacTlink/OS-practice/raw/master/hw2/Ghodsi.pdf)

其目标是确保每一个用户，即Mesos中的Framework能够接收到其最需资源的公平份额。

首先定义主导资源(domainant resource)和主导份额。
主导资源为一个Framework的某个资源，Framework所需除以Master所有，大于其它所有资源。
Framework所需除以Master所有，即为这个Framework的主导份额。

DRF算法会解方程，尽量让每一个Framework的主导份额相等，除非某个Framework不需要那么多的资源。如果是带权重的DRF算法，只需将权重归一化再执行DRF算法即可。

它的核心算法伪代码：
![伪代码](https://github.com/bacTlink/OS-practice/raw/master/hw2/DRF.png)

它的代码应该是位于mesos-1.1.0/src/master/allocator/mesos/hierarchical.cpp中的HierarchicallAllocatorProcess::allocate()

### 看法
DRF算法在公平这一点上，有其合理之处，
即让每个Framework最稀缺的资源占有相同的份额。

翻看代码后发现DRF在mesos中的实现还考虑的很多很多的情况，
包括Slave掉线、Framework掉线等等情况。
实际工程比起理论上，
需要补足很多细节。

5.写一个完成简单工作的框架(语言自选，需要同时实现scheduler和executor)并在Mesos上运行，在报告中对源码进行说明并附上源码，本次作业分数50%在于本项的完成情况、创意与实用程度。（后面的参考资料一定要读，降低大量难度）
---

使用PyMesos项目来完成。

### 对PyMesos进行一个功能上的测试：

#### scheduler.py
```
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

    sum_res = 0
    nums = 200000000
    counts = 10
    finished = 0
    i = 0

    def __init__(self, executor):
        self.executor = executor

    def frameworkMessage(self, driver, executorId, slaveId, message):
        self.sum_res = self.sum_res + int(decode_data(message))
        self.finished = self.finished + 1
        if self.finished >= self.counts:
            print(self.sum_res)
            driver.stop()

    def resourceOffers(self, driver, offers):
        if self.i >= self.counts:
            return None
        filters = {'refuse_seconds': 5}

        for offer in offers:
            if self.i >= self.counts:
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
            task.data = encode_data(str(self.i * self.nums) + ' ' + str((self.i + 1) * self.nums))

            task.resources = [
                dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
                dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
            ]

            driver.launchTasks(offer.id, [task], filters)
            self.i = self.i + 1

    def getResource(self, res, name):
        for r in res:
            if r.name == name:
                return r.scalar.value
        return 0.0

    def statusUpdate(self, driver, update):
        logging.debug('Status update TID %s %s',
                      update.task_id.value,
                      update.state)

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
        MyScheduler(executor),
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
    if len(sys.argv) != 2:
        print("Usage: {} <mesos_master>".format(sys.argv[0]))
        sys.exit(1)
    else:
        main(sys.argv[1])
```

#### executor.py
```
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
```

其功能，是计算0到nums(=200000000) * counts(=10)的和。

下图是计算到一半时，资源的使用状况：
![资源](https://github.com/bacTlink/OS-practice/raw/master/hw2/test0.png)

代码正确地显示了结果。
![结果](https://github.com/bacTlink/OS-practice/raw/master/hw2/test0_res.png)

这里仅仅作为interface.py中提到的API的一个测试。

我翻看了PyMesos的底层代码，PyMesos与Mesos的HTTP connect应该是一直不断的，（除了对Version的请求），所以HTTP消息应该是按顺序处理的，应该不会发生重入冲突。

### 用PyMesos写洋葱法积分的代码

#### scheduler.py
```
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

	#每个Task的任务量是500000个小区间
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
		#计算完成
		if self.finished >= self.counts:
			print(self.sum_res)
			driver.stop()

	def resourceOffers(self, driver, offers):
		filters = {'refuse_seconds': 5}

		for offer in offers:
			#计算完了就不再用资源了
			if self.left >= self.right-1e-16:
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
			#启动任务时，告诉executor要执行的函数、区间、步长
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
```

#### executor.py
```
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
						
			#对提交的函数从left到right进行积分
			while x<right-1e-16:
				exec(fun) in globals(), locals()
				res_tot = res_tot + res
				x = x + step
			#发送计算的结果
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
```

- 执行命令：`python scheduler.py 162.105.30.12 "res=4*math.sqrt(1-x*x)" 0 1 1000000`
	意思是对![f](http://chart.googleapis.com/chart?cht=tx&chl=\Large%204\sqrt{1-x^2})在0~1区间内进行积分，将区间分成1000000份。

- 执行命令：`python scheduler.py 162.105.30.12 "res=1/x" 1 2 1000000`
	意思是对![f](http://chart.googleapis.com/chart?cht=tx&chl=\Large%20\frac{1}{x})在1~2区间内进行积分，将区间分成1000000份。

理论结果应该为π和ln2

结果：

![结果](https://github.com/bacTlink/OS-practice/raw/master/hw2/PI_ln2.png)

积分结果问题不大。

