#第一次作业

[TOC]

-------

##1.mesos论文
[论文](https://github.com/bacTlink/OS-practice/blob/master/%E7%AC%AC1%E6%AC%A1%E4%BD%9C%E4%B8%9A/Mesos%20A%20Platform%20for%20Fine-Grained%20Resource%20Sharing%20in%20the%20Data%20Center.pdf)

---

##2.虚拟机和容器技术

虚拟机对硬件进行仿真，可在其上搭建一个有效的、独立的真实机器的副本，可以安装任何操作系统，可以和任何实际机器无关。
用户在虚拟机上运行一个完整操作系统，在该系统上再运行所需应用进程。

容器是一种云技术，它的运行环境是一层一层镜像的叠加，它的实质是一个独立进程，容器内的应用进程直接运行于宿主的内核，容器内没有自己的内核，而且也没有进行硬件虚拟。

虚拟机较为笨重，容器是轻量级的。
虚拟机和容器都有对资源进行控制，并且相互之间具有隔离性。
由于容器没有自己的内核，容器启动、删除、备份等都相当迅速，代价较低，因此构建、重组也十分方便。
由于容器是镜像的叠加，对容器容易实现版本的控制。

---

##3. mesos-1.1.0, build, 运行

下载mesos-1.1.0。
我是直接用release版本。
github上的1.1.0的release版本和tag1.1.0的版本的代码大概是一样的，make check <font color="red">FAILED</font>的都完全一样。

下载后解压，然后
```
# Change working directory.
$ cd mesos

# Bootstrap (Only required if building from git repository).
$ ./bootstrap

# Configure and build.
$ mkdir build
$ cd build
$ ../configure
$ make

# Run test suite.
$ make check

# Install (Optional).
$ make install
```
下面是make check的结果：
![build mesos](https://github.com/bacTlink/OS-practice/raw/master/%E7%AC%AC1%E6%AC%A1%E4%BD%9C%E4%B8%9A/build%20mesos.png)
运行一下examples：
```
# Change into build directory.
$ cd build

# Start mesos master (Ensure work directory exists and has proper permissions).
$ ./bin/mesos-master.sh --ip=127.0.0.1 --work_dir=/var/lib/mesos

# Start mesos agent (Ensure work directory exists and has proper permissions).
$ ./bin/mesos-agent.sh --master=127.0.0.1:5050 --work_dir=/var/lib/mesos

# Visit the mesos web page.
$ http://127.0.0.1:5050

# Run C++ framework (Exits after successfully running some tasks.).
$ ./src/test-framework --master=127.0.0.1:5050

# Run Java framework (Exits after successfully running some tasks.).
$ ./src/examples/java/test-framework 127.0.0.1:5050

# Run Python framework (Exits after successfully running some tasks.).
$ ./src/examples/python/test-framework 127.0.0.1:5050
```
下面是C++ Framework运行的结果
![C++ Framework](https://github.com/bacTlink/OS-practice/raw/master/%E7%AC%AC1%E6%AC%A1%E4%BD%9C%E4%B8%9A/C++%20Framework.png)

---

##4.运行Spark on Mesos

下载Spark-2.1.0。
需要

1. 解压
2. 设置配置文件
3. 压缩为spark.tar.gz，放到对应路径下

我放spark.tar.gz的路径是/usr/local/

###贴一下配置文件

spark-defaults.conf：
spark.master是本机的IP地址
```
spark.io.compression.codec	lzf
spark.executor.uri	/usr/local/spark.tar.gz
spark.mesos.executor.home /usr/local/spark.tar.gz
spark.master	mesos://10.0.2.15:5050
spark.driver.memory 512M
spark.executor.memory 512M
```

spark-env.sh
```
#!/usr/bin/env bash
export MESOS_NATIVE_JAVA_LIBRARY=/usr/local/lib/libmesos-1.1.0.so
export SPARK_EXECUTOR_URI=/usr/local/spark.tar.gz
```

运行spark的SparkPi进行测试
```
./bin/run-examples SparkPi 1000
```
可以在mesos主页看到SparkPi成功运行。

###运行wordcount.py
使用文件：100份[aesop11.txt](http://www.textfiles.com/stories/aesop11.txt)的合体文件[aesop11x100.txt](https://github.com/bacTlink/OS-practice/raw/master/%E7%AC%AC1%E6%AC%A1%E4%BD%9C%E4%B8%9A/aesop11x100.txt)，大小22.34MB
命令：

```
$ time bin/spark-submit --total-executor-cores N examples/src/main/python/wordcount.py aesop11x100.txt > result.txt
```

N=1
![N=1](https://github.com/bacTlink/OS-practice/raw/master/%E7%AC%AC1%E6%AC%A1%E4%BD%9C%E4%B8%9A/N%3D1.png)
N=2
![N=2](https://github.com/bacTlink/OS-practice/raw/master/%E7%AC%AC1%E6%AC%A1%E4%BD%9C%E4%B8%9A/N%3D2.png)
N=3
![N=3](https://github.com/bacTlink/OS-practice/raw/master/%E7%AC%AC1%E6%AC%A1%E4%BD%9C%E4%B8%9A/N%3D3.png)
N=4
![N=4](https://github.com/bacTlink/OS-practice/raw/master/%E7%AC%AC1%E6%AC%A1%E4%BD%9C%E4%B8%9A/N%3D4.png)

总资源
![资源](https://github.com/bacTlink/OS-practice/raw/master/%E7%AC%AC1%E6%AC%A1%E4%BD%9C%E4%B8%9A/%E8%B5%84%E6%BA%90.png)

结果文件：[result.txt](https://github.com/bacTlink/OS-practice/raw/master/%E7%AC%AC1%E6%AC%A1%E4%BD%9C%E4%B8%9A/result.txt)

---

##5.遇到的问题

- [x] **mesos**
    - [x] **make** FAILED, out of memory
        - [x] 内存增至2G
        - [x] 虚拟硬盘增至8G（我用的是VirtualBox，使用VBoxManager和Linux分区命令）
        - [x] 新建4G交换文件
        - [x] 等上大半天（没有SSD的电脑的忧伤）
    - [ ] **make check** 10 TESTS FAILED，不过好像不影响
    - [x] 打不开mesos主页。在VirtualBox处设置端口转发
- [x] **Spark**
    - [x] initial job has not accepted any resources
        - 检查了一段时间后发现，mesos主页显示mesos内存总共只有800M
       - [x] 内存增至2.5G后，mesos主页显示mesos内存有1.3G
       - [x] 设置spark.driver.memory和spark.executor.memory
