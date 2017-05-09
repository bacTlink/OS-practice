# 第五次作业

标签（空格分隔）： OS-prac

---

Linux内核处理IP包流程
---
![ip](https://github.com/bacTlink/OS-practice/raw/master/hw5/1.jpg)

如图所示，左边显示的是由底层接收到的IP包的处理流程，右边显示的是从上层接受到的发送IP包的处理流程。

## 接收
- 判断IP包是否发送给本机
- 判断IP包是否出错
- 调整包长度
- 进行路由选择，判断是本地的还是转发的，是单播的还是多播的

## 发送
- 添加IP包头、检查是否出错
- 等待发送
- 根据ARP选择是要直接发送到局域网内的物理地址，还是外部的IP地址

## iptables
iptables是一个配置Linux内核防火墙的命令行工具，是netfilter项目的一部分。
iptables可以检测、修改、转发、重定向和丢弃IPv4数据包。如图：
![iptables](https://github.com/bacTlink/OS-practice/raw/master/hw5/2.png)
从任何网络端口进来的每一个IPv4数据包都要从上到下的穿过这张图。

在服务器上使用iptables分别实现如下功能并测试：
---
## 1)拒绝来自某一特定IP地址的访问；
我的电脑的当前IP地址是10.128.188.205，拒绝本机的访问：```$ sudo iptables -A INPUT -s 10.128.188.205 -j DROP```
好了，ssh断了，请允许我做一个悲伤的表情。
赶紧从另一台机子登录，然后```$ sudo iptables -A INPUT -s 10.128.188.205 -j DROP```。网络恢复。

## 2）拒绝来自某一特定mac地址的访问；
拒绝从另一台服务器访问，查看mac地址：
```
$ ifconfig
docker0   Link encap:Ethernet  HWaddr 02:42:5b:d1:dc:d6
          inet addr:172.17.0.1  Bcast:0.0.0.0  Mask:255.255.0.0
          inet6 addr: fe80::42:5bff:fed1:dcd6/64 Scope:Link
          UP BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:1666 errors:0 dropped:0 overruns:0 frame:0
          TX packets:5294 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0
          RX bytes:104086 (104.0 KB)  TX bytes:31091898 (31.0 MB)

docker_gwbridge Link encap:Ethernet  HWaddr 02:42:79:18:f7:9b
          inet addr:172.18.0.1  Bcast:0.0.0.0  Mask:255.255.0.0
          inet6 addr: fe80::42:79ff:fe18:f79b/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:126 errors:0 dropped:0 overruns:0 frame:0
          TX packets:8 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0
          RX bytes:9372 (9.3 KB)  TX bytes:648 (648.0 B)

ens32     Link encap:Ethernet  HWaddr 02:00:6b:c8:00:02
          inet addr:172.16.6.225  Bcast:172.16.6.255  Mask:255.255.255.0
          inet6 addr: fe80::6bff:fec8:2/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:10674489 errors:0 dropped:0 overruns:0 frame:0
          TX packets:9274599 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000
          RX bytes:5375606652 (5.3 GB)  TX bytes:1206601537 (1.2 GB)

lo        Link encap:Local Loopback
          inet addr:127.0.0.1  Mask:255.0.0.0
          inet6 addr: ::1/128 Scope:Host
          UP LOOPBACK RUNNING  MTU:65536  Metric:1
          RX packets:1360 errors:0 dropped:0 overruns:0 frame:0
          TX packets:1360 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1
          RX bytes:152780 (152.7 KB)  TX bytes:152780 (152.7 KB)

vethd2be57c Link encap:Ethernet  HWaddr 52:3d:65:63:b5:c1
          inet6 addr: fe80::503d:65ff:fe63:b5c1/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:8 errors:0 dropped:0 overruns:0 frame:0
          TX packets:133 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0
          RX bytes:648 (648.0 B)  TX bytes:11694 (11.6 KB)
```
拒绝访问：```$ sudo iptables -A INPUT -m mac --mac-source 02:00:6b:c8:00:02 -j DROP```
ping 访问超时。
3）只开放本机的http服务，其余协议与端口均拒绝；
```
$ iptables -A INPUT -p tcp --dport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
$ iptables -A OUTPUT -p tcp --sport 80 -m state --state NEW,ESTABLISHED -j ACCEPT
$ iptables -P INPUT DROP  
$ iptables -P FORWARD DROP  
$ iptables -P OUTPUT DROP  
```
命令如上。
4）拒绝回应来自某一特定IP地址的ping命令
```
iptables -A INPUT -s 172.16.6.225 -p icmp --icmp-type 8 -j ACCEPT
```
这里172.16.6.225是另一台服务器的IP。

解释Linux网络设备工作原理
---

## Linux Bridge
- Linux下的Bridge是一种虚拟设备，是 Linux 上用来做 TCP/IP二层协议交换的设备，在现实中与之对应的是交换机。
- Bridge与交换机的功能相似，在协议栈的二层上连接多个设备，同时与宿主机的上层相交互。Bridge 设备实例可以和 Linux 上其他网络设备实例连接，attach 一个设备，类似于在现实中在交换机和一个用户终端之间连接一根网线。当有数据到达时，Bridge 会根据报文中的 MAC 信息进行广播、转发、丢弃处理。
- bridge处理流程图：
![br](http://www.uml.org.cn/itil/images/2013111131.jpg)
- 如图所示，当bridge接收到一个数据时，br_handle_frame()被调用，进行一个和现实世界中的交换机类似的处理过程：判断包的类别（广播/单点），查找内部 MAC 端口映射表，定位目标端口号，将数据转发到目标端口或丢弃，自动更新内部 MAC 端口映射表以自我学习。
- Linux Bridge与交换机有不同。Linux Bridge具有隐藏的mac地址，可以设置IP地址，可以管理三层协议上的一些问题。
- 当Bridge与网络设备绑定时，对于宿主机的上层来说，只能看到Bridge，而看不到具体的网络设备。

## Linux Vlan
- Vlan(Virtual Local Area Network) ，即虚拟局域网，是指物理上不同位置的设备和用户，可以根据功能、部门及应用等因素将它们组织起来，相互之间的通信就好像它们在同一个网段中一样。
- Linux 里的 Vlan 设备是对 802.1.q 协议的一种内部软件实现，模拟现实世界中的 802.1.q 交换机。
- Vlan工作流程图：
![Vlan](http://www.uml.org.cn/itil/images/2013111132.jpg)
- Linux 里 802.1.q VLAN 设备是以母子关系出现的，母设备相当于现实世界中的交换机 TRUNK 口，用于连接上级网络，子设备相当于普通接口用于连接下级网络。一个母设备有多个下级网络。
- 当一个子设备有一包数据需要发送时，数据将被加入 Vlan Tag 然后从母设备发送出去。
- 当母设备收到一包数据时，它将会分析其中的 Vlan Tag，如果有对应的子设备存在，则把数据转发到那个子设备上并根据设置移除 VLAN Tag，否则丢弃该数据。
- 一个母设备中的多个子设备不能直接连接到同一个Vlan当中。Linux Vlan实现的是隔离功能，结合Bridge的交换功能，可以连接到同一个Vlan当中。

## Linux Veth
    +----------------------------------------------------------------+
    |                                                                |
    |       +------------------------------------------------+       |
    |       |             Newwork Protocol Stack             |       |
    |       +------------------------------------------------+       |
    |              ↑               ↑               ↑                 |
    |..............|...............|...............|.................|
    |              ↓               ↓               ↓                 |
    |        +----------+    +-----------+   +-----------+           |
    |        |   eth0   |    |   veth0   |   |   veth1   |           |
    |        +----------+    +-----------+   +-----------+           |
    |192.168.1.11  ↑               ↑               ↑                 |
    |              |               +---------------+                 |
    |              |         192.168.2.11     192.168.2.1            |
    +--------------|-------------------------------------------------+
                   ↓
             Physical Network
         
- Veth(Virtual Ethernet Pair) 是一个成对的端口,所有从这对端口一端进入的数据包都将从另一端出来。
- Veth通过Bridge，可以将不同namespace的设备连接起来。

## Tun/tap
    +----------------------------------------------------------------+
    |                                                                |
    |  +--------------------+      +--------------------+            |
    |  | User Application A |      | User Application B |<-----+     |
    |  +--------------------+      +--------------------+      |     |
    |               | 1                    | 5                 |     |
    |...............|......................|...................|.....|
    |               ↓                      ↓                   |     |
    |         +----------+           +----------+              |     |
    |         | socket A |           | socket B |              |     |
    |         +----------+           +----------+              |     |
    |                 | 2               | 6                    |     |
    |.................|.................|......................|.....|
    |                 ↓                 ↓                      |     |
    |             +------------------------+                 4 |     |
    |             | Newwork Protocol Stack |                   |     |
    |             +------------------------+                   |     |
    |                | 7                 | 3                   |     |
    |................|...................|.....................|.....|
    |                ↓                   ↓                     |     |
    |        +----------------+    +----------------+          |     |
    |        |      eth0      |    |      tun0      |          |     |
    |        +----------------+    +----------------+          |     |
    |    10.32.0.11  |                   |   192.168.3.11      |     |
    |                | 8                 +---------------------+     |
    |                |                                               |
    +----------------|-----------------------------------------------+
                     ↓
             Physical Network

- 如图，这里tun0就是一个tun/tap设备，它收到包之后，会发送给本机的进程，而不是实际的物理网络。
- 一个典型的应用就是VPN。

Calico
---
Calico是一个纯3层的数据中心网络解决方案，能够提供可控的VM、容器、裸机之间的IP通信。通过将整个互联网的可扩展IP网络原则压缩到数据中心级别，Calico在每一个计算节点利用Linux Kernel实现了一个高效的vRouter来负责数据转发，而每个vRouter通过BGP协议负责把自己上运行的workload的路由信息像整个Calico网络内传播——小规模部署可以直接互联，大规模下可通过指定的BGP route reflector来完成。

Calico节点组网可以直接利用数据中心的网络结构（无论是L2或者L3），不需要额外的NAT，隧道或者Overlay Network。也因此它所需要发的包头十分短：
![hd](https://www.projectcalico.org/wp-content/uploads/2015/03/no-encap.png)

## Calico架构图：
![ca](http://dockerone.com/uploads/article/20160701/e3a52dd12c89d445a8f3f1be08124e27.png)

Calico由以下系统组件组成：

- Felix，Calico Agent，跑在每台需要运行Workload的节点上，主要负责配置路由及ACLs等信息来确保Endpoint的连通状态；
- etcd，分布式键值存储，主要负责网络元数据一致性，确保Calico网络状态的准确性；
- BGP Client（BIRD）, 主要负责把Felix写入Kernel的路由信息分发到当前Calico网络，确保Workload间的通信的有效性；
- BGP Route Reflector（BIRD），大规模部署时使用，摒弃所有节点互联的 mesh 模式，通过一个或者多个BGP Route Reflector来完成集中式的路由分发；

### Calico网络连接示意图：
![pic](http://dockerone.com/uploads/article/20160701/9c5a73710905be29c7b4be02796c72b9.png)

### 一个数据包从源容器发送到目标容器接收的具体过程
1. 通过Calico设置的Veth pair，传送到宿主机上。
2. 通过宿主机的cali发送
3. 穿过集群的网络
4. 到达另一个宿主机
5. 通过Calico设置的Veth pair，传送到容器中

Calico和Contiv
---
Contiv Netplugin 是来自思科的解决方案。编程语言为 Go。
Contiv 基于 OpenvSwitch，以插件化的形式支持容器访问网络，支持 VLAN，Vxlan，多租户，主机访问控制策略等。
## Contiv特点

- 多特点策略模型，提供安全、可预测的应用搭建
- 容器吞吐量高
- 支持多用户、隔离、重叠子网
- 集成IP地址管理和发现服务的功能
- 多层物理结构：Layer2 (VLAN)、Layer3 (BGP)、Overlay (VXLAN)、Cisco SDN Solution (ACI)
- 支持IPv6
- 可拓展的策略和路由分配
- 与一些应用集成，包括：Docker Compose和Kubernetes deployment manager
- 内置east-west微服务负载均衡
- 存储，控制，网络和管理流量均有隔离

## 对比
- Calico没有中心节点，IP管理依赖于etcd；Contiv有中心节点，集中管理IP资源。
- Calico不支持VLAN和VXLAN；Contiv支持。
- Calico是纯3层的，简单方便；Contiv既支持2层，也支持3层。

编写mesos framework
---

### 搭建ETCD服务器

先安装etcd，并关闭服务
```
root@oo-lab:/# apt install etcd
root@oo-lab:/# service etcd stop
```

用自定义的参数重启etcd服务


    etcd --name node0 --initial-advertise-peer-urls http://172.16.6.103:2380 \
    --listen-peer-urls http://172.16.6.103:2380 \
    --listen-client-urls http://172.16.6.103:2379,http://127.0.0.1:2379 \
    --advertise-client-urls http://172.16.6.103:2379 \
    --initial-cluster-token bacTlink \
    --initial-cluster node0=http://172.16.6.103:2380,node1=http://172.16.6.225:2380,node2=http://172.16.6.95:2380 \
    --initial-cluster-state new >> /dev/null 2>&1 &

    etcd --name node1 --initial-advertise-peer-urls http://172.16.6.225:2380 \
    --listen-peer-urls http://172.16.6.225:2380 \
    --listen-client-urls http://172.16.6.225:2379,http://127.0.0.1:2379 \
    --advertise-client-urls http://172.16.6.225:2379 \
    --initial-cluster-token bacTlink \
    --initial-cluster node0=http://172.16.6.103:2380,node1=http://172.16.6.225:2380,node2=http://172.16.6.95:2380 \
    --initial-cluster-state new >> /dev/null 2>&1 &

    etcd --name node2 --initial-advertise-peer-urls http://172.16.6.95:2380 \
    --listen-peer-urls http://172.16.6.95:2380 \
    --listen-client-urls http://172.16.6.95:2379,http://127.0.0.1:2379 \
    --advertise-client-urls http://172.16.6.95:2379 \
    --initial-cluster-token bacTlink \
    --initial-cluster node0=http://172.16.6.103:2380,node1=http://172.16.6.225:2380,node2=http://172.16.6.95:2380 \
    --initial-cluster-state new >> /dev/null 2>&1 &

让docker支持etcd
先退出docker
```
$ service docker stop
```
再用参数启动docker的服务
```
$ root@oo-lab:/# dockerd --cluster-store etcd://172.16.6.103:2379 >> /dev/null 2>&1 &
$ root@oo-lab:/# dockerd --cluster-store etcd://172.16.6.225:2379 >> /dev/null 2>&1 &
$ root@oo-lab:/# dockerd --cluster-store etcd://172.16.6.95:2379 >> /dev/null 2>&1 &
```
安装Calico，由于文件wget下载失败，从本地下载后再上传服务器，然后运行：
```
$ mv calicoctl /usr/local/bin/calicoctl
$ chmod +x /usr/local/bin/calicoctl
$ calicoctl node run --ip 172.16.6.103 --name node0
$ calicoctl node run --ip 172.16.6.225 --name node1
$ calicoctl node run --ip 172.16.6.95 --name node2
```
检查calico状态
```
$ calicoctl node status
Calico process is running.

IPv4 BGP status
+--------------+-------------------+-------+----------+-------------+
| PEER ADDRESS |     PEER TYPE     | STATE |  SINCE   |    INFO     |
+--------------+-------------------+-------+----------+-------------+
| 172.16.6.225 | node-to-node mesh | up    | 13:40:08 | Established |
| 172.16.6.95  | node-to-node mesh | up    | 13:40:10 | Established |
+--------------+-------------------+-------+----------+-------------+

IPv6 BGP status
No IPv6 peers found.

```
创建calico网络：
```
docker network create --driver calico --ipam-driver calico-ipam --subnet=192.168.0.0/16 calico_net
```

### 在三台服务器上创建docker ssh镜像
Dockerfile如下：
```
FROM ubuntu-updated

RUN apt-get update
RUN apt-get install -y ssh

RUN useradd -ms /bin/bash user
RUN adduser user sudo
RUN echo 'user:user' | chpasswd

RUN mkdir /var/run/sshd

USER user
WORKDIR /home/user

CMD ["/usr/sbin/sshd", "-D"]
```
然后创建镜像：
```
$ docker build -t ubuntu-ssh .
```
### 在三台服务器上创建jupyter镜像
Dockerfile如下：
```
FROM ubuntu-updated

RUN apt-get update
RUN apt-get install -y ssh python-pip
RUN pip install --upgrade pip
RUN pip install jupyter

RUN useradd -m calico
RUN echo "calico:calico" | chpasswd

RUN mkdir /var/run/sshd

USER calico
EXPOSE 22
WORKDIR /home/calico

CMD ["/usr/local/bin/jupyter", "notebook", "--NotebookApp.token=bactlink", "--ip=0.0.0.0", "--port=8888"]
```
然后创建镜像：
```
$ docker build -t ubuntu-jupyter .
```

设置反向代理：
```
nohup configurable-http-proxy --default-target=http://192.168.0.10:8888 --ip=172.16.6.103 --port=8888 >> /dev/null 2>&1 &
```

用pymesos写的framework代码如下：
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

from pymesos import MesosSchedulerDriver, Scheduler, encode_data
from addict import Dict

TASK_CPU = 1
TASK_MEM = 4

class MinimalScheduler(Scheduler):

	def __init__(self):
		self.cnt = 0

	def resourceOffers(self, driver, offers):
		filters = {'refuse_seconds': 5}

		for offer in offers:
			cpus = self.getResource(offer.resources, 'cpus')
			mem = self.getResource(offer.resources, 'mem')
			if cpus < TASK_CPU or mem < TASK_MEM:
				continue

#Jupyter
			if self.cnt == 0:
				
				ip = Dict()
				ip.key = 'ip'
				ip.value = '192.168.0.10'

				NetworkInfo = Dict()
				NetworkInfo.name = 'calico_net'

				DockerInfo = Dict()
				DockerInfo.image = 'ubuntu-jupyter'
				DockerInfo.network = 'USER'
				DockerInfo.parameters = [ip]

				ContainerInfo = Dict()
				ContainerInfo.type = 'DOCKER'
				ContainerInfo.docker = DockerInfo
				ContainerInfo.network_infos = [NetworkInfo]
				
				CommandInfo = Dict()
				CommandInfo.shell = False
				CommandInfo.value = 'jupyter'
				CommandInfo.arguments = ['notebook', '--ip=0.0.0.0', '--NotebookApp.token=bactlink', '--port=8888']
				
				task = Dict()
				task_id = 'Jupyter'
				task.task_id.value = task_id
				task.agent_id.value = offer.agent_id.value
				task.name = 'Homework5'
				
				task.container = ContainerInfo
				task.command = CommandInfo
				
				task.resources = [
					dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
					dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
				]

				self.cnt = self.cnt + 1
				driver.launchTasks(offer.id, [task], filters)

			elif self.cnt < 5:
			
#sshd	
				ip = Dict()
				ip.key = 'ip'
				ip.value = '192.168.0.1' + str(self.cnt)

				NetworkInfo = Dict()
				NetworkInfo.name = 'calico_net'

				DockerInfo = Dict()
				DockerInfo.image = 'ubuntu-ssh'
				DockerInfo.network = 'USER'
				DockerInfo.parameters = [ip]

				ContainerInfo = Dict()
				ContainerInfo.type = 'DOCKER'
				ContainerInfo.docker = DockerInfo
				ContainerInfo.network_infos = [NetworkInfo]
				
				CommandInfo = Dict()
				CommandInfo.shell = False
				CommandInfo.value = '/usr/sbin/sshd'
				CommandInfo.arguments = ['-D']
				
				task = Dict()
				task_id = 'sshd' + str(self.cnt)
				task.task_id.value = task_id
				task.agent_id.value = offer.agent_id.value
				task.name = 'Homework5'
				
				task.container = ContainerInfo
				task.command = CommandInfo
				
				task.resources = [
					dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
					dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
				]

				self.cnt = self.cnt + 1
				driver.launchTasks(offer.id, [task], filters)


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

	framework = Dict()
	framework.user = getpass.getuser()
	framework.name = "Jupyter"
	framework.hostname = socket.gethostname()

	driver = MesosSchedulerDriver(
		MinimalScheduler(),
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

Mesos地址为 http://162.105.174.32:5050
Mesos截图：
![cluster](https://github.com/bacTlink/OS-practice/raw/master/hw5/cluster.png)
![cluster](https://github.com/bacTlink/OS-practice/raw/master/hw5/sshds.png)
Jupyter地址为 http://162.105.174.32:8888
Jupyter截图：
![cluster](https://github.com/bacTlink/OS-practice/raw/master/hw5/first_page.png)
Jupyter的token是bactlink
可以使用终端：
![cluster](https://github.com/bacTlink/OS-practice/raw/master/hw5/terminal.png)
使用终端连接其中一个sshd容器：
![cluster](https://github.com/bacTlink/OS-practice/raw/master/hw5/ssh.png)
