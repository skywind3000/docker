## 简单介绍

SVN 服务启动起来简单，但是要有完善的权限管理就比较麻烦了，曾经花过两周的时间搭建了一套完善的 svn 服务，并编写了各种管理脚本，为了避免重复搭建，把之前的搭建经验股花到了 docker 镜像中。

从而提供一个完善的，方便管理的，一键启动的 svn 服务：


- 基于最新的 `Debian9` + `Apache2.4` + `davsvn`。
- 使用 https 进行 svn 访问，保证数据安全。
- 用户可以按需自行更换默认的 pem/key 证书。
- 同时支持多个仓库，每个仓库提供独立的权限配置。
- 自动备份（svn dump）打包到指定文件夹：每周日 2:30 全量备份，其他天 2:30 增量备份。
- 备份文件使用 7zip 极限压缩，并用密码加密，可以随意传播，没有密码解不开。
- 备份自动保留一个月，多余一个月的备份会被自动移除。
- 用户信息管理页面：创建用户，修改密码，用户密码复位（需管理员）。
- 轻松管理，不同仓库的权限可以分配给不同的用户来管理，不需要每次都让 admin 来处理所有权限。
- 新用户加入，可以通过后台页面注册用户名，也不需要 admin 插手。
- 自动整合各个仓库的权限配置：`/authz/access.ini`，合并成最终的多仓库配置给 davsvn 服务。
- 每次权限配置更改都会保留历史。

## 镜像地址

使用下面命令下载或更新镜像：

```bash
git pull skywind3000/apache2-svn:authz
```

## 启动服务

按需修改本目录内的 docker-compose.yml 文件，比如：

```yaml
version: "2"
services:
    svn-auth:
        image: skywind3000/apache2-svn:authz
        environment:
            - SVN_BACKUP="backup-password"
        ports:
            - "443:443"
            - "442:442"
        volumes:
            - /home/data/svn/data:/var/lib/svn
            - /home/data/svn/backup:/var/lib/backup
    
```

然后执行：

```bash
docker-compose up -d
```

即可启动服务，上面的各项配置代表什么呢？

#### 端口映射：

- 端口 443：提供 svn 服务，地址为 https://localhost/仓库名/路径
- 端口 442：提供账户管理页面，地址为 https://localhost:442/reg

#### 卷访问：

- /var/lib/svn：svn的仓库和配置
- /var/lib/backup：数据备份目录

#### 环境变量：

- SVN_BACKUP：非空字符串打开自动备份，字符串的内容就是仓库备份打包时的密码。

#### 用户权限：

镜像内的 apache2 使用 Debian / Ubuntu 默认的 `www-data` 用户（uid=33）及 `www-data` 组（gid=33），如果外部宿主机需要通过 Volume 访问数据的话，需要手工创建 uid=33 的 `www-data` 用户，以及 gid=33 的 `www-data` 用户组。


## 创建仓库

然后进入容器，创建仓库：

```bash
docker-compose exec svn-auth /bin/bash
/usr/local/bin/svn-create.sh test1
exit
```

这样就创建了一个位于 `/var/lib/svn/repos` 下面，名字是 `test1` 的仓库。

## 手工创建

不使用上面脚本的话，你也可以用 `svnadmin create` 手工创建：

```bash
docker-compose exec svn-auth /bin/bash
cd /var/lib/svn/repos
svnadmin create test1
```

然后为新仓库手工提交一个名为 `/authz/access.ini` 的文件：

```bash
mkdir -p /tmp/svntmp
svn checkout file:///var/lib/svn/repos/test1 /tmp/svntmp/test1
cd /tmp/svntmp/test1
mkdir authz
echo "[/]" > authz/access.ini
echo "* = r" >> authz/access.ini
svn add authz
svn commit -m "initialize authz/access.ini"

```

然后把仓库所有者设置成 www-data，并作些清理

```bash
chown -R www-data:www-data /var/lib/svn/repos/test1
rm -rf /tmp/svntmp
```

上面那个脚本就是作这些事情的。


## 用户注册

容器内的 `/var/lib/svn/conf/davsvn.passwd` 文件是一个 htpasswd 工具生成的账号密码数据库，我们的 davsvn 服务会用它来验证账号密码，该文件可以用 htpasswd 来创建账号或者修改密码，但是我们提供了页面来作这个事情：

- https://localhost:442/reg： 用户注册页面
- https://localhost:442/change： 密码修改页面
- https://localhost:442/reset： 密码复位页面，需要提供 admin 用户的密码

服务架设好以后，请首先使用第一个页面注册名为 `admin` 的用户，该用户有权限复位其他账号，以及访问所有仓库的 `/authz` 文件夹。

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

这样所有权限写到一个配置中是很难维护并且修改很危险的。因此本镜像使用分离权限管理，每个仓库根目录下放一个 `/authz/access.ini` 文件，独立配置该仓库的权限，比如仓库 repos1 的权限配置文件：

```ini
[/]
* = 
[/src]
user1 = rw
user2 = rw
```

这样镜像内的 crontab 服务会每隔五分钟扫描所有仓库的 `/authz/access.ini` 文件，有更改的话，就会整合生成最新的 `/var/lib/svn/conf/davsvn.authz` 文件，并且在 `/var/lib/svn/history` 下面保留一份备份。这样通过在各个仓库里提交最新的 access.ini ，等五分钟就会生效，权限配置错了回滚就行。

通过在 access.ini 里赋予 admin 以外的用户对 `/authz` 文件夹的访问权限，可以让不同的人管理不同的仓库，不需要每次权限变更都由 admin 用户来处理。

## 轻松管理

平时使用基本不用终极管理员 admin 出马，每次新用户加入的话，先让他们去后台页面注册一个用户名，再由对应仓库的管理员为他配置上权限即可，全程不需要 admin 操心。

除非某人忘记密码了要复位才需要 admin 出面，或者对应仓库的管理员把 access.ini 写错了，失去了原有的 /authz 文件夹的权限的话，admin 用户可以去作些修复。

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