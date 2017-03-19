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

更详细的工作流程：[(参考资料)](http://www.cnblogs.com/popsuper1982/p/5930827.html)
![pig](http://images2015.cnblogs.com/blog/635909/201610/635909-20161004174842567-1059543870.png)


2.用自己的语言描述框架（如Spark On Mesos）在Mesos上的运行过程，并与在传统操作系统上运行程序进行对比
---

### 以Spark为例。

3.叙述master和slave的初始化过程
---

向Master提供资源，每隔"disk_watch_interval"的时间就调用一次Slave::checkDiskUsage
4.查找资料，简述Mesos的资源调度算法，指出在源代码中的具体位置并阅读，说说你对它的看法
---

5.写一个完成简单工作的框架(语言自选，需要同时实现scheduler和executor)并在Mesos上运行，在报告中对源码进行说明并附上源码，本次作业分数50%在于本项的完成情况、创意与实用程度。（后面的参考资料一定要读，降低大量难度）
---