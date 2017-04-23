# 第四次作业

标签：OS-prac

---

# 分布式文件系统

## 要求

调研两种以上的分布式文件系统以及一种联合文件系统，说明其工作原理和特点以及使用方式。

## HDFS

HDFS特点：

- 能快速检测错误、快速且自动恢复
- 适合流式访问数据的应用
- 适合大文件存储
- 适合一次写入多次读取的文件访问模型
- 适合在不同平台上移植
- 可靠，数据不易丢失

HDFS工作原理：

- HDFS采用master/slave架构。一个HDFS集群是由一个Namenode和一定数目的Datanodes组成。
- Namenode是一个中心服务器，负责管理文件系统的名字空间(namespace)以及客户端对文件的访问。
- 集群中的Datanode一般是一个节点一个，负责管理它所在节点上的存储。
- ![HDFS](https://hadoop.apache.org/docs/r1.0.4/cn/images/hdfsarchitecture.gif)
- Namenode全权管理数据块的复制，它周期性地从集群中的每个Datanode接收心跳信号和块状态报告(Blockreport)。接收到心跳信号意味着该Datanode节点工作正常。块状态报告包含了一个该Datanode上所有数据块的列表。
- Namenode和Datanode之间是通过TCP/IP协议交互的。

健壮性：
HDFS的文件都是一次性写入的，并且严格要求在任何时候只能有一个写入者。
HDFS会将每个文件存储成若干个数据块。
为了容错，每个文件都会有若干个副本。
通常副本个数是3，HDFS会把一个副本放在本地机架的节点上，一个副本放在同一机架的另一个节点上，最后一个放在不同机架的节点上。这样的策略在不损害数据可靠性的前提下，减少了机架间的数据传输，提高了写操作的效率。
在读操作的时候，HDFS会尽量选取最近的副本。

如果Datanode宕机，或者网络发生了割裂，Namenode会通过心跳信号来检测这一情况的发生，并将对应Datanode宕机，不会再将新的IO请求发给它们。任何存储在宕机Datanode上的数据将不再有效。
如果Namenode宕机，通常需要手动重启，还会丢失一些改动，但如果有Secondary Namenode，那么丢失的改动会少一些，相当于Namenode的助手。

### 使用方式：

1. 命令行接口
2. Java API
3. Web UI

### 命令行接口：
    Hadoop自带一组命令行工具，而其中有关HDFS的命令是其工具集的一个子集。
    执行hadoop dfs命令可以显示基本的使用信息。
```
$ hadoop dfs
Usage: java FsShell
         [-ls <path>]
         [-lsr <path>]
         [-df [<path>]]
         [-du <path>]
         [-dus <path>]
         [-count[-q] <path>]
         [-mv <src> <dst>]
         [-cp <src> <dst>]
         [-rm [-skipTrash] <path>]
         [-rmr [-skipTrash] <path>]
         [-expunge]
         [-put <localsrc> ... <dst>]
         [-copyFromLocal <localsrc> ... <dst>]
         [-moveFromLocal <localsrc> ... <dst>]
         [-get [-ignoreCrc] [-crc] <src> <localdst>]
         [-getmerge <src> <localdst> [addnl]]
         [-cat <src>]
         [-text <src>]
         [-copyToLocal [-ignoreCrc] [-crc] <src> <localdst>]
         [-moveToLocal [-crc] <src> <localdst>]
         [-mkdir <path>]
         [-setrep [-R] [-w] <rep> <path/file>]
         [-touchz <path>]
         [-test -[ezd] <path>]
         [-stat [format] <path>]
         [-tail [-f] <file>]
         [-chmod [-R] <MODE[,MODE]... | OCTALMODE> PATH...]
         [-chown [-R] [OWNER][:[GROUP]] PATH...]
         [-chgrp [-R] GROUP PATH...]
         [-help [cmd]]
```

### Java API
HDFS使用Java编写的的，所以通过Java API可以调用所有的HDFS的交互操作接口，最常用的是FileSystem类，它也是命令行hadoop fs的实现。
### Web UI
还可以通过NameNode的50070端口号访问HDFS的Web UI。

直接在浏览器中输入master:9000（即NameNode的主机名:端口号）便可进入Web UI。点击“Browse the filesystem”可以查看整个HDFS的目录树，点击“Namenode Logs”可以查看所有的NameNode的日志，这对于排查错误十分有帮助。

![HDFS2](http://write.epubit.com.cn/api/storage/getbykey/screenshow?key=15030c15ed30c3e8f852)

## GlusterFS
GlusterFS是大规模网络分布式文件系统，适合云存储和媒体流处理等数据密集型任务。

### 工作原理

外部架构图：
![GlusterFS](http://s5.51cto.com/wyfs02/M01/84/07/wKiom1eDiHjA-6YjAAW6vXeeVEE704.png)
它主要由存储服务器（BrickServer）、客户端以及NFS/Samba 存储网关组成。

内部架构图：
![GlusterFS](http://s1.51cto.com/wyfs02/M00/84/06/wKioL1eDiNayWoKEAAcdvSoqpMo543.png)
GlusterFS是模块化堆栈式的架构设计，如上图所示。模块称为Translator，是GlusterFS提供的一种强大机制，借助这种良好定义的接口可以高效简便地扩展文件系统的功能。

GlusterFS数据访问流程:
![GlusterFS](http://s1.51cto.com/wyfs02/M00/84/07/wKiom1eDiTDxNAtWAACeeKXHV3M342.png)

1. 在客户端，用户通过glusterfs的mount point 来读写数据。
2. 用户的这个操作被递交给本地linux系统的VFS来处理。
3. VFS将数据递交给FUSE内核文件系统，在启动glusterfs客户端以前，需要向系统注册一个实际的文件系统FUSE，如上图所示,该文件系统与ext3在同一个层次上面，ext3是对实际的磁片进行处理，而fuse文件系统则是将数据通过/dev/fuse这个设备文件递交给了glusterfs client端。所以，我们可以将fuse文件系统理解为一个代理。
4. 数据被fuse递交给Glusterfs client 后，client对数据进行一些指定的处理（所谓的指定，是按照client配置文件来进行的一系列处理）
5. 在glusterfsclient的处理末端，通过网路将数据递交给Glusterfs Server,并且将数据写入到服务器所控制的存储设备上

### 特点

- 完全软件实现（SoftwareOnly）
    GlusterFS是开放的全软件实现，完全独立于硬件和操作系统。
- 完整的存储操作系统栈（CompleteStorage Operating System Stack）
    GlusterFS不仅提供了一个分布式文件系统，而且还提供了许多其他重要的分布式功能，比如分布式内存管理、I/O调度、软RAID和自我修复等。GlusterFS汲取了微内核架构的经验教训，借鉴了GNU/Hurd操作系统的设计思想，在用户空间实现了完整的存储操作系统栈。
- 用户空间实现（User Space）
    与传统的文件系统不同，GlusterFS在用户空间实现，这使得其安装和升级特别简便。
- 模块化堆栈式架构（ModularStackable Architecture）
    GlusterFS采用模块化、堆栈式的架构，可通过灵活的配置支持高度定制化的应用环境。
- 原始数据格式存储（DataStored in Native Formats）
    GlusterFS无元数据服务设计（NoMetadata with the Elastic Hash Algorithm）以原始数据格式（如EXT3、EXT4、XFS、ZFS）储存数据，并实现多种数据自动修复机制。

### 使用方式：
在命令行敲入gluster+参数使用。

## AUFS
AUFS是一种Union File System，联合文件系统将多个目录合并成一个虚拟文件系统，成员目录称为虚拟文件系统的一个分支（branch）。
![aufs](http://dockerone.com/uploads/article/20170317/8718698f73fb3bc10c547312ee2af50f.jpg)
只有最顶上的层（branch）是rw权限，其它的都是ro+wh权限只读的。

### 工作原理和特点
- AUFS 是一种联合文件系统，它把若干目录按照顺序和权限 mount 为一个目录并呈现出来
- 默认情况下，只有第一层（第一个目录）是可写的，其余层是只读的。
- 增加文件：默认情况下，新增的文件都会被放在最上面的可写层中。
- 删除文件：因为底下各层都是只读的，当需要删除这些层中的文件时，AUFS 使用 whiteout（写隐藏） 机制，它的实现是通过在上层的可写的目录下建立对应的whiteout隐藏文件来实现的。
- 修改文件：AUFS 利用其 CoW （copy-on-write）特性来修改只读层中的文件。AUFS 工作在文件层面，因此，只要有对只读层中的文件做修改，不管修改数据的量的多少，在第一次修改时，文件都会被拷贝到可写层然后再被修改。
- 节省空间：AUFS 的 CoW 特性能够允许在多个容器之间共享分层，从而减少物理空间占用。
- 查找文件：AUFS 的查找性能在层数非常多时会出现下降，层数越多，查找性能越低，因此，在制作 Docker 镜像时要注意层数不要太多。
- 性能：AUFS 的 CoW 特性在写入大型文件时第一次会出现延迟。

### 使用方式
只需使用mount命令，指定文件系统为aufs，即可以实现挂载：```mount -t aufs -o br=(upper)=rw:(base)=ro+wh none (rootfs)```

---

# 搭建分布式文件系统

## 要求：
安装配置一种分布式文件系统，要求启动容错机制，即一台存储节点挂掉仍然能正常工作。在报告里阐述搭建过程和结果。

## 过程：
选了HDFS来搭建。
惯例先update一下，然后检查java版本
```
$ apt-get update
$ java -version
openjdk version "1.8.0_121"
OpenJDK Runtime Environment (build 1.8.0_121-8u121-b13-0ubuntu1.16.04.2-b13)
OpenJDK 64-Bit Server VM (build 25.121-b13, mixed mode)
```
添加用于hadoop的用户：
```
$ sudo addgroup hadoop_group
$ sudo adduser --ingroup hadoop_group hduser1
$ sudo adduser hduser1 sudo
```
登录进去hduser1，创建一个密码为空的ssh key：
```
$ su – hduser1
$ ssh-keygen -t rsa -P ""
$ cat $HOME/.ssh/id_rsa.pub >> $HOME/.ssh/authorized_keys
```
试试登录：
```
$ ssh localhost
```
下载解压hadoop：
```
$ wget http://www-eu.apache.org/dist/hadoop/common/hadoop-2.8.0/hadoop-2.8.0.tar.gz
$ sha256sum hadoop-2.8.0.tar.gz
3c0c6053651970c3ce283c100ee3e4e257c7f2dd7d7f92c98c8b0a3a440c04a0  hadoop-2.8.0.tar.gz
$ tar -xzf hadoop-2.8.0.tar.gz
$ mv hadoop-2.8.0 hadoop
```
配置环境变量：
```
$ vim ~/.bashrc
export HADOOP_HOME=/home/hduser1/hadoop
export PATH=$PATH:$HADOOP_HOME/bin
$ vim etc/hadoop/hadoop-env.sh
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64
$ sudo mkdir -p /app/hadoop/tmp
$ sudo chown hduser1:hadoop_group /app/hadoop/tmp
$ sudo chmod 750 /app/hadoop/tmp
$ vim etc/hadoop/core-site.xml
<property>
    <name>hadoop.tmp.dir</name>
    <value>/app/hadoop/tmp</value>
    <description>A base for other temporary directories.</description>
</property>

<property>
    <name>fs.default.name</name>
    <value>hdfs://172.16.6.103:54310</value>
    <description>The name of the default file system.</description>
</property>
$ vim etc/hadoop/mapred-site.xml
<configuration>
        <property>
            <name>mapred.job.tracker</name>
            <value>172.16.6.103:54311</value>
            <description>The host and port that the MapReduce job tracker runs at. </description>
        </property>
</configuration>
$ vim hdfs-site.xml
<configuration>
        <property>
            <name>dfs.replication</name>
            <value>2</value>
            <description>Default block replication.</description>
        </property>
        <property>
           <name>dfs.secondary.http.address</name>
           <value>172.16.6.225:50090</value>
           <description>SecondaryNameNodeHostname</description>
        </property>
</configuration>
$ vim masters
172.16.6.103
$ vim slaves
172.16.6.103
172.16.6.225
```
启动hdfs：
```
$ bin/hdfs namenode -format
$ sbin/start-dfs.sh
Starting namenodes on [mesos1400012775-1.cs14bcloud.internal]
mesos1400012775-1.cs14bcloud.internal: starting namenode, logging to /home/hduser1/hadoop/logs/hadoop-hduser1-namenode-oo-lab.out
172.16.6.225: starting datanode, logging to /home/hduser1/hadoop/logs/hadoop-hduser1-datanode-oo-lab.out
172.16.6.103: starting datanode, logging to /home/hduser1/hadoop/logs/hadoop-hduser1-datanode-oo-lab.out
Starting secondary namenodes [mesos1400012775-2.cs14bcloud.internal]
mesos1400012775-2.cs14bcloud.internal: starting secondarynamenode, logging to /home/hduser1/hadoop/logs/hadoop-hduser1-secondarynamenode-oo-lab.out
```
在NameNode上确认运行：
```
$ jps
29698 Jps
29490 DataNode
29330 NameNode
```
在另一台机子上确认运行：
```
$ jps
24272 SecondaryNameNode
24138 DataNode
24315 Jps
```
这边已经启用了HDFS的容错机制：SecondaryNameNode。

---

# 使用分布式文件系统存放主页

## 要求
在上次作业的基础上，将web服务器的主页提前写好在分布式文件系统里，在docker容器启动的时候将分布式文件系统挂载到容器里，并将该主页拷贝到正确的路径下，使得访问网站时显示这个主页。在报告中详细阐述过程和结果。

## 过程
先设置hdfs的挂载，利用hdfs提供的nfs系统接口。（[指南](https://hadoop.apache.org/docs/r2.4.1/hadoop-project-dist/hadoop-hdfs/HdfsNfsGateway.html)）
修改一些配置文件：
```
$ vim etc/hadoop/core-site.xml
<configuration>
        <property>
            <name>hadoop.tmp.dir</name>
            <value>/app/hadoop/tmp</value>
            <description>A base for other temporary directories.</description>
        </property>
        <property>
            <name>fs.default.name</name>
            <value>hdfs://172.16.6.103:54310</value>
            <description>The name of the default file system.  A URI whose
            scheme and authority determine the FileSystem implementation.  The
            uri's scheme determines the config property (fs.SCHEME.impl) naming
            the FileSystem implementation class.  The uri's authority is used to
            determine the host, port, etc. for a filesystem.</description>
        </property>
        <property>
            <name>hadoop.proxyuser.nfsserver.groups</name>
            <value>*</value>
            <description>proxy</description>
        </property>
        <property>
            <name>hadoop.proxyuser.nfsserver.hosts</name>
            <value>*</value>
            <description>permit hosts</description>
        </property>
  <property>
    <name>hadoop.proxyuser.root.groups</name>
    <value>*</value>
  </property>
  <property>
    <name>hadoop.proxyuser.root.hosts</name>
    <value>*</value>
  </property>
</configuration>
$vim etc/hadoop/hdfs-site.xml
<configuration>
        <property>
            <name>dfs.replication</name>
            <value>2</value>
            <description>Default block replication.
            The actual number of replications can be specified when the file is created.
            The default is used if replication is not specified in create time.
            </description>
        </property>
        <property>
           <name>dfs.secondary.http.address</name>
           <value>172.16.6.225:50090</value>
           <description>SecondaryNameNodeHostname</description>
        </property>
        <property>
            <name>nfs.dump.dir</name>
            <value>/tmp/.hdfs-nfs</value>
        </property>
        <property>
            <name>nfs.rtmax</name>
            <value>1048576</value>
            <description>This is the maximum size in bytes of a READ request supported by the NFS gateway. If you change this, make sure you also update the nfs mount's rsize(add rsize= # of bytes to the mount directive).</description>
        </property>
        <property>
            <name>nfs.wtmax</name>
            <value>65536</value>
            <description>This is the maximum size in bytes of a WRITE request supported by the NFS gateway. If you change this, make sure you also update the nfs mount's wsize(add wsize= # of bytes to the mount directive).</description>
        </property>
        <property>
            <name>nfs.exports.allowed.hosts</name>
            <value>* rw</value>
            <description>allow rw permission</description>
        </property>
</configuration>
```
在启动了HDFS的情况下，启动portmap和nfs3（需要root权限）。
```
$ sudo sbin/hadoop-daemon.sh start portmap
$ sudo sbin/hadoop-daemon.sh start nfs3
```
检查情况：
```
$ sudo showmount -e localhost
Export list for localhost:
/ *
$ sudo rpcinfo -p localhost
   program vers proto   port  service
    100005    3   udp   4242  mountd
    100005    1   tcp   4242  mountd
    100000    2   udp    111  portmapper
    100000    2   tcp    111  portmapper
    100005    3   tcp   4242  mountd
    100005    2   tcp   4242  mountd
    100003    3   tcp   2049  nfs
    100005    2   udp   4242  mountd
    100005    1   udp   4242  mountd
```
将主页放到HDFS上：
```
$ bin/hadoop fs -put index.nginx-debian.html /
```
挂载HDFS：
```
$ mount -t nfs -o vers=3,proto=tcp,nolock,noacl,sync localhost:/ /opt/hdfsnfs/
$ ls /opt/hdfsnfs/
index.nginx-debian.html
```
启动docker，并将挂载的HDFS目录挂载到docker里：
```
$ docker run -d -p 80:80 -v /opt/hdfsnfs:/var/www/html/ -i -t ubuntu-updated nginx -g "daemon off;"
```
也可以在docker里直接挂载NFS。
访问http://162.105.174.32/ 可以看到结果。
修改HDFS里面的网页，上面的网页也会随之改变。

---

# Docker镜像制作

## 要求
Docker中使用了联合文件系统来提供镜像服务，了解docker的镜像机制，并仿照其工作机制完成一次镜像的制作，具体要求为:创建一个docker容器，找到其文件系统位置，并将其保存，然后在该容器中安装几个软件包，找到容器的只读层（保存着这几个软件包），将其保存，之后通过aufs将这两个保存的文件系统挂载起来，使用docker import命令从其中创建镜像，并从该镜像中创建容器，要求此时可以使用之前安装好的软件包。在报告中详细阐述过程。

## Docker镜像

典型的Linux文件系统由bootfs和rootfs两部分组成，bootfs(boot file system)主要包含 bootloader和kernel，bootloader主要是引导加载kernel，当kernel被加载到内存中后 bootfs就被umount了。 rootfs (root file system) 包含的就是典型 Linux 系统中的/dev，/proc，/bin，/etc等标准目录和文件。

## 过程

创建一个用于测试的镜像并运行
```
$ docker create -it --name ubuntu-test ubuntu /bin/bash
a5e50b5761b0d35e35862c7790e4bc7733d6f63d21312f0e2e0ece2f61364a21
$ docker start -i ubuntu-test
```
找到挂载点
```
$ df -hT
Filesystem                   Type      Size  Used Avail Use% Mounted on
udev                         devtmpfs  473M     0  473M   0% /dev
tmpfs                        tmpfs      99M   12M   88M  12% /run
/dev/mapper/oo--lab--vg-root ext4       19G   12G  6.2G  65% /
tmpfs                        tmpfs     492M  436K  492M   1% /dev/shm
tmpfs                        tmpfs     5.0M     0  5.0M   0% /run/lock
tmpfs                        tmpfs     492M     0  492M   0% /sys/fs/cgroup
/dev/sda1                    ext2      472M   57M  391M  13% /boot
tmpfs                        tmpfs      99M     0   99M   0% /run/user/1000
tmpfs                        tmpfs      99M     0   99M   0% /run/user/1001
localhost:/                  nfs        37G   24G   13G  66% /opt/hdfsnfs
none                         aufs       19G   12G  6.2G  65% /var/lib/docker/aufs/mnt/1a031eb386187af6c96c15cf1c59aa3d236bc46ebfbc9b73bb2bcb3d7b2660d5
shm                          tmpfs      64M     0   64M   0% /var/lib/docker/containers/bff294b24480482a3811eb2181ed620c8af9d7734410e71e754ffa5390b76c7c/shm
none                         aufs       19G   12G  6.2G  65% /var/lib/docker/aufs/mnt/bfd89fe321b861b8f4ba42f405e0b873aa7079c15bf71977d6a08d31eab99a53
shm                          tmpfs      64M     0   64M   0% /var/lib/docker/containers/a5e50b5761b0d35e35862c7790e4bc7733d6f63d21312f0e2e0ece2f61364a21/shm
$ cat /var/lib/docker/aufs/layers/bfd89fe321b861b8f4ba42f405e0b873aa7079c15bf71977d6a08d31eab99a53
bfd89fe321b861b8f4ba42f405e0b873aa7079c15bf71977d6a08d31eab99a53-init
72fe9770e0b6cb6439f747e7f862f50bad4c458279db3b40326b05d3a523ea14
40128d5871433e6c93f375281e53a5c9a607b709186ee08f950bb279f1e19258
4c249566dd1750303cfb92b8cd6c7bd6e25a71a6a76e76fe3526647f78471e48
d163c32e3318baf7061f813df7854446e1bb01c2034ab65bd57e947a9668fbf6
287bb2e2888c203727cffb5b66bc59fb9e2437b13f44091250f3f7442200f62a
```
复制各层
```
$ mkdir img
$ cp -r /var/lib/docker/aufs/diff/287bb2e2888c203727cffb5b66bc59fb9e2437b13f44091250f3f7442200f62a/ img/layer0
$ cp -r /var/lib/docker/aufs/diff/d163c32e3318baf7061f813df7854446e1bb01c2034ab65bd57e947a9668fbf6/ img/layer1
$ cp -r /var/lib/docker/aufs/diff/4c249566dd1750303cfb92b8cd6c7bd6e25a71a6a76e76fe3526647f78471e48/ img/layer2
$ cp -r /var/lib/docker/aufs/diff/40128d5871433e6c93f375281e53a5c9a607b709186ee08f950bb279f1e19258/ img/layer3
$ cp -r /var/lib/docker/aufs/diff/72fe9770e0b6cb6439f747e7f862f50bad4c458279db3b40326b05d3a523ea14/ img/layer4
```
安装软件包
```
$ apt-get update
$ apt-get install vim
```
复制可读可写层
```
$cp -r /var/lib/docker/aufs/diff/bfd89fe321b861b8f4ba42f405e0b873aa7079c15bf71977d6a08d31eab99a53 img/rw
```
挂载
```
$ mount -t aufs -o br=img/rw=ro:img/layer4=ro:img/layer3=ro:img/layer2=ro:img/layer1=ro:img/layer0=ro none img/mnt/
```
创建镜像
```
$ tar -c img/mnt/ | docker import - ubuntu-test2
sha256:94cd007e29832935cba93b65a0ab53d3841059dfc789e7c68b2beb9098b41f92
```
运行
```
$ docker run -i -t ubuntu-test2 /bin/bash
```
可使用vim
