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
version: "2"
services:
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
            - /home/data/svn/data:/var/lib/svn
            - /home/data/svn/backup:/var/lib/backup
    
```

然后执行：

```bash
docker-compose up -d
```

具体各项说明请见 docker-compose 的 [页面说明](https://github.com/skywind3000/docker/tree/master/compose/https-svn-authz)。