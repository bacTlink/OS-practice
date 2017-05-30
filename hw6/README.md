# 第六次作业

# Paxos算法
Paxos算法是莱斯利·兰伯特于1990年提出的一种基于消息传递且具有高度容错特性的一致性算法。

## 工作原理
节点的角色分为proposers，acceptors和learners。每个节点可能有多个角色。
proposers的工作是提出提案。acceptors的工作是判断一个提案是否被接受。learners的工作是学习最新提出的提案。
所有的提案都用一个唯一的全序关系的编号。
proposer提出一个提案前，首先要和足以形成多数派的acceptors进行通信，获得他们进行的最近一次接受（accept）的提案（prepare过程），之后根据回收的信息决定这次提案的value，形成提案开始投票。当获得多数acceptors接受（accept）后，提案获得批准（chosen），由proposer将这个消息告知learner。([维基百科](https://zh.wikipedia.org/wiki/Paxos%E7%AE%97%E6%B3%95))
工作阶段有：
提出提案：
```
一个proposer提出一个提案并发送给acceptors的一个多数派。
    一个acceptor收到一个提案时，如果提案的编号大于它已经回复的所有提案，则回复上次接受的提案，并不再回复编号小于n的提案。
```
批准提案：
```
当一个proposer接收到acceptors的一个多数派的回复后，向所有回复提案的acceptors请求批准提案，提案的值由acceptors回复的内容决定。
如果一个acceptor没有回应过编号更大的提案，那么受到一个批准请求时，会立即接受这个请求。
```
此算法的本质是多数人通过一个决议，因为两个acceptor的多数派一定至少有一个公共的acceptor，以此保证回复的一致性。
关于learners，一个learner可以通过发起一个提案来获取最新的提案，但是它不会发送批准提案请求。

## 算法结果
在一个分布式数据库系统中，如果各节点的初始状态一致，每个节点都执行相同的操作序列，那么他们最后能得到一个一致的状态。这里假设没有拜占庭将军问题（Byzantine failure，即虽然有可能一个消息被传递了两次，但是绝对不会出现错误的消息）；只要等待足够的时间，消息就会被传到。

# Raft算法
Raft算法是Paxos的一个替代品。
场景：Leader Election

- 一开始所有的节点都在等待监听Leader
![61](https://github.com/bacTlink/OS-practice/raw/master/hw6/61.png)

- 第一个计时结束的节点，C，要求别的节点给它投票
![61_5](https://github.com/bacTlink/OS-practice/raw/master/hw6/61_5.png)

- 其它节点给C投票
![61_6](https://github.com/bacTlink/OS-practice/raw/master/hw6/61_6.png)

- C获得了大多数选票，成为leader，定期与其它节点联络
![62](https://github.com/bacTlink/OS-practice/raw/master/hw6/62.png)

- 其它节点接收到联络时，刷新自己的计时器，并向C发送心跳信息
![63](https://github.com/bacTlink/OS-practice/raw/master/hw6/63.png)

- 如果C突然宕机，其它节点会失去联络，定时器不会被重置
![64](https://github.com/bacTlink/OS-practice/raw/master/hw6/64.png)

- B的定时器先到，成为candidate，要求其它节点为他投票
![65](https://github.com/bacTlink/OS-practice/raw/master/hw6/65.png)

- B成功成为了leader，并向其它节点发送联络
![66](https://github.com/bacTlink/OS-practice/raw/master/hw6/66.png)

- 如果同时有多个节点成为candidate，那么可能不会选举出一个leader，因为没有一个节点获得大多数选票
![67](https://github.com/bacTlink/OS-practice/raw/master/hw6/67.png)

- 直到有一个节点成为leader，心跳联络重新开始
![68](https://github.com/bacTlink/OS-practice/raw/master/hw6/68.png)

# Mesos容错机制

## Mesos容错机制
- Master

Mesos使用热备份（hot-standby）设计来实现Master节点集合。
一个Master节点与多个备用（standby）节点运行在同一集群中，并由开源软件Zookeeper来监控。
Zookeeper会监控Master集群中所有的节点，并在Master节点发生故障时管理新Master的选举。 当Master节点发生故障时，其状态可以很快地在新选举的Master节点上重建。
Mesos的状态信息实际上驻留在Framework调度器和Slave节点集合之中。
当一个新的Master当选后，Zookeeper会通知Framework和选举后的Slave节点集合，以便使其在新的Master上注册。
彼时，新的 Master可以根据Framework和Slave节点集合发送过来的信息，重建内部状态。

- Framework。

Framework调度器的容错是通过Framework将调度器注册2份或者更多份到Master来实现。当一个调度器发生故障时，Master会通知另一个调度来接管。需要注意的是Framework自身负责实现调度器之间共享状态的机制。

- Slave。

Mesos实现了Slave的恢复功能，当Slave节点上的进程失败时，可以让执行器/任务继续运行，并为那个Slave进程重新连接那台Slave节点上运行的执行器/任务。当任务执行时，Slave会将任务的监测点元数据存入本地磁盘。如果Slave进程失败，任务会继续运行，当Master重新启动Slave进程后，因为此时没有可以响应的消息，所以重新启动的Slave进程会使用检查点数据来恢复状态，并重新与执行器/任务连接。

## 实践
每台电脑下载zookeeper：
```
wget http://www-eu.apache.org/dist/zookeeper/zookeeper-3.4.9/zookeeper-3.4.9.tar.gz
tar -xvf zookeeper-3.4.9.tar.gz
mv zookeeper-3.4.9.tar.gz zookeeper
```
每台电脑配置zookeeper：
```
cd zookeeper
cp conf/zoo_sample.cfg conf/zoo.cfg
vim conf/zoo.cfg
dataDir=/var/lib/zookeeper
server.1=172.16.6.103:2888:3888
server.2=172.16.6.225:2888:3888
server.3=172.16.6.95:2888:3888
```
分别创建工作目录：
```
mkdir /var/lib/zookeeper
echo "1" > /var/lib/zookeeper/myid
```
```
mkdir /var/lib/zookeeper
echo "2" > /var/lib/zookeeper/myid
```
```
mkdir /var/lib/zookeeper
echo "3" > /var/lib/zookeeper/myid
```
分别启动zookeeper：
```
bin/zkServer.sh start
ZooKeeper JMX enabled by default
Using config: /home/pkusei/zookeeper/bin/../conf/zoo.cfg
Starting zookeeper ... STARTED
```
分别查看状态，有两台是follower，一台是leader
```
bin/zkServer.sh status
ZooKeeper JMX enabled by default
Using config: /home/pkusei/zookeeper/bin/../conf/zoo.cfg
Mode: follower
```
```
bin/zkServer.sh status
ZooKeeper JMX enabled by default
Using config: /home/pkusei/zookeeper/bin/../conf/zoo.cfg
Mode: leader
```
```
bin/zkServer.sh status
ZooKeeper JMX enabled by default
Using config: /home/pkusei/zookeeper/bin/../conf/zoo.cfg
Mode: follower
```
分别启动mesos
```
nohup bin/mesos-master.sh --zk=zk://172.16.6.103:2181,172.16.6.225:2181,172.16.6.95:2181/mesos \
--quorum=2 --ip=172.16.6.103 --cluster=mesos_with_zookeeper \
--work_dir=/var/lib/mesos --log_dir=/var/log/mesos \
--port=5050 \
> master.log 2>&1 &
```
```
nohup bin/mesos-master.sh --zk=zk://172.16.6.103:2181,172.16.6.225:2181,172.16.6.95:2181/mesos \
--quorum=2 --ip=172.16.6.225 --cluster=mesos_with_zookeeper \
--work_dir=/var/lib/mesos --log_dir=/var/log/mesos \
--port=6060 \
> master.log 2>&1 &
```
```
nohup bin/mesos-master.sh --zk=zk://172.16.6.103:2181,172.16.6.225:2181,172.16.6.95:2181/mesos \
--quorum=2 --ip=172.16.6.95 --cluster=mesos_with_zookeeper \
--work_dir=/var/lib/mesos --log_dir=/var/log/mesos \
--port=7070 \
> master.log 2>&1 &
```
启动agent
```
nohup bin/mesos-agent.sh --master=zk://172.16.6.103:2181,172.16.6.225:2181,172.16.6.95:2181/mesos \
--work_dir=/var/lib/mesos --log_dir=/var/log/mesos --ip=172.16.6.103 --port=5051 \
--hostname=162.105.174.32 --containerizers=docker,mesos --image_providers=docker \
--isolation=docker/runtime > agent.log 2>&1 &
```
```
nohup bin/mesos-agent.sh --master=zk://172.16.6.103:2181,172.16.6.225:2181,172.16.6.95:2181/mesos \
--work_dir=/var/lib/mesos --log_dir=/var/log/mesos --ip=172.16.6.225 --port=5052 \
--hostname=162.105.174.32 --containerizers=docker,mesos --image_providers=docker \
--isolation=docker/runtime > agent.log 2>&1 &
```
```
nohup bin/mesos-agent.sh --master=zk://172.16.6.103:2181,172.16.6.225:2181,172.16.6.95:2181/mesos \
--work_dir=/var/lib/mesos --log_dir=/var/log/mesos --ip=172.16.6.95 --port=5053 \
--hostname=162.105.174.32 --containerizers=docker,mesos --image_providers=docker \
--isolation=docker/runtime > agent.log 2>&1 &
```
查看master.log，可以看到A new leading master (UPID=master@172.16.6.103:5050) is detected
```
I0529 10:03:07.130661 13858 contender.cpp:152] Joining the ZK group
I0529 10:03:07.132148 13857 master.cpp:1951] Successfully attached file '/var/log/mesos/lt-mesos-master.INFO'
I0529 10:03:07.137517 13853 contender.cpp:268] New candidate (id='4') has entered the contest for leadership
I0529 10:03:07.140060 13856 detector.cpp:152] Detected a new leader: (id='4')
I0529 10:03:07.140671 13856 group.cpp:697] Trying to get '/mesos/json.info_0000000004' in ZooKeeper
I0529 10:03:07.142967 13856 zookeeper.cpp:259] A new leading master (UPID=master@172.16.6.103:5050) is detected
I0529 10:03:07.143388 13852 master.cpp:2017] Elected as the leading master!
```
中途有可能会出现运行错误的现象：
```
[1]+  Aborted                 (core dumped) nohup bin/mesos-master.sh --zk=zk://172.16.6.103:2181,172.16.6.225:2181,172.16.6.95:2181/mesos --quorum=2 --ip=172.16.6.225 --cluster=mesos_with_zookeeper --work_dir=/var/lib/mesos --log_dir=/var/log/mesos > master.log 2>&1
root@oo-lab:~/mesos/build# nohup bin/mesos-master.sh --zk=zk://172.16.6.103:2181,172.16.6.225:2181,172.16.6.95:2181/mesos --quorum=2 --ip=172.16.6.225 --cluster=mesos_with_zookeeper --work_dir=/var/lib/mesos --log_dir=/var/log/mesos > master.log 2>&1 &
```
解决方法：
```
rm -rf /var/lib/mesos
rm -rf /var/log/mesos
```
尝试停掉leading master。
```
kill -SIGSTOP 15381
```
看到产生了新的leading master。
```
127 I0529 10:34:00.022974 33961 detector.cpp:152] Detected a new leader: (id='12')
128 I0529 10:34:00.023372 33961 group.cpp:697] Trying to get '/mesos/json.info_0000000012' in ZooKeeper
129 I0529 10:34:00.025087 33959 group.cpp:697] Trying to get '/mesos/log_replicas/0000000012' in ZooKeeper
130 I0529 10:34:00.025516 33961 zookeeper.cpp:259] A new leading master (UPID=master@172.16.6.225:6060) is detected
131 I0529 10:34:00.027565 33957 network.hpp:480] ZooKeeper group PIDs: { log-replica(1)@172.16.6.95:7070, log-replica(1)@172.16.6.225:6060 }
132 I0529 10:34:00.034410 33961 master.cpp:2030] The newly elected leader is master@172.16.6.225:6060 with id a1313df4-01b6-4c5d-b510-0539ea94fbdd
133 I0529 10:34:00.105789 33961 replica.cpp:493] Replica received implicit promise request from __req_res__(22)@172.16.6.225:6060 with proposal 1
```
尝试继续运行原本的master：
```
kill -SIGCONT 15381
```
结果它自杀了，因为它已经失去了一致性。
```
I0529 10:40:31.257436 15395 detector.cpp:152] Detected a new leader: None
I0529 10:40:31.260598 15395 log.cpp:257] Renewing replica group membership
2017-05-29 10:40:31,260:15381(0x7f02e9c72700):ZOO_INFO@log_env@726: Client environment:zookeeper.version=zookeeper C client 3.4.8
2017-05-29 10:40:31,260:15381(0x7f02e9c72700):ZOO_INFO@log_env@730: Client environment:host.name=oo-lab
2017-05-29 10:40:31,260:15381(0x7f02e9c72700):ZOO_INFO@log_env@737: Client environment:os.name=Linux
2017-05-29 10:40:31,260:15381(0x7f02e9c72700):ZOO_INFO@log_env@738: Client environment:os.arch=4.4.0-62-generic
2017-05-29 10:40:31,260:15381(0x7f02e9c72700):ZOO_INFO@log_env@739: Client environment:os.version=#83-Ubuntu SMP Wed Jan 18 14:10:15 UTC 2017
2017-05-29 10:40:31,260:15381(0x7f02e9c72700):ZOO_INFO@log_env@747: Client environment:user.name=pkusei
2017-05-29 10:40:31,260:15381(0x7f02e9c72700):ZOO_INFO@log_env@755: Client environment:user.home=/root
2017-05-29 10:40:31,260:15381(0x7f02e9c72700):ZOO_INFO@log_env@767: Client environment:user.dir=/home/pkusei/mesos/build
2017-05-29 10:40:31,260:15381(0x7f02e9c72700):ZOO_INFO@zookeeper_init@800: Initiating client connection, host=172.16.6.103:2181,172.16.6.225:2181,172.16.6.95:2181 sessionTimeout=10000 watcher=0x7f02f636899e sessionId=0 sessionPasswd=<null> context=0x7f02dc008108 flags=0
I0529 10:40:31.262454 15399 master.cpp:2030] The newly elected leader is None
Lost leadership... committing suicide!
I0529 10:40:31.264047 15397 group.cpp:510] ZooKeeper session expired
2017-05-29 10:40:31,264:15381(0x7f02e8c70700):ZOO_INFO@zookeeper_close@2543: Freeing zookeeper resources for sessionId=0x25c547287b3000a
```
重启这个master：
```
nohup bin/mesos-master.sh --zk=zk://172.16.6.103:2181,172.16.6.225:2181,172.16.6.95:2181/mesos --quorum=2 --ip=172.16.6.103 --port=5050 --cluster=mesos_with_zookeeper --hostname=162.105.174.32 --work_dir=/var/lib/mesos --log_dir=/var/log/mesos > master.log 2>&1 &
[1] 16844
```
查看日志，可以看到它发现了另一个leader
```
I0529 10:42:57.447948 16844 master.cpp:448] Master allowing unauthenticated agents to register
I0529 10:42:57.447954 16844 master.cpp:462] Master allowing HTTP frameworks to register without authentication
I0529 10:42:57.448022 16844 master.cpp:504] Using default 'crammd5' authenticator
W0529 10:42:57.448055 16844 authenticator.cpp:512] No credentials provided, authentication requests will be refused
I0529 10:42:57.448222 16844 authenticator.cpp:519] Initializing server SASL
I0529 10:42:57.463443 16864 zookeeper.cpp:259] A new leading master (UPID=master@172.16.6.225:6060) is detected
I0529 10:42:57.472682 16860 contender.cpp:152] Joining the ZK group
I0529 10:42:57.474468 16844 master.cpp:1951] Successfully attached file '/var/log/mesos/lt-mesos-master.INFO'
I0529 10:42:57.474555 16844 master.cpp:2030] The newly elected leader is master@172.16.6.225:6060 with id a1313df4-01b6-4c5d-b510-0539ea94fbdd
I0529 10:42:57.481673 16858 contender.cpp:268] New candidate (id='14') has entered the contest for leadership
```

# 综合作业
啊，终于做完了。

[Mesos](http://162.105.174.32:5050/)
[Jupyter](http://162.105.174.32:8888) Token是bactlink

先制作镜像，安装gluster，ssh，jupyter和etcd。
按照官方教程一步一步来就可以了。

## ssh免密登录
ssh免密登录的原理很简单，就是如果B的authorized_keys的列表中，有A的的公钥，那么B就直接可以让A免密登录了。
由于用的都是用一份镜像，只要生成私钥和公钥之后，将公钥追加到authorized_keys中，之后这个镜像的所有运行实例，都可以免密码互相登录了。
```
$ sshkey-gen -t rsa
$ cat .ssh/id_rsa.pub  >> .ssh/authorized_keys
```
编辑.ssh/config，连yes都不用输入了，内容如下：
```
StrictHostKeyChecking no
```

## 自动代理jupyter脚本
上次就发现，用mesos运行jupyter，由于jupyter不知道在哪一台机器上，很麻烦，于是写脚本解决这件事。
思路是：检测运行jupyter的docker是否在本机上，如果在本机上，那么就代理该docker，否则代理下一台机器（最后一台没有下一台）
三个脚本是不一样的。宿主机形成一个链状的结构，而一个宿主机又对应着多个docker容器。
每隔5秒会重新检测一次，看是否需要重设代理。
代理代码（C++含注释）如下：
```
#include <bits/stdc++.h>
#include <unistd.h>
using namespace std;

string num;

//数字转字符串
string number2string(int t)
{
	char tmpc[3];
	sprintf(tmpc, "%d", t);
	return tmpc;
}

//检测本机有多少台宿主机，检测哪一个是master
bool alive[5];
int detect_etcd_master()
{
	memset(alive, 0, sizeof(alive));
	for (int i = 0; i < 5; ++i)
	{
		string tmp = number2string(i);
//用etcd的HTTP API查看etcd的状态
		string cmd = "curl --connect-timeout 1 http://192.168.0.1" + tmp + ":2379/v2/stats/self > etcd_state" + tmp + ".txt";
		system(cmd.c_str());
	}
	int res = -1;
	for (int i = 0; i < 5; ++i)
	{
		string tmp = number2string(i);
		ifstream fin(("etcd_state" + tmp + ".txt").c_str());
		string stat;
		getline(fin, stat);
		fin.close();
	//有StateLeader字样，说明是Leader
		if (stat.find("StateLeader") != -1)
			res = i;
		if (stat.find("StateLeader") != -1)
			alive[i] = 1;
	//有StateFollower字样，说明是Follower
		if (stat.find("StateFollower") != -1)
			alive[i] = 1;
	}
	return res;
}

//检查是否有正在运行的代理，如果有，kill掉它
void stop_proxy()
{
	system("ps -ef | grep configurable > http.txt");
	ifstream fin("http.txt");
	string stat;
	while (getline(fin, stat))
	{
		if (stat.find("configurable-http-proxy") != -1) break;
	}
	fin.close();
	if (stat.find("configurable-http-proxy") != -1)
	{
		int id;
		sscanf(stat.c_str(), "%*s%d", &id);
		system(("kill -9 " + number2string(id)).c_str());
	}
}

//etcd的leader不在此宿主机上，代理到下一台主机
void run_proxy_next()
{
	system("nohup configurable-http-proxy --default-target=http://172.16.6.225:8887 --ip=172.16.6.103 --port=8888 >> /dev/null 2>&1 &");
}

//etcd的leader在此宿主机上，代理到对应的容器
void run_proxy(int master)
{
	string cmd = "nohup configurable-http-proxy";
	cmd += " --default-target=http://192.168.0.1"+ number2string(master) + ":8888";
	cmd += " --ip=172.16.6.103 --port=8888 >> /dev/null 2>&1 &";
	system(cmd.c_str());
}

int main()
{
        int last = -2;
        while (1)
        {
                int res = detect_etcd_master();//检测Leader
                cout << "master is " << res << endl;
                if (last != res)//如果Leader没有变，不需要重设代理。
                {
                        stop_proxy();
                        if (res == -1)
                                run_proxy_next();
                        else
                                run_proxy(res);
                }
                last = res;
                usleep(5000000);//每隔5s做一次检测。
        }
        return 0;
}

```

## docker启动脚本
为了实现加载分布式文件系统、etcd集群、自动在etcd的leader节点运行jupyter notebook，我的思路是在docker容器内部写一个脚本，运行此脚本自动启动所有的这一些要求。
并且脚本会自动检测etcd的环境是否发生变化，即使挂掉单一节点，hosts也能设置正确，jupyter也能在正确的机器上运行起来。
代理代码（C++含注释）如下：
```
#include <bits/stdc++.h>
#include <unistd.h>
using namespace std;

string num;

//数字转字符串
string number2string(int t)
{
	char tmpc[3];
	sprintf(tmpc, "%d", t);
	return tmpc;
}

//运行etcd，配置集群参数
void run_etcd()
{
	string myip = "192.168.0.1" + num;
	string cmd = "etcd";
	cmd += " --name node" + num;
	cmd += " --initial-advertise-peer-urls http://" + myip + ":2380";
	cmd += " --listen-peer-urls http://" + myip + ":2380";
	cmd += " --listen-client-urls http://" + myip + ":2379,http://127.0.0.1:2379";
	cmd += " --advertise-client-urls http://" + myip + ":2379";
	cmd += " --initial-cluster-token final";
	cmd += " --initial-cluster";
	for (int i = 0; i < 5; ++i)
	{
		if (i == 0)
			cmd += " ";
		else cmd += ",";
		string tmp = number2string(i);
		cmd += "node" + tmp + "=http://192.168.0.1" + tmp + ":2380";
	}
	cmd += " --initial-cluster-state new >> etcd.log 2>&1 &";
	system(cmd.c_str());
}

//利用etcd的HTTP API接口，检测etcd的leader
bool alive[5];
int detect_etcd_master()
{
	memset(alive, 0, sizeof(alive));
	for (int i = 0; i < 5; ++i)
	{
		string tmp = number2string(i);
//用etcd的HTTP API查看etcd的状态
		string cmd = "curl --connect-timeout 1 http://192.168.0.1" + tmp + ":2379/v2/stats/self > etcd_state" + tmp + ".txt";
		system(cmd.c_str());
	}
	int res = -1;
	for (int i = 0; i < 5; ++i)
	{
		string tmp = number2string(i);
		ifstream fin(("etcd_state" + tmp + ".txt").c_str());
		string stat;
		getline(fin, stat);
		fin.close();
	//有StateLeader字样，说明是Leader
		if (stat.find("StateLeader") != -1)
			res = i;
		if (stat.find("StateLeader") != -1)
			alive[i] = 1;
	//有StateFollower字样，说明是Follower
		if (stat.find("StateFollower") != -1)
			alive[i] = 1;
	}
	return res;
}

//运行jupyter
void run_jupyter()
{
	string cmd;
	cmd = "jupyter";
	cmd += " notebook";
	cmd += " --NotebookApp.token=bactlink";
	cmd += " --ip=0.0.0.0";
	cmd += " --port=8888";
	cmd += " >> /dev/null 2>&1 &";
	system(cmd.c_str());
}

//停止正在运行的jupyter
void stop_jupyter()
{
	system("ps -ef | grep jupyter > jupyter_running.txt");
	ifstream fin("jupyter_running.txt");
	string stat;
	while (getline(fin, stat))
	{
		if (stat.find("jupyter-notebook") != -1) break;
	}
	fin.close();
	if (stat.find("jupyter-notebook") != -1)
	{
		int id;
		sscanf(stat.c_str(), "%*s%d", &id);
		system(("kill -9 " + number2string(id)).c_str());
	}
}

//更新hosts列表
void update_hosts(int master)
{
	system("cp /etc/hosts hosts_backup");
	ifstream fin("/etc/hosts_backup");
	ofstream fout("/etc/hosts");
	string host;
	while (getline(fin, host))
	{
		if (host.substr(0, 11) != "192.168.0.1")
			fout << host;
	}
	fin.close();
	//node-0是etcd集群的leader
	fout << "192.168.0.1" << master << "\t" << "node-0" << endl;
	//其余的alive的node按顺序排列
	int cnt = 1;
	for (int i = 0; i < 5; ++i)
	if (alive[i] && i != master)
	{
		fout << "192.168.0.1" << i << "\t" << "node-" << cnt << endl;
		++cnt;
	}
	fout.close();
}

int main(int argc, char *argv[])
{
	num = argv[1];
	run_etcd();
	system("/usr/sbin/sshd");
	int last = -2;
	while (1)
	{
		int res = detect_etcd_master();
		if (last != res)//如果etcd的leader没变，不需要重新运行jupyter
		{
		    //如果本容器是etcd集群的leader，运行jupyter；
		    //否则停止本容器运行的jupyter。
			if (number2string(res) == num)
				run_jupyter();
			else
				stop_jupyter();
		}
		update_hosts(res);//更新host列表
		last = res;
		usleep(5000000);
	}
	return 0;
}
```

## Mesos Framework
剩下的只需要写一个Framework启动所有的容器，并运行保存在容器中的脚本就好啦！
由以前的经验，很容易用pymesos写出一个Framework：
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
				
        ;资源不足，只运行4个容器
			if self.cnt < 4:
			
			;设置ip地址
				ip = Dict()
				ip.key = 'ip'
				ip.value = '192.168.0.1' + str(self.cnt)

            ;设置calico网络
				NetworkInfo = Dict()
				NetworkInfo.name = 'calico_net'

				DockerInfo = Dict()
				DockerInfo.image = 'ubuntu-finalssh'
				DockerInfo.network = 'USER'
				DockerInfo.parameters = [ip]

            ;用docker启动
				ContainerInfo = Dict()
				ContainerInfo.type = 'DOCKER'
				ContainerInfo.docker = DockerInfo
				ContainerInfo.network_infos = [NetworkInfo]
				
			;运行编译好的start脚本，参数是容器的编号
				CommandInfo = Dict()
				CommandInfo.shell = False
				CommandInfo.value = 'start'
				CommandInfo.arguments = [str(self.cnt)]
				
				task = Dict()
				task_id = 'node-' + str(self.cnt)
				task.task_id.value = task_id
				task.agent_id.value = offer.agent_id.value
				task.name = 'Homework6'
				
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
	framework.name = "Final"
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

## 运行效果
废话不说，上图。
下图是：[Mesos](http://162.105.174.32:5050/)的运行画面，看到4个node愉快地跑起来了。
![mesos](https://github.com/bacTlink/OS-practice/raw/master/hw6/mesos.png)
下图是[Jupyter](http://162.105.174.32:8888)的运行界面，可以看到里面的一些文件什么的。Token是bactlink。
![jupyter](https://github.com/bacTlink/OS-practice/raw/master/hw6/jupyter.png)
下图输出了/etc/hosts，可以看到所有机子。利用etcd的HTTP API，可以看到node-0确实是etcd的Leader（图中显示了“StateLeader”）。
![leader](https://github.com/bacTlink/OS-practice/raw/master/hw6/leader.png)
试一试无秘登录。ssh之后，没有弹出选项询问密码，连yes都不需要输入：
![nokey](https://github.com/bacTlink/OS-practice/raw/master/hw6/ssh-nokey.png)

上面的图没办法说明Jupyter是运行在etcd集群的Leader的。不过我的代理都是直接代理到etcd的leader，也就是说是通过检测etcd集群的Leader来确定Jupyter的，所以如果成功打开了Jupyter，那就说明Jupyter就在etcd集群的leader处运行。

另外，我也没有实验断掉一个node。一方面是时间原因，另一方面是因为实在是没有必要，因为etcd的leader变得太频繁了！助教可以通过我提供的Jupyter链接到集群上看一看，过不了多久代理就失效，然后不久之后刷新又好了。刷新之后看一看/etc/hosts，发现etcd的Leader变了！在etcd变化的情况下，Jupyter仍然可以在外面登录，也说明我的脚本在一个node挂掉的情况下，是不会有问题的。
