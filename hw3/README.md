
# 第三次作业


---

## 安装配置Docker
```
$ apt-get update
$ apt-get install docker
$ apt install docker.io
```

---

## docker命令举例

### 要求：
查阅相关资料及docker相关文档，介绍docker基本命令(如run,images,network等)，要求至少包含镜像管理，容器管理，网络管理三部分的命令，至少介绍5个不同的命令，尽量完整的介绍命令，包括命令的含义和其用法，例子。

### docker run

        Usage:  docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
        用于启动一个镜像，启动的参数是[OPTIONS]，[COMMAND]是执行的命令，命令结束后docker镜像随之退出。
        
例子：
```
$ docker run ubuntu echo "Hello world"
Hello world
```
运行ubuntu镜像，运行的命令为echo "Hello world"，然后在屏幕上输出了Hello world，命令结束，镜像退出。

### docker ps

        Usage:  docker ps [OPTIONS]
        用于列举出容器

例子：
```
$ docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                NAMES
dc73f070f67a        ubuntu-updated      "nginx -g 'daemon off"   10 hours ago        Up 10 hours         0.0.0.0:80->80/tcp   hungry_ardinghelli
```
可以看到一个正在运行的ubuntu-updated镜像，ID为dc73f070f67a，执行的命令为"nginx -g 'daemon off"，创建时间为10 hours ago，状态是启动了10 hours，映射了80:80的tcp端口，名字为hungry_ardinghelli。

### docker pull

        Usage:  docker pull [OPTIONS] NAME[:TAG|@DIGEST]
        用于下载一个镜像

例子：
```
$ docker pull ubuntu
```
下载官方的ubuntu镜像。

### docker network

        Usage:  docker network COMMAND
        用于执行网络相关的命令

例子：
```
$ docker network ls
NETWORK ID          NAME                DRIVER              SCOPE
9e8adb6e3704        bridge              bridge              local
02dda3dc5720        docker_gwbridge     bridge              local
54f348a92c91        host                host                local
4kxgi0tcfl5n        ingress             overlay             swarm
ad1c3a40b098        mybridge            bridge              local
d01e12367ddf        none                null                local
```
可以看出列举出了当前存在的docker网络

### docker commit

        Usage:  docker commit [OPTIONS] CONTAINER [REPOSITORY[:TAG]]
        用于从对容器的一次修改，创建一个新的镜像。

```
$ docker ps -a
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS                     PORTS                NAMES
783e92e62428        ubuntu              "echo 'Hello world'"     8 minutes ago       Exited (0) 8 minutes ago                        tiny_austin
dc73f070f67a        ubuntu-updated      "nginx -g 'daemon off"   10 hours ago        Up 10 hours                0.0.0.0:80->80/tcp   hungry_ardinghelli
$ docker commit 783e ubuntu2
```
先用ps命令查看运行后的容器ID，选择想用的容器ID（不必输入完整ID，输入前缀即可），输入新的镜像名字，即可创建镜像。

### docker命令组合使用
例子：
```
$ docker ps -a | grep Exit | cut -d ' ' -f 1 | xargs sudo docker rm
```
先查看docker ps，然后查找Exit的容器，截取其ID，作为docker rm的参数。
以上命令的作用是删除所有Exit的容器。

---

## 建立nginx服务器

### 要求：
创建一个基础镜像为ubuntu的docker镜像，随后再其中加入nginx服务器，之后启动nginx服务器并利用tail命令将访问日志输出到标准输出流。要求该镜像中的web服务器主页显示自己编辑的内容，编辑的内容包含学号和姓名。之后创建一个自己定义的network，模式为bridge，并让自己配的web服务器容器连到这一网络中。要求容器所在宿主机可以访问这个web服务器搭的网站。请在报告中详细阐述搭建的过程和结果。

### 步骤：

安装ubuntu:
```
$ docker pull ubuntu
```
打开ubuntu命令行交互：
```
$ docker run -i -t ubuntu /bin/bash
```
由于官方ubuntu镜像的apt源是archive.ubuntu.com，太慢了，换成清华的镜像。
用cat命令改掉/etc/apt/sources.list。
安装vim。
```
$ echo -e "deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial main restricted
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-updates main restricted
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial universe
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-updates universe
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial multiverse
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-updates multiverse
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-backports main restricted universe multiverse
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-security main restricted
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-security universe
deb http://mirrors.tuna.tsinghua.edu.cn/ubuntu/ xenial-security multiverse
" \
> /etc/apt/sources.list
$ apt-get update
$ apt-get install vim
```

安装nginx：
```
$ apt-get install nginx
```
修改nginx主页
```
$ vim /var/www/html/index.nginx-debian.html
```
Ctrl-D退出后，保存为ubuntu-updated
```
$ root@oo-lab:~# docker ps -l
CONTAINER ID        IMAGE       COMMAND             CREATED             STATUS                     PORTS               NAMES
77d602c491c8        ubuntu      "/bin/bash"         2 minutes ago       Exited (0) 8 seconds ago                       elated_torvalds

$root@oo-lab:~# docker commit 77d ubuntu-updated
sha256:d8e6ec3c1f5e54c490e325e6337cf52b9642e3707ae2f509adc68ac6dd54777f
```
运行交互命令行，设定端口，运行tail查看输出
```
$ docker run -p 80:80 -i -t ubuntu-updated /bin/bash
$ nginx
$ tail -f /var/log/nginx/access.log
```
然后从http://162.105.174.32/ 访问端口、本地用curl访问网页，tail显示了访问记录：
![tail](https://github.com/bacTlink/OS-practice/raw/master/hw3/tail.png)

创建一个自定义网络：
```
$ docker create network mybridge
$ docker network ls
NETWORK ID          NAME                DRIVER              SCOPE
49610f3edd44        bridge              bridge              local
54f348a92c91        host                host                local
ad1c3a40b098        mybridge            bridge              local
d01e12367ddf        none                null                local
```
可以看到自己创建的网络mybridge，方式为bridge（默认），在此网络上挂上nginx服务器：
```
$ docker run --network mybridge -d -p 80:80 ubuntu-updated nginx -g "daemon off;"
```
可以从http://162.105.174.32/ 访问了。

---

## 将docker容器分别加入四个不同的网络模式

### 要求
尝试让docker容器分别加入四个不同的网络模式:null,bridge,host,overlay。请查阅相关资料和docker文档，阐述这些网络模式的区别。

### null：使用 --net=none 指定
- Docker 容器拥有自己的 Network Namespace，但是，并不为 Docker 容器进行任何网络配置。这个 Docker 容器没有网卡、IP、路由等信息。需要我们自己为 Docker 容器添加网卡、配置 IP 等。
```
$ docker run --net=none -i -t ubuntu-updated-back /bin/bash
$ ifconfig
lo        Link encap:Local Loopback
          inet addr:127.0.0.1  Mask:255.0.0.0
          inet6 addr: ::1/128 Scope:Host
          UP LOOPBACK RUNNING  MTU:65536  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1
          RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)
```
只剩lo网卡了

### bridge：使用--net=bridge 指定
- bridge 模式是 Docker 默认的网络设置。
- 此模式会为每一个容器分配 Network Namespace、设置IP等，并将一个主机上的 Docker 容器连接到一个虚拟网桥上。
- 当Docker server启动时，会在主机上创建一个名为 docker0 的虚拟网桥，此主机上启动的 Docker 容器会连接到这个虚拟网桥上。
- 虚拟网桥的工作方式和物理交换机类似，对于新加入的容器，会选取一个网段，然后取一个子网中不存在的主机地址，分配给容器。
- 与传统虚拟机的桥接网卡相似。
```
$ docker run --net=bridge -i -t ubuntu-updated-back /bin/bash
$ ifconfig
eth0      Link encap:Ethernet  HWaddr 02:42:ac:11:00:03
          inet addr:172.17.0.3  Bcast:0.0.0.0  Mask:255.255.0.0
          inet6 addr: fe80::42:acff:fe11:3/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:7 errors:0 dropped:0 overruns:0 frame:0
          TX packets:7 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0
          RX bytes:578 (578.0 B)  TX bytes:578 (578.0 B)

lo        Link encap:Local Loopback
          inet addr:127.0.0.1  Mask:255.0.0.0
          inet6 addr: ::1/128 Scope:Host
          UP LOOPBACK RUNNING  MTU:65536  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1
          RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)
```
看到了172.17网段的网卡了。

### host：使用 --net=host 指定
- 如果启动容器的时候使用 host 模式，那么这个容器将不会获得一个独立的 Network Namespace，而是和宿主机共用一个 Network Namespace 。
- 容器将不会虚拟出自己的网卡，配置自己的IP等，而是使用宿主机的IP和端口。
```
$ docker run --net=host -i -t ubuntu-updated-back /bin/bash
```
太多了就不贴了。

### container：使用 --net=container:NAME_or_ID 指定
- 这个模式指定新创建的容器和已经存在的一个容器共享一个 Network Namespace。新创建的容器不会创建自己的网卡，配置自己的 IP，而是和一个指定的容器共享 IP、端口范围等。
```
$ docker run --net=container:ubuntu-updated -i -t ubuntu-updated-back /bin/bash
```
和ubuntu-updated一样。

### overlay：
先初始化swarm：
```
$ docker swarm init --advertise-addr 172.16.6.103
Swarm initialized: current node (cgjv3i449yup4zp545wr0l90h) is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join \
    --token SWMTKN-1-3j30yfm16ypxbuj2j3vlihawoobxwu92snfnq9dher5shcoqpk-6dj454k6gt9sp0zjtvv8ysyhb \
    172.16.6.103:2377

To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.
```
在另一台机器上执行所给的命令：
```
$ docker swarm join \
>     --token SWMTKN-1-3j30yfm16ypxbuj2j3vlihawoobxwu92snfnq9dher5shcoqpk-6dj454k6gt9sp0zjtvv8ysyhb \
>     172.16.6.103:2377
This node joined a swarm as a worker.

```
成功加入。
这样用命令
```
$ docker service create
```
可以创建在不同宿主机上也能互相查看的docker容器。

---

## 阅读代码

### 要求
阅读mesos中负责与docker交互的代码，谈谈mesos是怎样与docker进行交互的，并介绍docker类中run函数大致做了什么。

### 过程

- 查看了docker.hpp，发现一些接口函数：
```C++
// Performs 'docker run IMAGE'. Returns the exit status of the
  // container. Note that currently the exit status may correspond
  // to the exit code from a failure of the docker client or daemon
  // rather than the container. Docker >= 1.10 [1] uses the following
  // exit statuses inherited from 'chroot':
  //     125 if the error is with Docker daemon itself.
  //     126 if the contained command cannot be invoked.
  //     127 if the contained command cannot be found.
  //     Exit code of contained command otherwise.
  //
  // [1]: https://github.com/docker/docker/pull/14012
  virtual process::Future<Option<int>> run(
      const mesos::ContainerInfo& containerInfo,
      const mesos::CommandInfo& commandInfo,
      const std::string& containerName,
      const std::string& sandboxDirectory,
      const std::string& mappedDirectory,
      const Option<mesos::Resources>& resources = None(),
      const Option<std::map<std::string, std::string>>& env = None(),
      const Option<std::vector<Device>>& devices = None(),
      const process::Subprocess::IO& _stdout =
        process::Subprocess::FD(STDOUT_FILENO),
      const process::Subprocess::IO& _stderr =
        process::Subprocess::FD(STDERR_FILENO))
    const;

  // Returns the current docker version.
  virtual process::Future<Version> version() const;

  // Performs 'docker stop -t TIMEOUT CONTAINER'. If remove is true then a rm -f
  // will be called when stop failed, otherwise a failure is returned. The
  // timeout parameter will be passed through to docker and is the amount of
  // time for docker to wait after stopping a container before killing it.
  // A value of zero (the default value) is the same as issuing a
  // 'docker kill CONTAINER'.
  virtual process::Future<Nothing> stop(
      const std::string& containerName,
      const Duration& timeout = Seconds(0),
      bool remove = false) const;

  // Performs 'docker kill --signal=<signal> CONTAINER'.
  virtual process::Future<Nothing> kill(
      const std::string& containerName,
      int signal) const;

  // Performs 'docker rm (-f) CONTAINER'.
  virtual process::Future<Nothing> rm(
      const std::string& containerName,
      bool force = false) const;

  // Performs 'docker inspect CONTAINER'. If retryInterval is set,
  // we will keep retrying inspect until the container is started or
  // the future is discarded.
  virtual process::Future<Container> inspect(
      const std::string& containerName,
      const Option<Duration>& retryInterval = None()) const;

  // Performs 'docker ps (-a)'.
  virtual process::Future<std::list<Container>> ps(
      bool all = false,
      const Option<std::string>& prefix = None()) const;
```

- ps命令应该是最简单的docker命令之一，查看docker.cpp的ps函数：
```C++
Future<list<Docker::Container>> Docker::ps(
    bool all,
    const Option<string>& prefix) const
{
  string cmd = path + " -H " + socket + (all ? " ps -a" : " ps");

  VLOG(1) << "Running " << cmd;

  Try<Subprocess> s = subprocess(
      cmd,
      Subprocess::PATH("/dev/null"),
      Subprocess::PIPE(),
      Subprocess::PIPE());

  if (s.isError()) {
    return Failure("Failed to create subprocess '" + cmd + "': " + s.error());
  }

  // Start reading from stdout so writing to the pipe won't block
  // to handle cases where the output is larger than the pipe
  // capacity.
  const Future<string>& output = io::read(s.get().out().get());

  return s.get().status()
    .then(lambda::bind(&Docker::_ps, *this, cmd, s.get(), prefix, output));
}
```

- 可以发现，其实就是就是用命令行创建子进程去执行docker ps命令、再读取结果的交互方式。
- 查看docker.cpp的run函数，它做的事情有：

        查找docker是否存在
        获取docker的信息
        处理命令行参数：
            权限
            CPU资源
            内存资源
            环境变量
            处理volume
            映射路径
            处理volumeDriver
            设置网络
            设置host
            处理dockerInfo中的参数
            处理端口映射
            处理devices
            处理entrypoint
            设置名字、镜像
            添加命令行指定的参数
        创建子进程启动docker run
        处理错误情况
        处理docker返回的信息
        
---

## 运行nginx

### 要求
写一个framework，以容器的方式运行task，运行前面保存的nginx服务器镜像，网络为HOST，运行后，外部主机可以通过访问宿主ip+80端口来访问这个服务器搭建的网站，网站内容包含学号和姓名。报告中对源码进行说明，并附上源码和运行的相关截图。

### 实现过程

先启动一个docker镜像运行nginx，然后用docker stats查看它所用的资源，以便之后分配资源。
```
$ docker run -d -p 80:80 -i -t --name=c1 ubuntu-updated-back nginx -p 81 -g "daemon off;"
003e6da6430c7a3cf836a57c268b5f1e23236dbaac19f05b0c85fb6b33e05f06
$ docker images status
REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
$ docker stats
CONTAINER           CPU %               MEM USAGE / LIMIT       MEM %               NET I/O             BLOCK I/O             PIDS
003e6da6430c        0.00%               1.957 MiB / 983.7 MiB   0.20%               648 B / 648 B       237.6 kB / 8.192 kB   2
CONTAINER           CPU %               MEM USAGE / LIMIT       MEM %               NET I/O             BLOCK I/O             PIDS
003e6da6430c        0.00%               1.957 MiB / 983.7 MiB   0.20%               648 B / 648 B       237.6 kB / 8.192 kB   2
CONTAINER           CPU %               MEM USAGE / LIMIT       MEM %               NET I/O             BLOCK I/O             PIDS
003e6da6430c        0.00%               1.957 MiB / 983.7 MiB   0.20%               648 B / 648 B       237.6 kB / 8.192 kB   2
CONTAINER           CPU %               MEM USAGE / LIMIT       MEM %               NET I/O             BLOCK I/O             PIDS
003e6da6430c        0.00%               1.957 MiB / 983.7 MiB   0.20%               648 B / 648 B       237.6 kB / 8.192 kB   2
^C
$ docker ps
CONTAINER ID        IMAGE                 COMMAND                  CREATED             STATUS              PORTS                NAMES
003e6da6430c        ubuntu-updated-back   "nginx -p 81 -g 'daem"   39 seconds ago      Up 38 seconds       0.0.0.0:80->80/tcp   c1
$ docker stop 003
003
$ docker ps -a | grep Exit | cut -d ' ' -f 1 | xargs sudo docker rm
003e6da6430c
```
看到只用了1.957MB，分配4MB应该足够使用了。因为也没什么人访问，CPU设0.1也够了。

利用上次作业的pymesos建立framework发送docker命令。

```
#用之前查看的ubuntu—updated的数据
TASK_CPU = 0.1
TASK_MEM = 4
#利用pymesos的example作为模板：
class MinimalScheduler(Scheduler):

    #初始化
	def __init__(self):
		self.running = False

    #获得资源时：
	def resourceOffers(self, driver, offers):
		filters = {'refuse_seconds': 5}

		for offer in offers:
			if self.running:
				break;
			cpus = self.getResource(offer.resources, 'cpus')
			mem = self.getResource(offer.resources, 'mem')
			if cpus < TASK_CPU or mem < TASK_MEM:
				continue

			self.running = True;

            #设置Docker
			DockerInfo = Dict()
			DockerInfo.image = 'ubuntu-updated'
			DockerInfo.network = 'HOST'

            #设置Container
			ContainerInfo = Dict()
			ContainerInfo.type = 'DOCKER'
			ContainerInfo.docker = DockerInfo
			
			#设置CMD
			CommandInfo = Dict()
			CommandInfo.shell = False
			#执行的命令是'nginx'
			CommandInfo.value = 'nginx'
			#参数是'-g' 'daemon off'
			CommandInfo.arguments = ['-g', 'daemon off;']
			
			task = Dict()
			task_id = str(uuid.uuid4())
			task.task_id.value = task_id
			task.agent_id.value = offer.agent_id.value
			task.name = 'Nginx'
			
			task.container = ContainerInfo
			task.command = CommandInfo
			
			task.resources = [
				dict(name='cpus', type='SCALAR', scalar={'value': TASK_CPU}),
				dict(name='mem', type='SCALAR', scalar={'value': TASK_MEM}),
			]

            #启动任务
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

    #初始化framework
	framework = Dict()
	framework.user = getpass.getuser()
	framework.name = "Nginx"
	framework.hostname = socket.gethostname()

	driver = MesosSchedulerDriver(
		MinimalScheduler(),
		framework,
		master,
		use_addict=True,
	)

    #创建framework进程
	def signal_handler(signal, frame):
		driver.stop()

	def run_driver_thread():
		driver.run()

	driver_thread = Thread(target=run_driver_thread, args=())
	driver_thread.start()

	print('Scheduler running, Ctrl+C to quit.')
	signal.signal(signal.SIGINT, signal_handler)

    #创建Ctrl-C才会结束
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
不知道为什么网络使用BRIDGE并填写port_mappings字段，slave会启动失败。错误信息竟然是docker inspect找不到镜像，镜像名是"mesos-..."，与原本填写的镜像名完全不同，令人匪夷所思。
不填写port_mappings字段就可以成功启动。
最后还是网络使用了HOST。

找了很久的HTTP API，想知道JSON的格式，最后找到marathon去了。https://mesosphere.github.io/marathon/docs/ports.html

### Mesos
Mesos地址：http://162.105.174.32:5050/
![mesos](https://github.com/bacTlink/OS-practice/raw/master/hw3/mesos.png)

### Nginx
Nginx地址：http://162.105.174.32/
![nginx](https://github.com/bacTlink/OS-practice/raw/master/hw3/nginx.png)
