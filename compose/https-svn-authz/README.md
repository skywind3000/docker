## 简单介绍

SVN 服务搭建起来简单，但想做好就很麻烦。曾花过数周的时间搭建了一套相对完善的 svn 服务，编写了各种管理脚本，为避免重复搭建，把之前的经验固化到本 docker 镜像中。

从而提供一个完善的，方便管理的，一键启动的 svn 服务：


- 基于最新的 `Debian9` + `Apache2.4` + `davsvn`。
- 告别原始的 `svn://` 协议，使用 https 进行 svn 访问，保证数据安全。
- 用户可以按需自行更换默认的 pem/key 证书。
- 同时支持多个仓库，每个仓库提供独立的权限配置。
- 自动备份（svn dump）打包到指定文件夹：每周日 2:30 全量备份，其他天 2:30 增量备份。
- 备份文件使用 7zip 极限压缩，并用密码加密，可以随意传播，没有密码解不开。
- 备份自动保留一个月，多余一个月的备份会被自动移除。
- 用户信息管理页面：创建用户，修改密码，用户密码复位（需管理员）。
- 轻松管理，不同仓库的权限可以分配给不同的用户来管理，不需要每次都让 admin 来处理所有权限变更。
- 新用户加入，可以通过后台页面注册用户名，也不需要 admin 插手。
- 自动整合各个仓库的权限配置：`/authz/access.ini`，合并成最终的多仓库配置给 davsvn 服务。
- 每次权限配置更改都会保留历史。

## 镜像地址

使用下面命令下载或更新镜像：

```bash
git pull skywind3000/apache2-svn:authz
```

感兴趣还可以继续查看 [Dockerfile](/apache2-svn/authz).

## 启动服务

按需修改本目录内的 docker-compose.yml 文件，比如：

```yaml
svn-auth:
    image: skywind3000/apache2-svn:authz
    restart: always
    environment:
        SVN_BACKUP: "backup-password"
        SVN_AUTOAUTH: "5"
    ports:
        - "443:443"
        - "442:442"
    volumes:
        - ./data:/var/lib/svn
        - ./backup:/var/lib/backup
    
```

然后执行：

```bash
docker-compose up -d
```

即可启动服务，各项配置含义如下：

#### 端口映射：

- 端口 443：提供 svn 服务，地址为 https://localhost/仓库名/路径
- 端口 442：账户管理页面，地址为 https://localhost:442/reg

#### 卷访问：

- /var/lib/svn：svn的仓库和配置
- /var/lib/backup：数据备份目录

#### 环境变量：

- SVN_BACKUP：非空字符串打开自动备份，字符串的内容就是仓库备份打包时的密码。
- SVN_AUTOAUTH: 自动整合 davsvn.authz 的时间间隔，空的话将禁用 davsvn.authz 的自动生成。

#### 用户权限：

镜像内的 apache2 使用 Debian / Ubuntu 默认的 `www-data` 用户（uid=33）及 `www-data` 组（gid=33），如果外部宿主机需要通过 Volume 访问数据的话，需要手工创建 uid=33 的 `www-data` 用户，以及 gid=33 的 `www-data` 用户组。

## 用户注册

容器内的 `/var/lib/svn/conf/davsvn.passwd` 文件是一个 htpasswd 工具生成的账号密码数据库，我们的 davsvn 服务会用它来验证账号密码，该文件可以用 htpasswd 来创建账号或者修改密码，但是我们提供了页面来作这个事情：

- https://localhost:442/reg： 用户注册页面
- https://localhost:442/change： 密码修改页面
- https://localhost:442/reset： 密码复位页面，需要提供 admin 用户的密码

服务架设好以后，请首先使用第一个页面注册名为 `admin` 的用户，该用户有权限复位其他账号，以及访问所有仓库的 `/authz` 文件夹。

## 创建仓库

然后进入容器，创建仓库：

```bash
docker-compose exec svn-auth /bin/bash
/usr/local/bin/svn-create.sh test1
exit
```

该脚本创建了一个位于 `/var/lib/svn/repos` 下，名为 `test1` 的仓库，并将所有者设为 `www-data`，再为该仓库自动提交了一个默认的 `/authz/access.ini` 的权限配置文件。

该脚本做的事情相当于在容器内执行下面命令：

```bash
cd /var/lib/svn/repos
svnadmin create test1
mkdir -p /tmp/svntmp
svn checkout file:///var/lib/svn/repos/test1 /tmp/svntmp/test1
cd /tmp/svntmp/test1
mkdir authz
echo "[/]" > authz/access.ini
echo "* = r" >> authz/access.ini
svn add authz
svn commit -m "initialize authz/access.ini"
chown -R www-data:www-data /var/lib/svn/repos/test1
rm -rf /tmp/svntmp
```

你也可以在宿主机上通过 volume 映射，手工创建仓库，注意文件所有者是 `www-data`。



## 权限配置

容器内 `/var/lib/svn/conf/davsvn.authz` 是为 apache davsvn 服务提供的全局文件配置，该文件要把所有仓库的权限写到这个文件中，比如：

```ini
[repos1:/]
* = 
[repos1:/src]
user1 = rw
user2 = rw

[repos2:/]
* = 
[repos2:/src]
user3 = rw
user4 = rw

```

这样所有权限写到一个配置中是很难维护并且修改很危险的。因此本镜像使用分离权限管理，设置环境变量：

```
SVN_AUTOAUTH=5
```

将启用该功能，自动生成 `davsvn.authz` 文件，此时使用每个仓库根目录下的 `/authz/access.ini` 文件，独立配置该仓库的权限，比如仓库 repos1 的权限配置文件：

```ini
[/]
* = 
[/src]
user1 = rw
user2 = rw
```

这样镜像内的 crontab 服务会每隔五分钟扫描所有仓库的 `/authz/access.ini` 文件，有更改的话，就会整合生成最新的 `/var/lib/svn/conf/davsvn.authz` 文件，并且在 `/var/lib/svn/history` 下面保留一份备份。这样通过在各个仓库里提交最新的 access.ini ，等五分钟就会生效，权限配置错了回滚就行。

最终生成 `davsvn.authz` 时，`/var/lib/svn/conf` 下面可以放一个 `davsvn.inc` 文件，该文件的内容会被最终生成 `davsvn.authz` 的时附着到文件尾部，做一些权限覆盖。

通过在 access.ini 里赋予 admin 以外的用户对 `/authz` 文件夹的访问权限，可以让不同的人管理不同的仓库，不需要每次权限变更都由 admin 用户来处理。


## 证书更换

如果你不想用默认的证书，可以通过 volume 映射，替换容器内的两个文件：

```text
/etc/apache2/ssl/apache2-ssl.pem
/etc/apache2/ssl/apache2-ssl.key
```

使用 openssl 命令可以生成两个文件：

```bash
RANDFILE=/dev/random openssl req $@ -new -x509 -days 365 -nodes \
     -out /etc/apache2/ssl/svn.pem \
     -keyout /etc/apache2/ssl/svn.key
```

其中 `-days 365` 代表证书的有效时间为一年。


## 数据备份

目前所有备份都是备份到容器内的 `/var/lib/backup` 位置，想要备份到远程服务器的话，可在宿主机上把远端的 nfs 路径挂载到本地，再通过 volume 映射，将 nfs 路径映射到容器内的 `/var/lib/backup` 位置，这样可以自动备份到远端备份机器，宿主机挂了的话，备份机器还在。

更好的方式是 backup 卷还是映射到宿主机本地磁盘，而宿主机可以配置 crontab，定期将 backup 文件夹内的数据 rsync 到多个地址， backup 目录中的全量备份和增量备份只会保留一个月的，如果远程机器磁盘比较大的话，可以设置下 rsync 参数，让远程机保留所有备份。


## 轻松管理

平时使用基本不用终极管理员 admin 出马，每次新用户加入的话，先让他们去后台页面注册一个用户名，再由对应仓库的管理员为他配置上权限即可，全程不需要 admin 操心。

除非某人忘记密码了要复位才需要 admin 出面，或者对应仓库的管理员把 access.ini 写错了，失去了原有的 /authz 文件夹的权限的话，admin 用户可以去作些修复。

